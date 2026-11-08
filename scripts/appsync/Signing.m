// SPDX-License-Identifier: GPL-3.0-or-later
#import "Signing.h"
#import <mach-o/loader.h>
#import <mach-o/fat.h>
#import <sys/file.h>
#import <sys/stat.h>
#import <dlfcn.h>
#import <fcntl.h>
#import <pthread.h>
#import <unistd.h>
#import <errno.h>

// installd's sandbox denies process-fork, so the signer is a library that runs
// in the calling process (ldid-library.cpp) instead of a separate executable.
#ifndef AS_SIGNER_PATH
#define AS_SIGNER_PATH "/usr/lib/libunixnu-ldid.dylib"
#endif

typedef int (*ASSignBundle)(const char *path, char *message, size_t size);

static BOOL failure(NSError **error, NSString *reason) {
    if (error) *error = [NSError errorWithDomain:@"org.unixnu.appsync" code:1
        userInfo:@{NSLocalizedDescriptionKey: reason}];
    return NO;
}

static BOOL readAt(int fd, void *data, size_t size, uint64_t at, uint64_t end) {
    if (at > end || size > end - at || at > INT64_MAX) return NO;
    uint8_t *bytes = data;
    while (size) {
        ssize_t count = pread(fd, bytes, size, (off_t)at);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return NO;
        size -= (size_t)count; bytes += count; at += (uint64_t)count;
    }
    return YES;
}

// Inspect every slice before ldid writes anything. Encrypted payloads require
// their original account authorization; never clear cryptid or sign ciphertext.
static BOOL thinCode(int fd, uint64_t at, uint64_t end) {
    uint32_t header[7];
    if (!readAt(fd, header, sizeof(header), at, end) ||
        (header[0] != MH_MAGIC && header[0] != MH_MAGIC_64)) return NO;
    size_t head = header[0] == MH_MAGIC_64 ? 32 : 28;
    if (at > end || head > end - at || header[5] > end - at - head || header[4] > 16384) return NO;
    uint64_t cursor = at + head, limit = cursor + header[5];
    for (uint32_t i = 0; i < header[4]; ++i) {
        uint32_t command[2];
        if (!readAt(fd, command, sizeof(command), cursor, limit) || command[1] < 8 ||
            command[1] > limit - cursor) return NO;
        if (command[0] == LC_ENCRYPTION_INFO || command[0] == LC_ENCRYPTION_INFO_64) {
            uint32_t cryptid;
            if (command[1] < 20 || !readAt(fd, &cryptid, sizeof(cryptid), cursor + 16, limit) || cryptid) return NO;
        }
        cursor += command[1];
    }
    return cursor == limit;
}

static BOOL signableFile(NSURL *url) {
    int fd = open(url.fileSystemRepresentation, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) return NO;
    struct stat st;
    BOOL ok = fstat(fd, &st) == 0 && S_ISREG(st.st_mode) && st.st_size >= 0;
    uint32_t magic = 0;
    if (ok && st.st_size >= 4) ok = readAt(fd, &magic, 4, 0, (uint64_t)st.st_size);
    if (ok && (magic == MH_MAGIC || magic == MH_MAGIC_64)) {
        ok = thinCode(fd, 0, (uint64_t)st.st_size);
    } else if (ok && (magic == FAT_CIGAM || magic == FAT_CIGAM_64)) {
        uint32_t count = 0;
        ok = readAt(fd, &count, 4, 4, (uint64_t)st.st_size);
        count = CFSwapInt32BigToHost(count);
        ok = ok && count > 0 && count <= 32;
        size_t stride = magic == FAT_CIGAM_64 ? 32 : 20;
        for (uint32_t i = 0; ok && i < count; ++i) {
            uint8_t arch[32] = {0};
            ok = readAt(fd, arch, stride, 8 + (uint64_t)i * stride, (uint64_t)st.st_size);
            uint64_t offset = 0, size = 0;
            if (magic == FAT_CIGAM_64) {
                memcpy(&offset, arch + 8, 8); memcpy(&size, arch + 16, 8);
                offset = CFSwapInt64BigToHost(offset); size = CFSwapInt64BigToHost(size);
            } else {
                uint32_t o, s; memcpy(&o, arch + 8, 4); memcpy(&s, arch + 12, 4);
                offset = CFSwapInt32BigToHost(o); size = CFSwapInt32BigToHost(s);
            }
            ok = ok && offset <= (uint64_t)st.st_size && size <= (uint64_t)st.st_size - offset &&
                thinCode(fd, offset, offset + size);
        }
    }
    close(fd);
    return ok;
}

