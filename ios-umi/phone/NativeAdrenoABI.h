/* NativeAdreno user-client ABI v1 (UniXNU drivers/NativeAdreno/NativeAdrenoABI.h, MIT): what Turnip's darwin backend
 * (work/turnip/mesa src/freedreno/vulkan/tu_knl_darwin.cc) speaks. the user-space copy of the kernel's SweetGPUABI.h (SweetAdreno.cpp serves it). */
/* SPDX-License-Identifier: MIT */
#ifndef NATIVE_ADRENO_ABI_H
#define NATIVE_ADRENO_ABI_H
#include <stdint.h>

/* Versioned kernel/user-client wire ABI for the native Adreno driver. This is
 * NOT the Metal, IOKit or Turnip ABI and it does not describe an ioctl. The
 * IOKit service will copy exactly these fixed-size records across its external
 * methods. All fields are little endian; both participants are ARM64. Every
 * array is inside one fixed record so a caller cannot pass a length that
 * disagrees with the storage. Unknown versions, methods and flags are refused
 * rather than ignored. */
enum {
    NativeAdrenoAbiVersion = 1,
    NativeAdrenoAbiMaxBuffers = 16,
    NativeAdrenoAbiMaxBoBytesShift = 28, /* 256MiB per object */
    NativeAdrenoMethodQuery = 1,
    NativeAdrenoMethodBoAlloc = 2,
    NativeAdrenoMethodBoMap = 3,
    NativeAdrenoMethodBoFree = 4,
    NativeAdrenoMethodSubmit = 5,
    NativeAdrenoMethodWaitFence = 6,
    NativeAdrenoMethodGetTimestamp = 7,
    NativeAdrenoMethodGetStatus = 8,
    NativeAdrenoMethodSetMetadata = 9,
    NativeAdrenoMethodGetMetadata = 10,
    NativeAdrenoMethodCreateQueue = 11,
    NativeAdrenoMethodCloseQueue = 12,
    NativeAdrenoMethodBoCpuMap = 13,
    NativeAdrenoMethodBoCpuUnmap = 14,
    NativeAdrenoMethodGetDeviceInfo = 15,
    NativeAdrenoMethodBoImport = 16,
    NativeAdrenoAbiMetadataBytes = 64,
    NativeAdrenoAbiMaxQueues = 8
};
struct NativeAdrenoAbiParams {
    uint32_t abi_version;
    uint32_t input_bits;          /* GPU VA bits below 2^input_bits */
    uint32_t output_bits;         /* physical address bits */
    uint32_t flags;               /* NativeAdrenoParamsHostImport or zero */
    uint64_t max_bo_bytes;
};
enum {
    NativeAdrenoParamsHostImport = 1  /* BoImport pins the caller's own pages (an IOSurface's) as a BO */
};
struct NativeAdrenoAbiBoAlloc {
    uint64_t bytes;               /* 4KiB multiple, <= max_bo_bytes */
    uint32_t align_log2;          /* 12..24 */
    uint32_t contiguous;          /* 1 requires one raw physical span */
};
struct NativeAdrenoAbiBoAllocReply {
    uint64_t handle;              /* opaque to userspace, nonzero */
};
/* Pins [address, address + bytes) of the CALLING task and makes it a BO (reply: NativeAdrenoAbiBoAllocReply). The pages stay wired
 * until BoFree; they keep the caller's own CPU mapping and cache mode, so the caller cleans its caches before GPU use and invalidates
 * them after GPU writes (the GPU maps them non-cacheable). An imported BO has no CPU-map token. */
