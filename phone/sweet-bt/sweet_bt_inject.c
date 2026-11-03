/*
 * libsweet-bt.dylib (umi): what the kernel inserts into bluetoothd and BlueTool so iOS's Bluetooth stack talks to
 * the QCA6390 the kernel brought up (bsd/dev/sweet_bt.c, boot-arg sweetbt=6: the firmware runs, the H4 kernel control
 * "com.sweet.bluetooth" and the registry entry "bluetooth" are up). Inserted with boot-arg
 *   sweetinject=/usr/local/lib/libsweet-bt.dylib,bluetoothd,BlueTool
 * (kern.exec_inject adds DYLD_INSERT_LIBRARIES; the "AMFI" policy answers dyld's op 0x5a for those programs only).
 * Everything happens in the constructor, before the program's main() runs.
 *
 * bluetoothd -- the transport: BT_HCI_TRANSPORT=H4:POSIX:com.sweet.bluetooth,115200 (launchd will not take it from
 *   a job's plist) makes bluetoothd open the kernel's H4 endpoint; BT_BAUDRATE=115200 too. sweetbthci=STRING
 *   overrides the transport, sweetbthci=0 leaves the environment alone. It also fills the H4 transport's empty
 *   stack-stopped handler (in memory only; nothing on the root changes): without one, turning Bluetooth off
 *   crashes bluetoothd at pc 0.
 * BlueTool -- a stand-in: bluetoothd asks BlueTool (MachService com.apple.BlueTool) to RunBuiltinScript "boot" /
 *   "init" and waits for "result" 0. Apple's BlueTool only opens Apple's own transports, fails, and bluetoothd
 *   starts over. Here BlueTool's main() goes to our XPC responder instead: boot/init answer 0 once the controller
 *   is ready (registry "SweetBluetoothReady" and com.sweet.bluetooth resolves), deepsleep 0, anything else
 *   ENOTSUP. sweetbtool=0 lets Apple's BlueTool run.
 * sweetbtlog=1 mirrors bluetoothd's power-on os_log lines to stderr ("btd:" lines).
 * Output goes to stderr: the kernel log with the program's name in boot-arg sweetnull.
 *
 * Adapted from project-BadApple, github.com/aTechGeekDev/ios-apollo userland/bt-inject/sweet_bt_inject.c (its
 * forced-result stopgap left out). The offsets are bluetoothd's of iOS 16.7.16 (20H392), umi's build too; every
 * one is checked against what it should hold before anything is written.
 *
 * MIT License. Copyright (c) 2026 Leo Malik, Copyright (c) 2026 dipa-studio.
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 * to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
 * copyright notice and this permission notice shall be included in all copies or substantial portions of the
 * Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
 * SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */
#include <CoreFoundation/CoreFoundation.h>
#include <dispatch/dispatch.h>
#include <dlfcn.h>
#include <errno.h>
#include <libkern/OSCacheControl.h>
#include <mach/mach.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/sysctl.h>
#include <unistd.h>

extern const char *getprogname(void);
extern char ***_NSGetArgv(void);
extern int *_NSGetArgc(void);

/* The iOS SDK has no IOKit headers; the IOKitLib calls used are declared here (IOKit.framework is linked). */
typedef mach_port_t io_object_t;
typedef io_object_t io_service_t;
typedef io_object_t io_registry_entry_t;
extern CFMutableDictionaryRef IOServiceNameMatching(const char *name);
extern io_service_t IOServiceGetMatchingService(mach_port_t mainPort, CFDictionaryRef matching);
extern CFTypeRef IORegistryEntryCreateCFProperty(io_registry_entry_t entry, CFStringRef key, CFAllocatorRef allocator,
    uint32_t options);
extern kern_return_t IOObjectRelease(io_object_t object);

