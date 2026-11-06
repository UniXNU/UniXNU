// Exercise the production repair and locking code with the real source-built signer.
#import "Signing.h"
#import <assert.h>
#import <spawn.h>
#import <sys/wait.h>
#import <errno.h>

int main(int argc, const char **argv) {
    @autoreleasepool {
        assert(argc == 3);
        NSURL *bundle = [NSURL fileURLWithPath:@(argv[1])];
        NSString *mode = @(argv[2]);
        __block unsigned calls = 0;
        NSError *error = nil;
        BOOL accepted = ASValidateUserBundle(bundle, ^BOOL(NSError **nativeError) {
            ++calls;
            // The host cannot execute the iOS certificate/provisioning verifier.
            // Model its first rejection for non-Apple and expired identities,
            // then independently verify the repaired on-disk signature.
            if (calls == 1 && ![mode isEqual:@"valid"]) {
                if (nativeError) *nativeError = [NSError errorWithDomain:@"native-fixture" code:13 userInfo:nil];
                return NO;
            }
            char *args[] = {"/usr/bin/codesign", "--verify", "--deep", "--strict", (char *)bundle.fileSystemRepresentation, NULL};
            char *env[] = {"PATH=/usr/bin:/bin", NULL};
            pid_t child;
            int status;
            if (posix_spawn(&child, args[0], NULL, NULL, args, env)) return NO;
            while (waitpid(child, &status, 0) < 0 && errno == EINTR) {}
            return WIFEXITED(status) && WEXITSTATUS(status) == 0;
        }, &error);
        if ([mode isEqual:@"reject"]) { assert(!accepted && error && calls == 1); }
        else { assert(accepted && error == nil); assert(calls == ([mode isEqual:@"valid"] ? 1 : 2)); }
    }
    return 0;
}