struct NativeAdrenoAbiBoImport {
    uint64_t address;             /* 4KiB aligned */
    uint64_t bytes;               /* 4KiB multiple, <= max_bo_bytes */
};
struct NativeAdrenoAbiBoMap {
    uint64_t handle;
    uint64_t iova;                /* 4KiB aligned, inside the mounted aperture */
    uint32_t permissions;         /* bit0 read, bit1 write; read required */
    uint32_t writeback;           /* 0 normal non-coherent, 1 WB/WA */
    uint32_t shareability;        /* 2 outer, 3 inner */
    uint32_t reserved;            /* zero */
};
struct NativeAdrenoAbiBoMapReply {
    uint64_t iova;
};
struct NativeAdrenoAbiBoFree {
    uint64_t handle;
};
struct NativeAdrenoAbiSubmitBuffer {
    uint64_t handle;
    uint64_t iova;
    uint64_t bytes;               /* 4-byte multiple, dword count = bytes/4 */
};
struct NativeAdrenoAbiSubmit {
    uint32_t buffer_count;        /* 1..NativeAdrenoAbiMaxBuffers */
    uint32_t reserved;            /* zero */
    uint64_t queue;               /* open queue; 0 is created by open() */
    uint64_t wait_fence;          /* zero or an earlier fence of this client */
    uint64_t wait_timeout_ns;     /* used only when wait_fence is nonzero */
    struct NativeAdrenoAbiSubmitBuffer buffers[NativeAdrenoAbiMaxBuffers];
};
struct NativeAdrenoAbiMetadata {
    uint64_t handle;              /* object identity */
    uint32_t bytes;               /* set: length; get: requested capacity */
    uint32_t reserved;            /* zero */
    char text[NativeAdrenoAbiMetadataBytes]; /* raw bytes, not NUL terminated */
};
struct NativeAdrenoAbiSubmitReply {
    uint64_t fence;               /* nonzero CP timestamp value */
};
struct NativeAdrenoAbiWaitFence {
    uint64_t fence;
    uint64_t timeout_ns;          /* 0 polls once */
};
struct NativeAdrenoAbiTimestamp {
    uint64_t ticks;               /* GPU always-on counter value */
};
struct NativeAdrenoAbiBoCpuMap {
    uint64_t handle;
};
struct NativeAdrenoAbiBoCpuMapReply {
    uint32_t token;               /* clientMemoryForType selector */
    uint32_t reserved;            /* zero */
    uint64_t bytes;               /* bytes the mapping covers */
};
struct NativeAdrenoAbiBoCpuUnmap {
    uint64_t handle;
    uint32_t token;               /* exactly the token returned by map */
    uint32_t reserved;            /* zero */
};
struct NativeAdrenoAbiQueue {
    uint64_t queue;               /* zero for create, an open id for close */
};
struct NativeAdrenoAbiQueueReply {
    uint64_t queue;               /* nonzero id of the created queue */
};
struct NativeAdrenoAbiStatus {
    uint64_t faults;              /* monotonic; change means context lost */
    uint64_t suspends;            /* monotonic suspend/reset count */
};
/* Fixed facts of the mounted GPU that the Vulkan driver needs and cannot derive: all come from the board code, which takes
 * them from the pinned sources (a6xx catalog, UBWC config, the programmed UCHE ranges), never from a guess. */
enum {
    NativeAdrenoDeviceClientIova = 1,     /* flags: the client chooses BO addresses (BoMap iova) */
    NativeAdrenoDeviceCachedCoherent = 2  /* flags: unused until IO-coherent BO memory exists */
};
struct NativeAdrenoAbiDeviceInfo {
    uint32_t chip_id;             /* ADRENO_CHIPID, e.g. 0x43050a01 */
    uint32_t gmem_bytes;
    uint64_t gmem_base;           /* UCHE GMEM window start (GPU address) */
    uint64_t uche_trap_base;
    uint64_t va_start;            /* first GPU address the client may map */
    uint64_t va_size;
    uint32_t highest_bank_bit;
    uint32_t ubwc_swizzle;        /* bit0 level 1, bit1 level 2, bit2 level 3 */
    uint32_t macrotile_mode;      /* 0 four channel, 1 eight channel */
    uint32_t ubwc_version;        /* encoder version, 4 for UBWC 4.0 */
    uint32_t flags;
    uint32_t reserved;            /* zero */
};
#if defined(__cplusplus)
static_assert(sizeof(NativeAdrenoAbiDeviceInfo) == 64, "ABI device info layout");
static_assert(sizeof(NativeAdrenoAbiParams) == 24, "ABI params layout");
static_assert(sizeof(NativeAdrenoAbiBoAlloc) == 16, "ABI alloc layout");
static_assert(sizeof(NativeAdrenoAbiBoMap) == 32, "ABI map layout");
static_assert(sizeof(NativeAdrenoAbiBoImport) == 16, "ABI import layout");
static_assert(sizeof(NativeAdrenoAbiSubmitBuffer) == 24, "ABI buffer layout");
static_assert(sizeof(NativeAdrenoAbiSubmit) == 416, "ABI submit layout");
static_assert(sizeof(NativeAdrenoAbiBoCpuMap) == 8, "ABI cpu map layout");
static_assert(sizeof(NativeAdrenoAbiBoCpuMapReply) == 16, "ABI cpu map reply layout");
static_assert(sizeof(NativeAdrenoAbiBoCpuUnmap) == 16, "ABI cpu unmap layout");
static_assert(sizeof(NativeAdrenoAbiQueue) == 8, "ABI queue layout");
static_assert(sizeof(NativeAdrenoAbiQueueReply) == 8, "ABI queue reply layout");
static_assert(sizeof(NativeAdrenoAbiMetadata) == 80, "ABI metadata layout");
static_assert(sizeof(NativeAdrenoAbiWaitFence) == 16, "ABI wait layout");
static_assert(sizeof(NativeAdrenoAbiTimestamp) == 8, "ABI timestamp layout");
static_assert(sizeof(NativeAdrenoAbiStatus) == 16, "ABI status layout");
#endif
#endif