/* Nor XPC headers: the libxpc calls used (libSystem). */
typedef void *xpc_object_t;
typedef xpc_object_t xpc_connection_t;
extern const char _xpc_type_dictionary, _xpc_type_connection;
extern const void *xpc_get_type(xpc_object_t object);
extern xpc_connection_t xpc_connection_create_mach_service(const char *name, dispatch_queue_t queue, uint64_t flags);
extern void xpc_connection_set_event_handler(xpc_connection_t connection, void (^handler)(xpc_object_t object));
extern void xpc_connection_resume(xpc_connection_t connection);
extern void xpc_connection_send_message(xpc_connection_t connection, xpc_object_t message);
extern uid_t xpc_connection_get_euid(xpc_connection_t connection);
extern xpc_object_t xpc_dictionary_create_reply(xpc_object_t original);
extern xpc_object_t xpc_dictionary_get_value(xpc_object_t dictionary, const char *key);
extern const char *xpc_dictionary_get_string(xpc_object_t dictionary, const char *key);
extern void xpc_dictionary_set_int64(xpc_object_t dictionary, const char *key, int64_t value);
extern void xpc_release(xpc_object_t object);
#define SWEET_XPC_MACH_SERVICE_LISTENER 1u

/* Nor the kernel-control ABI (sys/kern_control.h): what CTLIOCGINFO takes. */
struct sweet_ctl_info {
	uint32_t ctl_id;
	char ctl_name[96];
};
#define SWEET_CTLIOCGINFO       _IOWR('N', 3, struct sweet_ctl_info)
#define SWEET_SYSPROTO_CONTROL  2
#ifndef AF_SYSTEM
#define AF_SYSTEM               32
#endif

#define BT_HCI_DEFAULT  "H4:POSIX:com.sweet.bluetooth,115200"

/*
 * bluetoothd's transports are tables of functions; the one BT_HCI_TRANSPORT names is kept at 0x100844850. H4's (20H392:
 * __DATA,__data at image offset 0x844228: id 1, name "H4", functions from +0x10) has nothing in slot +0x60, and
 * 0x1000e6aac calls that slot without a null check when the stack stops -- only Apple's own transports, whose handler
 * just notes that the stack stopped (APPLEBT: strb #1), were ever used on an iPhone. Turning Bluetooth off crashed
 * bluetoothd at pc 0 (apollo boot 76). Fill the slot with a handler that does nothing, if the table is the expected one.
 */
#define BTD_H4_TRANSPORT_OFFSET 0x844228u
#define BTD_H4_STOPPED_SLOT     0x60u

/*
 * Observability (boot-arg sweetbtlog=1): bluetoothd logs its power-on steps through os_log, which
 * sweetnull (stdout/stderr) never sees, so boots 68-70 were blind past the BlueTool gate. Redirect
 * the _os_log_impl GOT slot (20H392 image offset 0x7f5438; the stub at 0x10065fe2c is
 * `adrp x16,0x1007f5000; ldr x16,[x16,#0x438]; br x16`) to a thunk that mirrors each line to stderr
 * and then calls the real one. os_log passes the format string in register x3; for the common
 * "%{public}s" case (bluetoothd's printf-style debug helper formats into a string and logs that),
 * the string pointer sits in the encoded arg buffer, so pull it out too. A keyword filter keeps the
 * 4 MiB console ring from wrapping away the early power-on lines.
 */
#define BTD_OSLOG_GOT_OFFSET 0x7f5438u

typedef void (*os_log_impl_fn)(void *dso, void *log, unsigned int type,
    const char *format, uint8_t *buf, uint32_t size);
static os_log_impl_fn real_os_log_impl;

static void
say(const char *format, ...)
{
	char line[512];
	va_list ap;
	int n;

	va_start(ap, format);
	n = vsnprintf(line, sizeof(line), format, ap);
	va_end(ap);
	if (n > (int)sizeof(line) - 1) {
		n = (int)sizeof(line) - 1;
	}
	if (n > 0) {
		write(2, line, (size_t)n);
	}
}

/* the text after "NAME=" in the boot arguments, up to the next space, copied into out; or NULL */
static const char *
boot_arg(const char *arguments, const char *name, char *out, size_t size)
{
	size_t length = strlen(name);

	for (const char *at = arguments; (at = strstr(at, name)) != NULL; at += length) {
		if ((at == arguments || at[-1] == ' ') && at[length] == '=') {
			size_t value = strcspn(at + length + 1, " ");

			if (value == 0 || value >= size) {
				return NULL;
			}
			memcpy(out, at + length + 1, value);
			out[value] = 0;
			return out;
		}
	}
	return NULL;
}

