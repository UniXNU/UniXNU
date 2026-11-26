// SPDX-License-Identifier: GPL-3.0-or-later
// CoreBrightness on iPadOS 27 selects VMBLControl when MobileGestalt reports IsVirtualDevice, and that control drops every brightness
// request. The board reports a virtual platform for AMFI (ADT vmm-present) and many other frameworks read the same answer, so it stays
// true. Only backboardd's choice changes: initBLControl: gets the mode a physical device gets (1 instead of 3).
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <dlfcn.h>
#import <math.h>
#import <stdlib.h>
#import <string.h>
#if TARGET_OS_OSX
#import <IOKit/IOKitLib.h>
#endif

static BOOL (*originalInit)(id, SEL, long long);

static BOOL initBLControl(id self, SEL command, long long mode) {
    return originalInit(self, command, mode == 3 ? 1 : mode);
}

#if TARGET_OS_OSX
static void (*originalSetNitsSDR)(id, SEL, float);
static void (*originalUpdateSDRNits)(id, SEL, float);
static void (*originalSendState)(id, SEL, unsigned long long);

static void pushNitsToBacklight(float nits) {
    if (!isfinite(nits) || nits < 0.0f) return;
    static io_service_t service = 0;
    static int32_t lastFixed = -1;
    int32_t fixed = (int32_t)(nits * 65536.0f + 0.5f);
    if (fixed == lastFixed) return;
    if (!service) {
        service = IOServiceGetMatchingService(0, IOServiceMatching("AppleARMBacklight"));
        if (!service) return;
    }
    CFNumberRef num = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &fixed);
    if (!num) return;
    CFStringRef key = CFSTR("brightness-nits");
    CFDictionaryRef dict = CFDictionaryCreate(kCFAllocatorDefault, (const void **)&key, (const void **)&num, 1,
                                              &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
    if (dict) {
        kern_return_t kr = IORegistryEntrySetCFProperties(service, dict);
        if (kr == KERN_SUCCESS) lastFixed = fixed;
        CFRelease(dict);
    }
    CFRelease(num);
}

static void hookedSetNitsSDR(id self, SEL cmd, float nits) {
    originalSetNitsSDR(self, cmd, nits);
    pushNitsToBacklight(nits);
}

static void hookedUpdateSDRNits(id self, SEL cmd, float nits) {
    originalUpdateSDRNits(self, cmd, nits);
    pushNitsToBacklight(nits);
}

static void hookedSendState(id self, SEL cmd, unsigned long long reason) {
    originalSendState(self, cmd, reason);
    SEL nitsSel = sel_registerName("nitsSDR");
    if ([self respondsToSelector:nitsSel]) {
        float nits = ((float (*)(id, SEL))objc_msgSend)(self, nitsSel);
        pushNitsToBacklight(nits);
    }
}
#endif

__attribute__((constructor)) static void start(void) {
    const char *prog = getprogname();
    if (strcmp(prog, "backboardd") && strcmp(prog, "corebrightnessd")) return;
    @autoreleasepool {
        dlopen("/System/Library/PrivateFrameworks/CoreBrightness.framework/CoreBrightness", RTLD_NOW);
        Method method = class_getInstanceMethod(objc_getClass("BrightnessSystemInternal"), sel_registerName("initBLControl:"));
        char type[16] = "";
        if (method) method_getArgumentType(method, 2, type, sizeof(type));
        if (!method || method_getNumberOfArguments(method) != 3 || !strchr("qQlL", type[0]) || !type[0]) {
            NSLog(@"[UniXNU backlight] initBLControl: ABI mismatch; inactive");
            return;
        }
        originalInit = (void *)method_setImplementation(method, (IMP)initBLControl);
#if TARGET_OS_OSX
        if (!strcmp(prog, "corebrightnessd")) {
            Class skl = objc_getClass("CBDisplayModuleSKL");
            if (skl) {
                Method m1 = class_getInstanceMethod(skl, sel_registerName("setNitsSDR:"));
                if (m1) originalSetNitsSDR = (void *)method_setImplementation(m1, (IMP)hookedSetNitsSDR);
                Method m2 = class_getInstanceMethod(skl, sel_registerName("updateSDRNits:"));
                if (m2) originalUpdateSDRNits = (void *)method_setImplementation(m2, (IMP)hookedUpdateSDRNits);
                Method m3 = class_getInstanceMethod(skl, sel_registerName("sendDisplayBrightnessStateNotificationWithReason:"));
                if (m3) originalSendState = (void *)method_setImplementation(m3, (IMP)hookedSendState);
            }
        }
#endif
        NSLog(@"[UniXNU backlight] physical brightness control selected");
    }
}
