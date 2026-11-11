/*
 * sweet-gpu-test: the Adreno 650 through the SweetAdreno user client (iokit/Kernel/arm/
 * SweetAdreno.cpp, kernel patches 0173+), the way Mesa freedreno's libdrm-msm stand-in will:
 *
 *   GET_PARAM (chip id, gmem, VA start), GEM_NEW two objects, GEM_INFO their GPU addresses,
 *   map the command object into this task, build an indirect buffer that CP_MEM_WRITEs four
 *   known words into the data object, GEM_SUBMIT it, WAIT_FENCE, read the data object back and
 *   compare, GEM_CLOSE both. Results go to /private/var/sweet/gpu-test.log, so they can be
 *   fetched from the Mac with tools/umi-files.py (the kernel file server, tcp 2223).
 *
 * PM4 packet encodings as in bsd/dev/sweet_adreno.c (CP_MEM_WRITE 0x3d; the type 7 header with
 * its parity bits). Build with phone/build-gpu-test.sh (iPhoneOS SDK + ldid).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <mach/mach.h>
#include <IOKit/IOKitLib.h>
#include "NativeAdrenoABI.h"

#define SEL_GET_PARAM   1
#define SEL_GEM_NEW     2
#define SEL_GEM_INFO    3
#define SEL_GEM_CLOSE   4
#define SEL_GEM_SUBMIT  5
#define SEL_WAIT_FENCE  6

/* msm DRM uAPI MSM_PARAM_* (include/uapi/drm/msm_drm.h) */
#define MSM_PARAM_GMEM_SIZE     0x02
#define MSM_PARAM_CHIP_ID       0x03
#define MSM_PARAM_VA_START      0x0e

#define CP_MEM_WRITE           0x3d

static int v1_test(void);
static int v2_test(void);

static FILE *logf;

static uint32_t
pm4_parity(uint32_t v)
{
	return 0x9669 >> (0xf & (v ^ v >> 4 ^ v >> 8 ^ v >> 12 ^ v >> 16 ^ v >> 20 ^ v >> 24 ^ v >> 28)) & 1;
}

static uint32_t
pkt7(uint32_t opcode, uint32_t words)
{
	return 7u << 28 | words | pm4_parity(words) << 15 | (opcode & 0x7f) << 16 | pm4_parity(opcode) << 23;
}

static kern_return_t
scalar(io_connect_t c, uint32_t sel, const uint64_t *in, uint32_t nin, uint64_t *out, uint32_t *nout)
{
	return IOConnectCallScalarMethod(c, sel, in, nin, out, nout);
}

static uint64_t
get_param(io_connect_t c, uint32_t param, const char *name)
{
	uint64_t out = 0;
	uint32_t nout = 1;
	kern_return_t k = scalar(c, SEL_GET_PARAM, &(uint64_t){ param }, 1, &out, &nout);
	fprintf(logf, "GET_PARAM %#x (%s) -> %#llx%s\n", param, name, out,
	    k == kIOReturnSuccess ? "" : " (failed)");
	return k == kIOReturnSuccess ? out : 0;
}

static int
fail(const char *what, kern_return_t k)
{
	fprintf(logf, "FAIL: %s: %#x\n", what, k);
	fflush(logf);
	return 1;
}

static const uint32_t words[4] = { 0x5eed0001u, 0x5eed0002u, 0x5eed0003u, 0x5eed0004u };

int
main(void)
{
	logf = fopen("/private/var/sweet/gpu-test.log", "w");
	if (logf == NULL) {
		logf = stderr;
	}
	setvbuf(logf, NULL, _IONBF, 0);           /* every line on disk at once: the file server reads it */
	fprintf(logf, "sweet-gpu-test: start (pid %d, bootstrap port %#x)\n", getpid(), bootstrap_port);
	int v1 = v1_test();
	int v2 = v2_test();
	int pass = v1 == 0 && v2 == 0;
	fprintf(logf, "sweet-gpu-test: %s (v1 %s, v2 %s)\n", pass ? "PASS" : "FAIL",
	    v1 == 0 ? "PASS" : "FAIL", v2 == 0 ? "PASS" : "FAIL");
	fflush(logf);
	return pass ? 0 : 1;
}