/*
 * The running program's own Mach-O, not libsweet-bt.dylib's. dyld does NOT promise image 0 is the
 * main program once a library is inserted (boot 68: image 0 was our dylib), so find the one
 * MH_EXECUTE image; its header is at the slid load address, so offsets add directly.
 */
static const struct mach_header *
main_executable(void)
{
	uint32_t count = _dyld_image_count();

	for (uint32_t i = 0; i < count; i++) {
		const struct mach_header *h = _dyld_get_image_header(i);

		if (h != NULL && h->magic == MH_MAGIC_64 && h->filetype == MH_EXECUTE) {
			return h;
		}
	}
	return NULL;
}

/* Overwrite count instruction words at `at`: made writable (copied on write), then executable again. 0 or -1. */
static int
write_code(uint32_t *at, const uint32_t *words, unsigned count)
{
	uintptr_t ps = (uintptr_t)getpagesize();
	vm_address_t page = (vm_address_t)((uintptr_t)at & ~(ps - 1));
	vm_size_t span = (vm_size_t)((((uintptr_t)(at + count)) - page + ps - 1) & ~(ps - 1));
	kern_return_t kr;

	kr = vm_protect(mach_task_self(), page, span, FALSE, VM_PROT_READ | VM_PROT_WRITE | VM_PROT_COPY);
	if (kr != KERN_SUCCESS) {
		say("sweet-bt: vm_protect(rw) at %p failed (%d)\n", (void *)page, kr);
		return -1;
	}
	for (unsigned i = 0; i < count; i++) {
		at[i] = words[i];
	}
	(void)vm_protect(mach_task_self(), page, span, FALSE, VM_PROT_READ | VM_PROT_EXECUTE);
	sys_icache_invalidate(at, count * sizeof(*at));
	return 0;
}

/* Keep only power-on / transport / authorization lines, so the mirror does not flood the ring. */
static int
keep(const char *s)
{
	static const char *const words[] = {
		"transport", "Transport", "HCI", "ontroller", "power state", "PowerState",
		"Power state chang", "power init", "TCC", "uthoriz", "onnectab", "Searching",
		"H4", "ACIPC", "QCA", "eset", "endor", "socket", "Opening", "connect", "Connect",
		"fail", "Fail", "error", "Error", "radio", "Radio", "nable", "managerState",
		/* controller-init outcome (the async power-init gate) */
		"chip", "Chip", "latform", "anufacturer", "restart", "booting", "timed",
		"high power", "Turning", "modification", "Unknown", "result", "Init",
		/* the BlueTool exchange and the end of HCI initialization */
		"BlueTool", "script", "Stack", "initializ", NULL
	};

	for (int i = 0; words[i] != NULL; i++) {
		if (strstr(s, words[i]) != NULL) {
			return 1;
		}
	}
	return 0;
}

/* Append os_log's encoded arguments after the format, so %d/%x/%s values are visible. */
static void
decode_args(char *out, size_t outsz, const char *fmt, const uint8_t *buf, uint32_t size)
{
	int n = snprintf(out, outsz, "%s", fmt);
	size_t p = 2;

	if (buf == NULL || size < 2 || n < 0) {
		return;
	}
	for (uint8_t i = 0; i < buf[1] && p + 2 <= size && n < (int)outsz - 1; i++) {
		uint8_t desc = buf[p];
		uint8_t sz = buf[p + 1];

		p += 2;
		if ((size_t)sz > size - p) {
			break;
		}
		if ((desc & 0x0f) == 2 && sz == 8) {       /* %s: a pointer to a string */
			const char *s;

			memcpy(&s, buf + p, sizeof(s));
			if (s != NULL && (uintptr_t)s > 0x1000 && ((uintptr_t)s >> 47) == 0) {
				n += snprintf(out + n, outsz - (size_t)n, " |%s", s);
			}
		} else if (sz >= 1 && sz <= 8) {            /* a scalar (%d/%x/%lld/...) */
			unsigned long long v = 0;

			for (uint8_t b = 0; b < sz; b++) {
				v |= (unsigned long long)buf[p + b] << (8 * b);
			}
			n += snprintf(out + n, outsz - (size_t)n, " |%llu", v);
		}
		p += sz;
	}
}

