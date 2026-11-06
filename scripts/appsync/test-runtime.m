// Execute the production Objective-C hooks against host ABI fixtures.
#import <Foundation/Foundation.h>
#import <dlfcn.h>
#import <assert.h>
#define MICodeSigningVerifier ASFixtureVerifier
#define FBSSignatureValidationService ASFixtureSignatureService

@interface ASBundle : NSObject
@property NSURL *bundleURL;
@end
@implementation ASBundle
@end

@interface MICodeSigningVerifier : NSObject
@property ASBundle *bundle;
@property BOOL allowAdhocSigning;
@property BOOL verifyTrustCachePresence;
@property BOOL performOnlineAuthorization;
@property BOOL trusted;
@property BOOL skipProfileIDValidation;
@property BOOL raiseException;
@property NSUInteger calls;
- (BOOL)performValidationWithError:(NSError **)error;
@end
@implementation MICodeSigningVerifier
- (BOOL)performValidationWithError:(NSError **)error {
    ++self.calls;
    if (self.raiseException) [NSException raise:@"fixture" format:@"validation interrupted"];
    BOOL accepted = self.trusted && self.allowAdhocSigning && !self.verifyTrustCachePresence && !self.performOnlineAuthorization && self.skipProfileIDValidation;
    if (!accepted && error) *error = [NSError errorWithDomain:@"fixture" code:17 userInfo:nil];
    return accepted;
}
@end

@interface FBSSignatureValidationService : NSObject
- (NSUInteger)trustStateForApplication:(id)application;
@end
@implementation FBSSignatureValidationService
- (NSUInteger)trustStateForApplication:(id)application { (void)application; return 4; }
@end

static MICodeSigningVerifier *activeVerifier;
static BOOL repairAllowed;
BOOL ASValidateUserBundle(NSURL *url, BOOL (^validate)(NSError **), NSError **error) {
    (void)url;
    if (validate(error)) return YES;
    if (!repairAllowed) return NO;
    activeVerifier.trusted = YES;
    BOOL result = validate(error);
    if (result && error) *error = nil;
    return result;
}

int main(int argc, const char **argv) {
    @autoreleasepool {
        assert(argc == 4);
        assert(dlopen(argv[1], RTLD_NOW | RTLD_LOCAL));
        ASBundle *bundle = [ASBundle new];
        bundle.bundleURL = [NSURL fileURLWithPath:@(argv[2])];
        BOOL expected = [@(argv[3]) isEqual:@"user"];
        if ([NSProcessInfo.processInfo.processName isEqual:@"SpringBoard"]) {
            FBSSignatureValidationService *service = [FBSSignatureValidationService new];
            assert([service trustStateForApplication:bundle] == (expected ? 8 : 4));
            assert([service trustStateForApplication:nil] == 4);
        } else {
            MICodeSigningVerifier *verifier = [MICodeSigningVerifier new];
            activeVerifier = verifier;
            verifier.bundle = bundle;
            verifier.trusted = YES;
            verifier.performOnlineAuthorization = YES;
            NSError *error = nil;
            assert([verifier performValidationWithError:&error] == expected);
            assert(verifier.calls == 1);
            assert(!verifier.allowAdhocSigning && !verifier.verifyTrustCachePresence && verifier.performOnlineAuthorization && !verifier.skipProfileIDValidation);
            verifier.trusted = NO;
            assert(![verifier performValidationWithError:&error]);
            assert(error.code == 17);
            assert(![verifier performValidationWithError:NULL]);
            repairAllowed = YES;
            assert([verifier performValidationWithError:&error] == expected);
            if (expected) assert(error == nil);
            assert(!verifier.allowAdhocSigning && !verifier.verifyTrustCachePresence && verifier.performOnlineAuthorization && !verifier.skipProfileIDValidation);
            verifier.raiseException = YES;
            BOOL caught = NO;
            @try { [verifier performValidationWithError:NULL]; }
            @catch (NSException *exception) { (void)exception; caught = YES; }
            assert(caught);
            assert(!verifier.allowAdhocSigning && !verifier.verifyTrustCachePresence && verifier.performOnlineAuthorization && !verifier.skipProfileIDValidation);
        }
    }
    return 0;
}