/* ---- v1: the msm-uAPI-shaped selectors (the 0173/0174 test) ---- */

static int
v1_test(void)
{
	io_connect_t connect = MACH_PORT_NULL;
	io_iterator_t iter;
	kern_return_t k;
	uint64_t in[3], out[2];
	uint32_t nout;

	/* Find the service the way a user-space driver would. The GPU bring-up (boot-arg
	 * sweetgpu) only has the core running a minute or so into the boot, and launchd
	 * starts this daemon before that: keep looking, then keep opening, for up to 4 min. */
	mach_port_t mainPort = MACH_PORT_NULL;
	kern_return_t pk = IOMainPort(bootstrap_port, &mainPort);
	fprintf(logf, "IOMainPort -> %#x (port %#x)\n", pk, mainPort);
	for (int tries = 0; tries < 48 && connect == MACH_PORT_NULL; tries++) {
		CFMutableDictionaryRef match = IOServiceMatching("SweetAdreno");
		fprintf(logf, "IOServiceGetMatchingServices try %d...\n", tries);
		k = IOServiceGetMatchingServices(mainPort, match, &iter);
		if (k != KERN_SUCCESS) {
			return fail("IOServiceGetMatchingServices(SweetAdreno)", k);
		}
		fprintf(logf, "lookup -> %#x\n", k);
		io_service_t service = IOIteratorNext(iter);
		IOObjectRelease(iter);
		if (service == MACH_PORT_NULL) {
			fprintf(logf, "no SweetAdreno service yet (try %d)\n", tries);
			sleep(5);
			continue;
		}
		fprintf(logf, "service found (%#x), opening\n", service);
		k = IOServiceOpen(service, mach_task_self(), 0, &connect);
		IOObjectRelease(service);
		fprintf(logf, "IOServiceOpen -> %#x\n", k);
		if (k != KERN_SUCCESS) {
			connect = MACH_PORT_NULL;
			sleep(5);
		}
	}
	if (connect == MACH_PORT_NULL) {
		return fail("SweetAdreno never opened", KERN_FAILURE);
	}
	fprintf(logf, "SweetAdreno opened\n");

	(void)get_param(connect, MSM_PARAM_CHIP_ID, "chip id");
	(void)get_param(connect, MSM_PARAM_GMEM_SIZE, "gmem bytes");
	(void)get_param(connect, MSM_PARAM_VA_START, "VA start");

	/* Two objects: commands and data. */
	uint64_t cmd_handle = 0, cmd_gpu = 0, data_handle = 0, data_gpu = 0;
	in[0] = 16384;
	nout = 1;
	if (scalar(connect, SEL_GEM_NEW, in, 1, out, &nout) != kIOReturnSuccess || nout != 1) {
		return fail("GEM_NEW commands", k);
	}
	cmd_handle = out[0];
	nout = 1;
	if (scalar(connect, SEL_GEM_NEW, in, 1, out, &nout) != kIOReturnSuccess || nout != 1) {
		return fail("GEM_NEW data", k);
	}
	data_handle = out[0];
	in[0] = cmd_handle;
	nout = 2;
	if (scalar(connect, SEL_GEM_INFO, in, 1, out, &nout) != kIOReturnSuccess) {
		return fail("GEM_INFO commands", k);
	}
	cmd_gpu = out[0];
	in[0] = data_handle;
	nout = 2;
	if (scalar(connect, SEL_GEM_INFO, in, 1, out, &nout) != kIOReturnSuccess) {
		return fail("GEM_INFO data", k);
	}
	data_gpu = out[0];
	fprintf(logf, "commands handle %llu at the core's %#llx, data handle %llu at %#llx\n",
	    cmd_handle, cmd_gpu, data_handle, data_gpu);

	/* The command object in this task: build the indirect buffer in it. */
	mach_vm_address_t map_addr = 0;
	mach_vm_size_t map_size = 0;
	k = IOConnectMapMemory(connect, (uint32_t)cmd_handle, mach_task_self(), &map_addr, &map_size,
	    kIOMapAnywhere);
	if (k != KERN_SUCCESS) {
		return fail("IOConnectMapMemory(commands)", k);
	}
	volatile uint32_t *ib = (volatile uint32_t *)map_addr;
	uint32_t n = 0;
	ib[n++] = pkt7(CP_MEM_WRITE, 2 + 4);
	ib[n++] = (uint32_t)data_gpu;
	ib[n++] = (uint32_t)(data_gpu >> 32);
	for (int i = 0; i < 4; i++) {
		ib[n++] = words[i];
	}
	fprintf(logf, "IB of %u words built at %#llx (mapped %llu bytes)\n", n, (unsigned long long)map_addr,
	    (unsigned long long)map_size);

	/* Submit and wait. */
	in[0] = cmd_handle;
	in[1] = 0;
	in[2] = n;
	nout = 1;
	k = scalar(connect, SEL_GEM_SUBMIT, in, 3, out, &nout);
	if (k != kIOReturnSuccess) {
		return fail("GEM_SUBMIT", k);
	}
	uint64_t fence = out[0];
	fprintf(logf, "GEM_SUBMIT -> fence %llu\n", fence);
	in[0] = fence;
	in[1] = 2000;
	nout = 1;
	k = scalar(connect, SEL_WAIT_FENCE, in, 2, out, &nout);
	if (k != kIOReturnSuccess) {
		return fail("WAIT_FENCE", k);
	}
	fprintf(logf, "WAIT_FENCE(%llu, 2000 ms) -> %s\n", fence, out[0] ? "signalled" : "NOT signalled");
	if (!out[0]) {
		goto out;
	}

	/* The data object in this task: read back what the core wrote. */
	mach_vm_address_t data_addr = 0;
	mach_vm_size_t data_size = 0;
	k = IOConnectMapMemory(connect, (uint32_t)data_handle, mach_task_self(), &data_addr, &data_size,
	    kIOMapAnywhere);
	if (k != KERN_SUCCESS) {
		return fail("IOConnectMapMemory(data)", k);
	}
	volatile uint32_t *got = (volatile uint32_t *)data_addr;
	int right = got[0] == words[0] && got[1] == words[1] && got[2] == words[2] && got[3] == words[3];
	int pass = right;
	fprintf(logf, "the data object reads %#x %#x %#x %#x: %s\n", got[0], got[1], got[2], got[3],
	    right ? "as the core was told to write (USER SPACE DRAWS WITH THE GPU)" :
	    "NOT what the core was told to write");

out:
	in[0] = cmd_handle;
	(void)scalar(connect, SEL_GEM_CLOSE, in, 1, out, &nout);
	in[0] = data_handle;
	(void)scalar(connect, SEL_GEM_CLOSE, in, 1, out, &nout);
	fprintf(logf, "v1 (msm-uAPI) test: %s\n", pass ? "PASS" : "FAIL");
	fflush(logf);
	IOServiceClose(connect);
	return pass ? 0 : 1;
}