/* Our stand-in for bluetoothd's _os_log_impl: mirror interesting lines to stderr, then call real. */
static void
sweet_oslog(void *dso, void *log, unsigned int type, const char *format, uint8_t *buf, uint32_t size)
{
	static char last[1024];
	char line[1024];

	if (format != NULL) {
		if (strcmp(format, "%{public}s") == 0 && buf != NULL && size >= 12 && buf[1] >= 1 && buf[3] == 8) {
			const char *s;

			memcpy(&s, buf + 4, sizeof(s));
			if (s != NULL && (uintptr_t)s > 0x1000 && ((uintptr_t)s >> 47) == 0) {
				snprintf(line, sizeof(line), "%s", s);
			} else {
				snprintf(line, sizeof(line), "%s", format);
			}
		} else {
			decode_args(line, sizeof(line), format, buf, size);
		}
		if (keep(line) && strcmp(line, last) != 0) {    /* skip the repeated power-state floods */
			say("btd: %s\n", line);
			strlcpy(last, line, sizeof(last));
		}
	}
	if (real_os_log_impl != NULL) {
		real_os_log_impl(dso, log, type, format, buf, size);
	}
}

/* Redirect bluetoothd's _os_log_impl GOT slot to sweet_oslog (see the header comment). */
static void
hook_os_log(const struct mach_header *base)
{
	void **slot;
	void *cur, *expected;
	vm_address_t page;
	vm_size_t span;
	kern_return_t kr;
	uintptr_t ps = (uintptr_t)getpagesize();

	if (base == NULL) {
		return;
	}
	slot = (void **)((uintptr_t)base + BTD_OSLOG_GOT_OFFSET);
	cur = *slot;
	if (cur == NULL) {
		say("sweet-bt: bluetoothd: os_log GOT slot empty; not hooking\n");
		return;
	}
	expected = dlsym(RTLD_DEFAULT, "_os_log_impl");
	if (expected == NULL) {
		expected = dlsym(RTLD_DEFAULT, "os_log_impl");
	}
	if (expected != NULL && cur != expected) {
		say("sweet-bt: bluetoothd: os_log GOT %p != _os_log_impl %p; not hooking\n", cur, expected);
		return;
	}
	real_os_log_impl = (os_log_impl_fn)cur;
	page = (vm_address_t)((uintptr_t)slot & ~(ps - 1));
	span = (vm_size_t)((((uintptr_t)slot + sizeof(*slot)) - page + ps - 1) & ~(ps - 1));
	kr = vm_protect(mach_task_self(), page, span, FALSE, VM_PROT_READ | VM_PROT_WRITE | VM_PROT_COPY);
	if (kr != KERN_SUCCESS) {
		say("sweet-bt: bluetoothd: vm_protect os_log slot at %p failed (%d); not hooking\n", (void *)page, kr);
		return;
	}
	*slot = (void *)&sweet_oslog;
	(void)vm_protect(mach_task_self(), page, span, FALSE, VM_PROT_READ);
	say("sweet-bt: bluetoothd: os_log hooked (real %p); power-on now mirrored to stderr (sweetbtlog=1)\n",
	    (void *)real_os_log_impl);
}

static void
h4_stack_stopped(void)
{
}

static void
fix_h4_transport(const struct mach_header *header)
{
	uintptr_t table = (uintptr_t)header + BTD_H4_TRANSPORT_OFFSET;
	const char *name;
	void **slot = (void **)(table + BTD_H4_STOPPED_SLOT);

	if (header == NULL) {
		return;
	}
	name = *(const char *const *)(table + 8);
	if (*(const uint32_t *)table != 1 || name == NULL || strcmp(name, "H4") != 0 || *slot != NULL) {
		say("sweet-bt: bluetoothd: no empty H4 transport table at %p (different build?); not filled\n", (void *)table);
		return;
	}
	*slot = (void *)h4_stack_stopped;
	say("sweet-bt: bluetoothd: H4 transport's stack-stopped handler filled; turning Bluetooth off no longer crashes\n");
}

