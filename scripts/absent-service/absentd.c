// SPDX-License-Identifier: BSD-2-Clause-Patent
// The stand-in for a system daemon that cannot run on a board (the kernel's deny-exec list; macOS: mobileactivationd, which needs the
// Secure Enclave's device identity, and cryptexd, which needs grafted cryptex volumes). The kernel executes this program in the
// daemon's place, so it runs as that launchd job: it takes the job's Mach services and closes every connection made to them. A client
// then gets "connection invalid" at once, as it does from a daemon that is not there. Without a process behind the services launchd
// keeps each request queued for the next start of the job, and a client that waits for its reply never returns (macOS run41/run42:
// mdmclient in -[MobileActivationMacOS getUCRTDEPEnrollmentState:], so the login never finished).
#include <CoreFoundation/CoreFoundation.h>
#include <dispatch/dispatch.h>
#include <stdio.h>
#include <stdlib.h>
#include <xpc/xpc.h>

static void refuse(const char *name)
{
    xpc_connection_t listener = xpc_connection_create_mach_service(name, dispatch_get_main_queue(), XPC_CONNECTION_MACH_SERVICE_LISTENER);
    if (!listener) return;
    xpc_connection_set_event_handler(listener, ^(xpc_object_t peer) {
        if (xpc_get_type(peer) != XPC_TYPE_CONNECTION) return;
        xpc_connection_set_event_handler((xpc_connection_t)peer, ^(xpc_object_t event) { (void)event; });
        xpc_connection_activate((xpc_connection_t)peer);
        xpc_connection_cancel((xpc_connection_t)peer);
    });
    xpc_connection_activate(listener);
}

static void refuse_each(const void *key, const void *value, void *context)
{
    (void)value; (void)context;
    char name[256];
    if (CFGetTypeID(key) == CFStringGetTypeID() && CFStringGetCString(key, name, sizeof name, kCFStringEncodingUTF8)) refuse(name);
}

int main(void)
{
    // launchd gives every job its label; the job's own description names its services.
    const char *label = getenv("XPC_SERVICE_NAME");
    char path[512];
    if (!label || snprintf(path, sizeof path, "/System/Library/LaunchDaemons/%s.plist", label) >= (int)sizeof path) return 78;
    CFURLRef url = CFURLCreateFromFileSystemRepresentation(NULL, (const UInt8 *)path, (CFIndex)strlen(path), false);
    CFReadStreamRef stream = url ? CFReadStreamCreateWithFile(NULL, url) : NULL;
    CFPropertyListRef job = NULL;
    if (stream && CFReadStreamOpen(stream)) {
        job = CFPropertyListCreateWithStream(NULL, stream, 0, kCFPropertyListImmutable, NULL, NULL);
        CFReadStreamClose(stream);
    }
    if (stream) CFRelease(stream);
    if (url) CFRelease(url);
    if (job && CFGetTypeID(job) == CFDictionaryGetTypeID()) {
        CFTypeRef services = CFDictionaryGetValue(job, CFSTR("MachServices"));
        if (services && CFGetTypeID(services) == CFDictionaryGetTypeID()) CFDictionaryApplyFunction(services, refuse_each, NULL);
    }
    // Launch events (cryptexd is started by one) stay with launchd; this process keeps running, so they start nothing again.
    dispatch_main();
}