static BOOL signableBundle(NSURL *root, NSError **error) {
    __block NSError *walkError = nil;
    NSArray *keys = @[NSURLIsSymbolicLinkKey, NSURLIsRegularFileKey, NSURLIsDirectoryKey];
    NSDirectoryEnumerator *walk = [NSFileManager.defaultManager enumeratorAtURL:root
        includingPropertiesForKeys:keys options:0 errorHandler:^BOOL(NSURL *url, NSError *problem) {
            (void)url; walkError = problem; return NO;
        }];
    if (!walk) return failure(error, @"Cannot inspect application bundle");
    NSString *prefix = [root.path stringByAppendingString:@"/"];
    for (NSURL *url in walk) {
        NSDictionary *values = [url resourceValuesForKeys:keys error:&walkError];
        if (!values) break;
        if ([values[NSURLIsSymbolicLinkKey] boolValue]) {
            if (![url.URLByResolvingSymlinksInPath.path hasPrefix:prefix])
                return failure(error, @"Application symlink leaves its bundle");
        } else if ([values[NSURLIsRegularFileKey] boolValue]) {
            if (!signableFile(url)) return failure(error, @"Malformed or encrypted application code");
        } else if (![values[NSURLIsDirectoryKey] boolValue]) {
            return failure(error, @"Unsupported application file type");
        }
    }
    if (walkError) { if (error) *error = walkError; return NO; }
    return YES;
}

static ASSignBundle loadSigner(NSString **problem) {
    static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
    static ASSignBundle sign;
    pthread_mutex_lock(&lock);
    if (!sign) {
        void *image = dlopen(AS_SIGNER_PATH, RTLD_NOW | RTLD_LOCAL);
        if (image) sign = (ASSignBundle)dlsym(image, "unixnu_ldid_sign_bundle");
        if (!sign) {
            const char *reason = dlerror();
            *problem = [NSString stringWithFormat:@"Cannot load application signer: %s",
                reason ?: "unixnu_ldid_sign_bundle missing"];
        }
    }
    ASSignBundle result = sign;
    pthread_mutex_unlock(&lock);
    return result;
}

static BOOL repair(NSURL *root, NSError **error) {
    if (!signableBundle(root, error)) return NO;
    // A repaired ad-hoc signature has no provisioning identity. Remove stale
    // profiles from the private install copy before rebuilding its resources.
    NSDirectoryEnumerator *files = [NSFileManager.defaultManager enumeratorAtURL:root
        includingPropertiesForKeys:nil options:0 errorHandler:nil];
    for (NSURL *file in files) {
        if ([file.lastPathComponent isEqual:@"embedded.mobileprovision"] ||
            [file.lastPathComponent isEqual:@"embedded.provisionprofile"])
            if (![NSFileManager.defaultManager removeItemAtURL:file error:error]) return NO;
    }
    NSString *problem = nil;
    ASSignBundle sign = loadSigner(&problem);
    if (!sign) {
        NSLog(@"[UniXNU AppSync] %@", problem);
        return failure(error, problem);
    }
    // The same command as before: ldid -Hsha256 -M -S BUNDLE.
    char message[512] = {0};
    int status = sign(root.fileSystemRepresentation, message, sizeof(message));
    if (status) {
        NSString *reason = [NSString stringWithFormat:@"Application signer failed (%d): %s", status, message];
        NSLog(@"[UniXNU AppSync] %@: %@", reason, root.path);
        return failure(error, reason);
    }
    NSLog(@"[UniXNU AppSync] repaired signature: %@", root.path);
    return YES;
}

BOOL ASValidateUserBundle(NSURL *url, BOOL (^validate)(NSError **), NSError **error) {
    NSURL *canonical = url.URLByResolvingSymlinksInPath.URLByStandardizingPath;
    NSArray<NSString *> *parts = canonical.pathComponents;
    NSURL *root = nil;
    for (NSUInteger i = 0; i < parts.count; ++i) {
        if ([parts[i] hasSuffix:@".app"] && parts[i].length > 4) {
            root = [NSURL fileURLWithPath:[NSString pathWithComponents:[parts subarrayWithRange:NSMakeRange(0, i + 1)]]];
            break;
        }
    }
    if (!root) return validate(error);
    int lock = open(root.fileSystemRepresentation, O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    if (lock < 0) return validate(error);
    if (flock(lock, LOCK_EX)) { close(lock); return validate(error); }
    BOOL valid = NO;
    @try {
        NSError *validationError = nil, *signingError = nil;
        valid = validate(&validationError);
        if (!valid && repair(root, &signingError)) {
            validationError = nil;
            valid = validate(&validationError);
        }
        if (error) *error = valid ? nil : (signingError ?: validationError);
    } @finally {
        flock(lock, LOCK_UN);
        close(lock);
    }
    return valid;
}