/*
 * The controller is ready when the registry entry "bluetooth" says SweetBluetoothReady and the kernel control
 * com.sweet.bluetooth resolves (sweet_bt.c sets both once the firmware runs). 0, or an errno.
 */
static int
controller_ready(void)
{
	io_service_t service = IOServiceGetMatchingService(0, IOServiceNameMatching("bluetooth"));
	struct sweet_ctl_info info;
	CFTypeRef ready;
	bool running;
	int fd, error;

	if (service == 0) {
		return ENODEV;
	}
	ready = IORegistryEntryCreateCFProperty(service, CFSTR("SweetBluetoothReady"), kCFAllocatorDefault, 0);
	IOObjectRelease(service);
	running = ready == kCFBooleanTrue;
	if (ready != NULL) {
		CFRelease(ready);
	}
	if (!running) {
		return EIO;
	}
	fd = socket(AF_SYSTEM, SOCK_STREAM, SWEET_SYSPROTO_CONTROL);
	if (fd < 0) {
		return errno;
	}
	memset(&info, 0, sizeof(info));
	strlcpy(info.ctl_name, "com.sweet.bluetooth", sizeof(info.ctl_name));
	error = ioctl(fd, SWEET_CTLIOCGINFO, &info) < 0 ? errno : 0;
	close(fd);
	return error;
}

/* One request to com.apple.BlueTool: kMsgId, and for RunBuiltinScript kMsgArgs { script }; the reply's "result". */
static void
bluetool_request(xpc_connection_t peer, xpc_object_t message)
{
	xpc_object_t reply, arguments;
	const char *command, *script = NULL;
	int result = ENOTSUP;

	if (xpc_get_type(message) != &_xpc_type_dictionary) {
		return;
	}
	reply = xpc_dictionary_create_reply(message);
	if (reply == NULL) {
		return;
	}
	command = xpc_dictionary_get_string(message, "kMsgId");
	arguments = xpc_dictionary_get_value(message, "kMsgArgs");
	if (arguments != NULL && xpc_get_type(arguments) == &_xpc_type_dictionary) {
		script = xpc_dictionary_get_string(arguments, "script");
	}
	if (command != NULL && script != NULL && strcmp(command, "RunBuiltinScript") == 0) {
		if (strcmp(script, "boot") == 0 || strcmp(script, "init") == 0) {
			result = controller_ready();
		} else if (strcmp(script, "deepsleep") == 0) {
			result = 0;     /* see the header comment */
		}
	}
	say("sweet-bt: BlueTool (ours): %.48s %.48s -> result %d\n", command != NULL ? command : "(no kMsgId)",
	    script != NULL ? script : "-", result);
	xpc_dictionary_set_int64(reply, "result", result);
	xpc_connection_send_message(peer, reply);
	xpc_release(reply);
}

/* What runs instead of Apple's BlueTool main(): the com.apple.BlueTool service, answered by bluetool_request. */
static void __attribute__((noreturn))
bluetool_main(void)
{
	xpc_connection_t listener = xpc_connection_create_mach_service("com.apple.BlueTool", dispatch_get_main_queue(),
	    SWEET_XPC_MACH_SERVICE_LISTENER);

	if (listener == NULL) {
		say("sweet-bt: BlueTool (ours): cannot check in com.apple.BlueTool\n");
		exit(1);
	}
	xpc_connection_set_event_handler(listener, ^(xpc_object_t object) {
		xpc_connection_t peer = object;
		uid_t uid;

		if (xpc_get_type(object) != &_xpc_type_connection) {
			return;
		}
		uid = xpc_connection_get_euid(peer);
		if (uid != 0 && uid != 501) {           /* bluetoothd runs as mobile */
			return;
		}
		xpc_connection_set_event_handler(peer, ^(xpc_object_t message) {
			bluetool_request(peer, message);
		});
		xpc_connection_resume(peer);
	});
	xpc_connection_resume(listener);
	say("sweet-bt: BlueTool (ours): answering boot/init/deepsleep on com.apple.BlueTool; Apple's BlueTool does not run\n");
	dispatch_main();
}

/*
 * Have dyld's call of the program's main() land in `replacement` instead: main's first instructions become
 * `ldr x16, <literal>; br x16` with the replacement's address as the literal, 8-aligned (a nop first when main is
 * not). LC_MAIN names main, so this holds for any build. 0, or -1 with nothing changed.
 */
