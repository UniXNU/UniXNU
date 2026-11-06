// SPDX-License-Identifier: GPL-3.0-or-later
// CoreBrightness on iPadOS 27 selects VMBLControl when MobileGestalt reports IsVirtualDevice, and that control drops every brightness
// request. The board reports a virtual platform for AMFI (ADT vmm-present) and many other frameworks read the same answer, so it stays
// true. Only backboardd's choice changes: initBLControl: gets the mode a physical device gets (1 instead of 3).
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <stdlib.h>
#import <string.h>

static BOOL (*originalInit)(id, SEL, long long);

static BOOL initBLControl(id self, SEL command, long long mode) {
    return originalInit(self, command, mode == 3 ? 1 : mode);
}

__attribute__((constructor)) static void start(void) {
    if (strcmp(getprogname(), "backboardd")) return;
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
        NSLog(@"[UniXNU backlight] physical brightness control selected");
    }
}
