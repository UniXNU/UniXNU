/* Host adapters for the actual XNU functions compiled by test_text_fixup.py. */
#define _DEFAULT_SOURCE
#include <assert.h>
#include <arpa/inet.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#define SHA256_CTX CC_SHA256_CTX
#define SHA256_Init CC_SHA256_Init
#define SHA256_Update CC_SHA256_Update
#define SHA256_Final CC_SHA256_Final
#else
#include <openssl/sha.h>
#endif
#define PAGE_SHIFT 12
#define PAGE_SIZE 4096
#define PAGE_MASK 4095
#define CS_TEXT_FIXUP_MAX 32
#define CS_TEXT_FIXUP_BYTES 16
#define CS_HASH_MAX_SIZE 64
#define CS_LAZY_BLOCK 16384
#define CS_LAZY_SLOT 32
#define CS_NATIVE4K_UNCACHED (32 * 1024 * 1024)
#define CS_NATIVE4K_CHUNK (1024 * 1024)
#define EBADEXEC 85
#define ENOMEM 12
#define EOVERFLOW 75
#define EIO 5
#define UIO_READ 0
#define UIO_SYSSPACE 0
#define XNU_NATIVE_CS_HASH_CACHE 1
#define CS_VALIDATE_TAINTED 1
#define CS_VALIDATE_NX 2
#define Z_WAITOK 0
#define UBC_FLAGS_NONE 0
#define KERN_SUCCESS 0
#define KERN_MEMORY_ERROR 1
#define KERN_RESOURCE_SHORTAGE 2
#define MEMORY_OBJECT_CONTROL_NULL NULL
#define NULLVP NULL
#define TRUE 1
#define FALSE 0
#define CAST_DOWN(type, value) ((type)(value))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define panic(...) abort()
#define os_atomic_inc(value, order) (++*(value))
#define os_atomic_add(value, delta, order) (*(value) += (delta))
#define os_atomic_load(value, order) atomic_load(value)
#define os_atomic_add_orig(value, delta, order) atomic_fetch_add(value, delta)
#define os_atomic_cmpxchgv(value, old, new, answer, order) atomic_compare_exchange_strong(value, answer, new)
#define os_add_overflow(a, b, result) __builtin_add_overflow(a, b, result)
typedef uint64_t memory_object_offset_t;
typedef size_t vm_size_t;
typedef uintptr_t vm_offset_t;
typedef void *memory_object_t;
typedef void *memory_object_control_t;
typedef int boolean_t;
typedef int kern_return_t;
typedef int kauth_cred_t;
typedef int lck_mtx_t;
struct vnode { const char *v_name; };
typedef struct vnode *vnode_t;
union cs_hash_union { SHA256_CTX sha256; };
struct cs_hash {
    size_t cs_size, cs_digest_size;
    void (*cs_init)(union cs_hash_union *);
    void (*cs_update)(union cs_hash_union *, const void *, size_t);
    void (*cs_final)(unsigned char *, union cs_hash_union *);
};
static void sha_init(union cs_hash_union *ctx) { assert(SHA256_Init(&ctx->sha256)); }
static void sha_update(union cs_hash_union *ctx, const void *data, size_t length) {
    assert(SHA256_Update(&ctx->sha256, data, length));
}
static void sha_final(unsigned char *digest, union cs_hash_union *ctx) { assert(SHA256_Final(digest, &ctx->sha256)); }
static const struct cs_hash sha256 = { 32, 32, sha_init, sha_update, sha_final };
typedef struct { uint32_t codeLimit; } CS_CodeDirectory;
struct cs_native4k_lazy { int unused; };
struct cs_native4k_lazy_chunk { int unused; };
struct cs_blob {
    struct cs_blob *csb_next;
    off_t csb_base_offset, csb_start_offset, csb_end_offset;
    void *csb_mem_kaddr;
    size_t csb_mem_offset, csb_mem_size;
    const CS_CodeDirectory *csb_cd;
    const struct cs_hash *csb_hashtype;
    unsigned csb_hash_pageshift, csb_hash_firstlevel_pageshift;
    const unsigned char *csb_native4k_hashes;
    size_t csb_native4k_hashes_size, csb_native4k_hash_count;
    const struct cs_native4k_lazy *csb_native4k_lazy;
};
struct cs_text_fixup {
    char name[64];
    uint64_t offset;
    uint8_t original[CS_TEXT_FIXUP_BYTES], replacement[CS_TEXT_FIXUP_BYTES];
    uint32_t length;
};
static struct cs_text_fixup cs_text_fixups[CS_TEXT_FIXUP_MAX];
static uint32_t cs_text_fixup_count, cs_text_fixup_applied;
static unsigned long cs_validate_page_no_hash, cs_validate_page_bad_hash, cs_native4k_page_checks;
static uint64_t cs_native4k_read_ticks, cs_native4k_bytes, cs_native4k_hash_ticks, cs_native4k_lazy_ticks;
static uint64_t cs_native4k_chunk_ticks, cs_native4k_record_ticks;
static unsigned long cs_native4k_lazy_errors;
static unsigned long cs_native4k_full_blocks;
static int cs_debug, fixture_ready;
static struct cs_native4k_lazy fixture_lazy;
static unsigned char expected_digest[32], recorded_hashes[4][32];
static const unsigned char *fixture_bytes;
static uint64_t fixture_base;
static size_t fixture_length;
struct cs_native4k_clock { int unused; };
static void cs_native4k_clock_start(struct cs_native4k_clock *clock) {}
static void cs_native4k_clock_stop(struct cs_native4k_clock *clock, uint64_t bytes) {}
static uint64_t mach_absolute_time(void) { return 0; }
static void *kalloc_data(size_t length, int flags) { return calloc(1, length); }
static void kfree_data(void *data, size_t length) { free(data); }
static void *ubc_getobject(struct vnode *vp, int flags) { return vp; }
static void *current_proc(void) { return NULL; }
static int vn_rdwr(int mode, struct vnode *vp, char *buffer, int length, off_t position,
                   int space, int flags, int cred, int *resid, void *proc) {
    assert((uint64_t)position >= fixture_base);
    size_t at = (size_t)((uint64_t)position - fixture_base);
    assert(at <= fixture_length && (size_t)length <= fixture_length - at);
    memcpy(buffer, fixture_bytes + at, (size_t)length);
    *resid = 0;
    return 0;
}
static struct vnode *vnode_pager_lookup_vnode(memory_object_t pager) { return pager; }
static void cs_native4k_touch(struct cs_blob *blob, size_t index, bool large) {}
static const unsigned char *hashes(const CS_CodeDirectory *cd, uint32_t block, size_t size,
                                   const char *lower, const char *upper) { return expected_digest; }
static const unsigned char *cs_native4k_lazy_hash(const struct cs_blob *blob, off_t offset,
                                                 off_t limit, size_t size, unsigned *answer) { return expected_digest; }
static struct cs_native4k_lazy_chunk *cs_native4k_lazy_chunk(const struct cs_native4k_lazy *lazy,
                                                           uint32_t block, bool create) {
    static struct cs_native4k_lazy_chunk chunk;
    return &chunk;
}
static void cs_native4k_lazy_record(struct cs_native4k_lazy_chunk *chunk, uint32_t block, const void *derived) {
    fixture_ready = derived != NULL;
    if (derived) memcpy(recorded_hashes, derived, sizeof(recorded_hashes));
}
static int vm_fault_cs_lazy_fetch(memory_object_control_t control, uint64_t offset,
                                 uint64_t start, uint64_t end, void *buffer) {
    assert(offset >= fixture_base && offset - fixture_base < fixture_length);
    size_t at = (size_t)(offset - fixture_base);
    size_t length = MIN((size_t)PAGE_SIZE, fixture_length - at);
    memcpy(buffer, fixture_bytes + at, length);
    return KERN_SUCCESS;
}