static int
take_over_main(void (*replacement)(void))
{
	const struct mach_header_64 *header = (const struct mach_header_64 *)main_executable();
	const uint8_t *command, *end;
	uint64_t entry = 0;
	uintptr_t main_address, target = (uintptr_t)replacement;
	uint32_t code[5];
	unsigned count = 0;

	if (header == NULL || header->magic != MH_MAGIC_64) {
		return -1;
	}
	command = (const uint8_t *)(header + 1);
	end = command + header->sizeofcmds;
	for (uint32_t i = 0; i < header->ncmds; i++) {
		const struct load_command *lc = (const struct load_command *)(const void *)command;

		if ((size_t)(end - command) < sizeof(*lc) || lc->cmdsize < sizeof(*lc) ||
		    lc->cmdsize > (size_t)(end - command)) {
			return -1;
		}
		if (lc->cmd == LC_MAIN && lc->cmdsize >= sizeof(struct entry_point_command)) {
			entry = ((const struct entry_point_command *)(const void *)command)->entryoff;
		}
		command += lc->cmdsize;
	}
	if (entry == 0 || (entry & 3) != 0) {
		return -1;
	}
	main_address = (uintptr_t)header + (uintptr_t)entry;
	if (main_address & 4) {
		code[count++] = 0xd503201fu;    /* nop */
	}
	code[count++] = 0x58000050u;            /* ldr x16, #8 */
	code[count++] = 0xd61f0200u;            /* br x16 */
	code[count++] = (uint32_t)target;
	code[count++] = (uint32_t)((uint64_t)target >> 32);
	if (write_code((uint32_t *)main_address, code, count) != 0) {
		return -1;
	}
	say("sweet-bt: BlueTool: main() at %p now goes to our responder\n", (void *)main_address);
	return 0;
}

__attribute__((constructor))
static void
sweet_bt_init(void)
{
	char arguments[1024] = "";
	char value[256];
	size_t size = sizeof(arguments) - 1;
	const char *name = getprogname();

	if (name == NULL) {
		return;
	}
	(void)sysctlbyname("kern.bootargs", arguments, &size, NULL, 0);

	if (strcmp(name, "bluetoothd") == 0) {
		const char *transport = BT_HCI_DEFAULT;
		int set_transport = 1;

		if (boot_arg(arguments, "sweetbthci", value, sizeof(value)) != NULL) {
			if (strcmp(value, "0") == 0) {
				set_transport = 0;
				say("sweet-bt: bluetoothd: sweetbthci=0: leaving BT_HCI_TRANSPORT as it is\n");
			} else {
				transport = value;
			}
		}
		if (set_transport) {
			setenv("BT_HCI_TRANSPORT", transport, 1);
			setenv("BT_BAUDRATE", "115200", 0);
			say("sweet-bt: bluetoothd: BT_HCI_TRANSPORT=%s BT_BAUDRATE=%s (the kernel's H4 endpoint; sweetbt=6)\n",
			    transport, getenv("BT_BAUDRATE"));
		}
		fix_h4_transport(main_executable());
		if (boot_arg(arguments, "sweetbtlog", value, sizeof(value)) != NULL && strcmp(value, "1") == 0) {
			hook_os_log(main_executable());
		}
	} else if (strcmp(name, "BlueTool") == 0) {
		char **argv = _NSGetArgv() != NULL ? *_NSGetArgv() : NULL;
		int argc = _NSGetArgc() != NULL ? *_NSGetArgc() : 0;

		for (int i = 0; argv != NULL && i < argc && argv[i] != NULL; i++) {
			say("sweet-bt: BlueTool argv[%d]=%s\n", i, argv[i]);
		}
		if (boot_arg(arguments, "sweetbtool", value, sizeof(value)) != NULL && strcmp(value, "0") == 0) {
			say("sweet-bt: BlueTool: sweetbtool=0: Apple's BlueTool runs\n");
		} else if (take_over_main(bluetool_main) != 0) {
			say("sweet-bt: BlueTool: could not take over main(); Apple's BlueTool runs\n");
		}
	}
}
