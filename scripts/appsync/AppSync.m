// SPDX-License-Identifier: GPL-3.0-or-later
// UniXNU adaptation of AppSync's installation and FrontBoard strategy.
// See README.md for the upstream attribution and the 24A446 ABI contract.
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import "Signing.h"

#ifdef AS_HOST_TEST
#define AS_VERIFIER "ASFixtureVerifier"
#define AS_TRUST "ASFixtureSignatureService"
#else
#define AS_VERIFIER "MICodeSigningVerifier"
#define AS_TRUST "FBSSignatureValidationService"
#endif

@interface NSObject (UniXNUAppSyncPrivate)
- (NSURL *)bundleURL;
- (id)bundle;
- (BOOL)allowAdhocSigning;
- (BOOL)verifyTrustCachePresence;
- (BOOL)performOnlineAuthorization;
- (BOOL)skipProfileIDValidation;
- (void)setAllowAdhocSigning:(BOOL)value;
- (void)setVerifyTrustCachePresence:(BOOL)value;
- (void)setPerformOnlineAuthorization:(BOOL)value;
- (void)setSkipProfileIDValidation:(BOOL)value;
@end

static BOOL (*originalValidation)(id, SEL, NSError **);
static NSUInteger (*originalTrust)(id, SEL, id);

// Installation staging, installed apps and their nested bundles live on Data.
// Classify their location, never their identifier, version or executable hash.
static BOOL userBundle(NSURL *url) {
    if (![url isKindOfClass:[NSURL class]] || !url.isFileURL) return NO;
    NSString *path = url.URLByResolvingSymlinksInPath.URLByStandardizingPath.path;
    if (![path hasPrefix:@"/private/var/"] && ![path hasPrefix:@"/var/"]) return NO;
    for (NSString *component in path.pathComponents)
        if ([component hasSuffix:@".app"] && component.length > 4) return YES;
    return NO;
}

static BOOL validate(id self, SEL command, NSError **error) {
    id bundle = [self bundle];
    if (![bundle respondsToSelector:@selector(bundleURL)] || !userBundle([bundle bundleURL]))
        return originalValidation(self, command, error);
    // Validate ad-hoc user packages without a preloaded hash or provisioning
    // profile ID. The kernel trusts their validated CodeDirectories on demand.
    BOOL adhoc = [self allowAdhocSigning], trust = [self verifyTrustCachePresence];
    BOOL online = [self performOnlineAuthorization], profile = [self skipProfileIDValidation];
    [self setAllowAdhocSigning:YES];
    [self setVerifyTrustCachePresence:NO];
    [self setPerformOnlineAuthorization:NO];
    [self setSkipProfileIDValidation:YES];
    @try {
        return ASValidateUserBundle([bundle bundleURL], ^BOOL(NSError **nativeError) {
            return originalValidation(self, command, nativeError);
        }, error);
    } @finally {
        [self setAllowAdhocSigning:adhoc];
        [self setVerifyTrustCachePresence:trust];
        [self setPerformOnlineAuthorization:online];
        [self setSkipProfileIDValidation:profile];
    }
}

static NSUInteger trustState(id self, SEL command, id application) {
    NSUInteger state = originalTrust(self, command, application);
    // AppSync's iOS 14+ trusted value, also used by the 24A446 service.
    if (state == 8 || ![application respondsToSelector:@selector(bundleURL)]) return state;
    return userBundle([application bundleURL]) ? 8 : state;
}

static BOOL signature(Method method, const char *result, unsigned count, const char **args) {
    if (!method || method_getNumberOfArguments(method) != count + 2) return NO;
    char type[64];
    method_getReturnType(method, type, sizeof(type));
    if (strcmp(type, result)) return NO;
    for (unsigned i = 0; i < count; ++i) {
        method_getArgumentType(method, i + 2, type, sizeof(type));
        // NSError ** may carry the out qualifier in a private ABI.
        const char *plain = type;
        while (*plain && strchr("rnNoORV", *plain)) ++plain;
        if (strcmp(plain, args[i])) return NO;
    }
    return YES;
}

__attribute__((constructor)) static void start(void) {
    @autoreleasepool {
        NSString *process = NSProcessInfo.processInfo.processName;
        if ([process isEqual:@"installd"] || [process isEqual:@"com.apple.MobileInstallationHelperService"]) {
#ifndef AS_HOST_TEST
            dlopen("/System/Library/PrivateFrameworks/InstalledContentLibrary.framework/InstalledContentLibrary", RTLD_NOW);
#endif
            Class cls = objc_getClass(AS_VERIFIER);
            SEL selector = @selector(performValidationWithError:);
            Method method = class_getInstanceMethod(cls, selector);
            const char *arguments[] = {"^@"};
            const char *getters[] = {"allowAdhocSigning", "verifyTrustCachePresence", "performOnlineAuthorization", "skipProfileIDValidation"};
            const char *setters[] = {"setAllowAdhocSigning:", "setVerifyTrustCachePresence:", "setPerformOnlineAuthorization:", "setSkipProfileIDValidation:"};
            BOOL valid = signature(method, "B", 1, arguments) &&
                signature(class_getInstanceMethod(cls, @selector(bundle)), "@", 0, NULL);
            const char *boolean[] = {"B"};
            for (unsigned i = 0; i < 4; ++i)
                valid &= signature(class_getInstanceMethod(cls, sel_registerName(getters[i])), "B", 0, NULL) &&
                    signature(class_getInstanceMethod(cls, sel_registerName(setters[i])), "v", 1, boolean);
            if (!valid) { NSLog(@"[UniXNU AppSync] installation ABI mismatch; inactive"); return; }
            originalValidation = (void *)method_setImplementation(method, (IMP)validate);
            NSLog(@"[UniXNU AppSync] installation adapter active (all user bundles)");
        } else if ([process isEqual:@"SpringBoard"]) {
#ifndef AS_HOST_TEST
            dlopen("/System/Library/PrivateFrameworks/FrontBoardServices.framework/FrontBoardServices", RTLD_NOW);
#endif
            Method method = class_getInstanceMethod(objc_getClass(AS_TRUST),
                @selector(trustStateForApplication:));
            const char *arguments[] = {"@"};
            if (!signature(method, "Q", 1, arguments)) {
                NSLog(@"[UniXNU AppSync] FrontBoard ABI mismatch; inactive"); return;
            }
            originalTrust = (void *)method_setImplementation(method, (IMP)trustState);
            NSLog(@"[UniXNU AppSync] FrontBoard adapter active (all user bundles)");
        }
    }
}