/* ---- v2: the NativeAdreno ABI (Turnip's darwin backend), as tu_knl_darwin.cc uses it ---- */

static kern_return_t
v2call(io_connect_t c, uint32_t method, const void *in, size_t insz, void *out, size_t *outsz)
{
	return IOConnectCallStructMethod(c, method, in, insz, out, outsz);
}

/* Turnip's tunnel form: {'NTNL', method, payload} through the first admitted selector. */
static kern_return_t
v2tun(io_connect_t c, uint32_t method, const void *in, size_t insz, void *out, size_t *outsz)
{
	uint8_t buf[8 + 416];
	if (insz > 408 || insz + 8 < 8) {
		return KERN_INVALID_ARGUMENT;
	}
	((uint32_t *)buf)[0] = 0x4e544e4cu;       /* 'NTNL' */
	((uint32_t *)buf)[1] = method;
	if (insz) {
		memcpy(buf + 8, in, insz);
	}
	return IOConnectCallStructMethod(c, 0, buf, 8 + insz, out, outsz);
}

static int
v2_test(void)
{
	io_service_t service = MACH_PORT_NULL;
	io_connect_t c = MACH_PORT_NULL;
	kern_return_t k;

	/* open the same service with the v2 ('AG') type */
	CFMutableDictionaryRef match = IOServiceMatching("SweetAdreno");
	io_iterator_t iter;
	k = IOServiceGetMatchingServices(MACH_PORT_NULL, match, &iter);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: no matching services: %#x\n", k);
		return 1;
	}
	service = IOIteratorNext(iter);
	IOObjectRelease(iter);
	if (service == MACH_PORT_NULL) {
		fprintf(logf, "v2: no SweetAdreno service\n");
		return 1;
	}
	k = IOServiceOpen(service, mach_task_self(), 0x4147, &c);
	IOObjectRelease(service);
	if (k != KERN_SUCCESS || c == MACH_PORT_NULL) {
		fprintf(logf, "v2: open type 0x4147 refused: %#x\n", k);
		return 1;
	}
	fprintf(logf, "v2: SweetAdreno opened (type 0x4147)\n");

	struct NativeAdrenoAbiParams params;
	size_t sz = sizeof(params);
	k = v2call(c, NativeAdrenoMethodQuery, NULL, 0, &params, &sz);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: Query -> %#x\n", k);
		goto out;
	}
	fprintf(logf, "v2: Query -> abi %u, input bits %u, output bits %u, max bo %#llx\n",
	    params.abi_version, params.input_bits, params.output_bits, (unsigned long long)params.max_bo_bytes);


	struct NativeAdrenoAbiDeviceInfo di;
	sz = sizeof(di);
	k = v2call(c, NativeAdrenoMethodGetDeviceInfo, NULL, 0, &di, &sz);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: GetDeviceInfo -> %#x\n", k);
		goto out;
	}
	fprintf(logf, "v2: DeviceInfo -> chip id %#x, gmem %#x at %#llx, va %#llx..%#llx, hbb %u, ubwc %u\n",
	    di.chip_id, di.gmem_bytes, (unsigned long long)di.gmem_base, (unsigned long long)di.va_start,
	    (unsigned long long)(di.va_start + di.va_size), di.highest_bank_bit, di.ubwc_version);
	/* the tunnel form Turnip uses (probe selector 0, method 0xffffffff answers success) */
	uint32_t probe[2] = { 0x4e544e4cu, 0xffffffffu };
	k = IOConnectCallStructMethod(c, 0, probe, sizeof(probe), NULL, NULL);
	fprintf(logf, "v2: tunnel probe -> %#x (%s)\n", k, k == KERN_SUCCESS ? "admitted" : "REFUSED");
	struct NativeAdrenoAbiParams p2;
	sz = sizeof(p2);
	k = v2tun(c, NativeAdrenoMethodQuery, NULL, 0, &p2, &sz);
	fprintf(logf, "v2: tunnel Query -> %#x, abi %u\n", k, p2.abi_version);
	struct NativeAdrenoAbiBoAlloc ba2 = { .bytes = 16384, .align_log2 = 12, .contiguous = 0 };
	struct NativeAdrenoAbiBoAllocReply br2;
	sz = sizeof(br2);
	k = v2tun(c, NativeAdrenoMethodBoAlloc, &ba2, sizeof(ba2), &br2, &sz);
	fprintf(logf, "v2: tunnel BoAlloc -> %#x, handle %llu\n", k, (unsigned long long)br2.handle);
	struct NativeAdrenoAbiBoMap bm2 = { .handle = br2.handle, .iova = di.va_start, .permissions = 3,
		.writeback = 0, .shareability = 2, .reserved = 0 };
	struct NativeAdrenoAbiBoMapReply bmr2;
	sz = sizeof(bmr2);
	k = v2tun(c, NativeAdrenoMethodBoMap, &bm2, sizeof(bm2), &bmr2, &sz);
	fprintf(logf, "v2: tunnel BoMap(%llu at %#llx) -> %#x (%s)\n", (unsigned long long)bm2.handle,
	    (unsigned long long)bm2.iova, k, k == KERN_SUCCESS ? "mapped" : "REFUSED - the Turnip failure");
	struct NativeAdrenoAbiBoFree bf2 = { .handle = br2.handle };
	(void)v2tun(c, NativeAdrenoMethodBoFree, &bf2, sizeof(bf2), NULL, 0);

	/* two objects: commands and data, at addresses we pick in our window */
	struct NativeAdrenoAbiBoAlloc ba = { .bytes = 16384, .align_log2 = 12, .contiguous = 0 };
	struct NativeAdrenoAbiBoAllocReply br;
	sz = sizeof(br);
	k = v2call(c, NativeAdrenoMethodBoAlloc, &ba, sizeof(ba), &br, &sz);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: BoAlloc commands -> %#x\n", k);
		goto out;
	}
	uint64_t cmd_h = br.handle;
	sz = sizeof(br);
	if (v2call(c, NativeAdrenoMethodBoAlloc, &ba, sizeof(ba), &br, &sz) != KERN_SUCCESS) {
		fprintf(logf, "v2: BoAlloc data -> %#x\n", k);
		goto out;
	}
	uint64_t data_h = br.handle;
	fprintf(logf, "v2: BoAlloc -> commands handle %llu, data handle %llu\n",
	    (unsigned long long)cmd_h, (unsigned long long)data_h);

	uint64_t cmd_iova = di.va_start + 0x100000, data_iova = di.va_start + 0x200000;
	struct NativeAdrenoAbiBoMap bm = { .handle = cmd_h, .iova = cmd_iova, .permissions = 3,
		.writeback = 0, .shareability = 2, .reserved = 0 };
	struct NativeAdrenoAbiBoMapReply bmr;
	sz = sizeof(bmr);
	k = v2call(c, NativeAdrenoMethodBoMap, &bm, sizeof(bm), &bmr, &sz);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: BoMap commands -> %#x\n", k);
		goto out;
	}
	bm.handle = data_h;
	bm.iova = data_iova;
	sz = sizeof(bmr);
	if (v2call(c, NativeAdrenoMethodBoMap, &bm, sizeof(bm), &bmr, &sz) != KERN_SUCCESS) {
		fprintf(logf, "v2: BoMap data -> %#x\n", k);
		goto out;
	}
	fprintf(logf, "v2: BoMap -> commands at %#llx, data at %#llx\n",
	    (unsigned long long)cmd_iova, (unsigned long long)data_iova);

	/* the command object in this task (BoCpuMap -> token -> IOConnectMapMemory) */
	struct NativeAdrenoAbiBoCpuMap cm = { .handle = cmd_h };
	struct NativeAdrenoAbiBoCpuMapReply cmr;
	sz = sizeof(cmr);
	k = v2call(c, NativeAdrenoMethodBoCpuMap, &cm, sizeof(cm), &cmr, &sz);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: BoCpuMap -> %#x\n", k);
		goto out;
	}
	mach_vm_address_t map_addr = 0;
	mach_vm_size_t map_size = 0;
	k = IOConnectMapMemory(c, cmr.token, mach_task_self(), &map_addr, &map_size, kIOMapAnywhere);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: map commands token %u -> %#x\n", cmr.token, k);
		goto out;
	}
	volatile uint32_t *ib = (volatile uint32_t *)map_addr;
	uint32_t n = 0;
	ib[n++] = pkt7(CP_MEM_WRITE, 2 + 4);
	ib[n++] = (uint32_t)data_iova;
	ib[n++] = (uint32_t)(data_iova >> 32);
	for (int i = 0; i < 4; i++) {
		ib[n++] = words[i];
	}

	/* submit, wait, read the data object back through its own map */
	struct NativeAdrenoAbiSubmit sub;
	bzero(&sub, sizeof(sub));
	sub.buffer_count = 1;
	sub.buffers[0].handle = cmd_h;
	sub.buffers[0].iova = cmd_iova;
	sub.buffers[0].bytes = 4ull * n;
	struct NativeAdrenoAbiSubmitReply sr;
	sz = sizeof(sr);
	k = v2call(c, NativeAdrenoMethodSubmit, &sub, sizeof(sub), &sr, &sz);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: Submit -> %#x\n", k);
		goto out;
	}
	fprintf(logf, "v2: Submit %u words -> fence %llu\n", n, (unsigned long long)sr.fence);

	struct NativeAdrenoAbiWaitFence wf = { .fence = sr.fence, .timeout_ns = 2000000000ull };
	k = v2call(c, NativeAdrenoMethodWaitFence, &wf, sizeof(wf), NULL, 0);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: WaitFence(%llu) -> %#x (NOT signalled)\n", (unsigned long long)sr.fence, k);
		goto out;
	}
	fprintf(logf, "v2: WaitFence(%llu) signalled\n", (unsigned long long)sr.fence);

	cm.handle = data_h;
	sz = sizeof(cmr);
	if (v2call(c, NativeAdrenoMethodBoCpuMap, &cm, sizeof(cm), &cmr, &sz) != KERN_SUCCESS) {
		fprintf(logf, "v2: BoCpuMap data -> %#x\n", k);
		goto out;
	}
	mach_vm_address_t data_addr = 0;
	mach_vm_size_t data_size = 0;
	k = IOConnectMapMemory(c, cmr.token, mach_task_self(), &data_addr, &data_size, kIOMapAnywhere);
	if (k != KERN_SUCCESS) {
		fprintf(logf, "v2: map data token %u -> %#x\n", cmr.token, k);
		goto out;
	}
	volatile uint32_t *got = (volatile uint32_t *)data_addr;
	int right = got[0] == words[0] && got[1] == words[1] && got[2] == words[2] && got[3] == words[3];
	fprintf(logf, "v2: the data object reads %#x %#x %#x %#x: %s\n", got[0], got[1], got[2], got[3],
	    right ? "as the core was told to write (THE TURNIP ABI WORKS)" :
	    "NOT what the core was told to write");

	struct NativeAdrenoAbiTimestamp ts;
	sz = sizeof(ts);
	if (v2call(c, NativeAdrenoMethodGetTimestamp, NULL, 0, &ts, &sz) == KERN_SUCCESS) {
		fprintf(logf, "v2: GetTimestamp -> %llu\n", (unsigned long long)ts.ticks);
	}

	struct NativeAdrenoAbiBoFree bf = { .handle = data_h };
	(void)v2call(c, NativeAdrenoMethodBoFree, &bf, sizeof(bf), NULL, 0);
	bf.handle = cmd_h;
	(void)v2call(c, NativeAdrenoMethodBoFree, &bf, sizeof(bf), NULL, 0);
	fprintf(logf, "v2 (NativeAdreno/Turnip ABI) test: %s\n", right ? "PASS" : "FAIL");
	IOServiceClose(c);
	return right ? 0 : 1;

out:
	{
		struct NativeAdrenoAbiBoFree bf = { .handle = data_h };
		(void)v2call(c, NativeAdrenoMethodBoFree, &bf, sizeof(bf), NULL, 0);
		bf.handle = cmd_h;
		(void)v2call(c, NativeAdrenoMethodBoFree, &bf, sizeof(bf), NULL, 0);
	}
	IOServiceClose(c);
	return 1;
}
