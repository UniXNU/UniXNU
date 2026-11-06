/* Run the exact kernel registration implementation with a locked mock runtime. */
#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef int kern_return_t;
enum { KERN_SUCCESS, KERN_FAILURE, KERN_NOT_SUPPORTED, KERN_INVALID_ARGUMENT, KERN_RESOURCE_SHORTAGE };
enum { kTCReturnSuccess, kTCReturnNotFound, kTCReturnFailure, kTCQueryTypeAll = 0, kTCTypeEngineering = 1 };
#define Z_WAITOK_ZERO 0
typedef struct { uint8_t CDHash[20], hashType, flags, constraintCategory, reserved0; } TrustCacheEntry2_t;
typedef struct { uint32_t version; uint8_t uuid[16]; uint32_t numEntries; TrustCacheEntry2_t entries[]; } TrustCacheModule2_t;
typedef struct Cache { struct Cache *next; TrustCacheModule2_t *module; } TrustCache_t;
typedef struct { int unused; } TrustCacheQueryToken_t;
typedef struct { int error; } TCReturn_t;
static uint32_t enabled = 1;
static bool fail_load, fail_query, fail_alloc;
static atomic_int allocations;
static unsigned loads;
static TrustCache_t *head;
static int runtime, *trust_cache_rt = &runtime;
static pthread_mutex_t trust_cache_rt_lock = PTHREAD_MUTEX_INITIALIZER;
static void *allocate(size_t size) {
    if (fail_alloc) return NULL;
    void *p = calloc(1, size); assert(p); atomic_fetch_add(&allocations, 1); return p;
}
static void release(void *p) { assert(p); atomic_fetch_sub(&allocations, 1); free(p); }
#define kalloc_type(type, flags) ((type *)allocate(sizeof(type)))
#define kalloc_data(size, flags) allocate(size)
#define kfree_type(type, ptr) release(ptr)
#define kfree_data(ptr, size) release(ptr)
#define lck_rw_lock_exclusive(lock) assert(pthread_mutex_lock(lock) == 0)
#define lck_rw_unlock_exclusive(lock) assert(pthread_mutex_unlock(lock) == 0)
static void PE_parse_boot_argn(const char *arg, void *output, size_t size) {
    assert(!strcmp(arg, "appsync") && size == sizeof(enabled)); memcpy(output, &enabled, size);
}
static TCReturn_t query(int *rt, int type, const uint8_t *hash, TrustCacheQueryToken_t *token) {
    assert(rt == trust_cache_rt && type == kTCQueryTypeAll && token);
    if (fail_query) return (TCReturn_t){kTCReturnFailure};
    for (TrustCache_t *c = head; c; c = c->next)
        if (!memcmp(c->module->entries[0].CDHash, hash, 20)) return (TCReturn_t){kTCReturnSuccess};
    return (TCReturn_t){kTCReturnNotFound};
}
static TCReturn_t load(int *rt, int type, TrustCache_t *cache, uintptr_t address, size_t size) {
    assert(rt == trust_cache_rt && type == kTCTypeEngineering);
    assert(size == sizeof(TrustCacheModule2_t) + sizeof(TrustCacheEntry2_t));
    TrustCacheModule2_t *m = (void *)address;
    assert(m->version == 2 && m->numEntries == 1);
    assert(m->entries[0].flags == 0 && m->entries[0].constraintCategory == 0);
    if (fail_load) return (TCReturn_t){kTCReturnFailure};
    cache->module = m; cache->next = head; head = cache; ++loads;
    return (TCReturn_t){kTCReturnSuccess};
}
static struct AMFI { struct {
    TCReturn_t (*query)(int *, int, const uint8_t *, TrustCacheQueryToken_t *);
    TCReturn_t (*loadModule)(int *, int, TrustCache_t *, uintptr_t, size_t);
} TrustCache; } mock_amfi = {{query, load}}, *amfi = &mock_amfi;
static kern_return_t xnu_query_trust_cache(int type, const uint8_t *hash, TrustCacheQueryToken_t *token) {
    lck_rw_lock_exclusive(&trust_cache_rt_lock);
    int error = query(trust_cache_rt, type, hash, token).error;
    lck_rw_unlock_exclusive(&trust_cache_rt_lock);
    return error == kTCReturnSuccess ? KERN_SUCCESS : KERN_FAILURE;
}
#include "appsync_trust.inc"

static const char *user_path = "/private/var/containers/Bundle/Application/NEW/New.app/New";
static void *racing_load(void *hash) {
    assert(appsync_trust_user_code(user_path, hash, 2) == KERN_SUCCESS); return NULL;
}
int main(void) {
    uint8_t hashes[5][20] = {{1}, {2}, {3}, {4}, {5}};
    const char *foreign[] = {"/System/Applications/One.app/One", "/private/var-other/One.app/One",
        "/private/var/One.appx/One", "/private/var/.app/One", "/private/var/One.app/../Other/Code"};
    for (unsigned i = 0; i < sizeof(foreign)/sizeof(*foreign); ++i)
        assert(appsync_trust_user_code(foreign[i], hashes[0], 2) == KERN_SUCCESS);
    enabled = 0;
    assert(appsync_trust_user_code(user_path, hashes[0], 2) == KERN_SUCCESS);
    assert(loads == 0 && allocations == 0);
    enabled = 1;
    pthread_t threads[32];
    for (unsigned i = 0; i < 32; ++i) assert(!pthread_create(&threads[i], NULL, racing_load, hashes[0]));
    for (unsigned i = 0; i < 32; ++i) assert(!pthread_join(threads[i], NULL));
    assert(loads == 1 && allocations == 2);
    assert(appsync_trust_user_code("/var/containers/Bundle/Application/NEW/New.app/Frameworks/F.framework/F", hashes[1], 1) == KERN_SUCCESS);
    assert(appsync_trust_user_code(user_path, hashes[2], 2) == KERN_SUCCESS); // new app version, same path
    assert(loads == 3 && allocations == 6);
    fail_load = true;
    assert(appsync_trust_user_code(user_path, hashes[3], 2) == KERN_FAILURE);
    fail_load = false; fail_query = true;
    assert(appsync_trust_user_code(user_path, hashes[3], 2) == KERN_FAILURE);
    fail_query = false; fail_alloc = true;
    assert(appsync_trust_user_code(user_path, hashes[3], 2) == KERN_RESOURCE_SHORTAGE);
    fail_alloc = false;
    assert(appsync_trust_user_code(user_path, hashes[3], 0) == KERN_INVALID_ARGUMENT);
    assert(loads == 3 && allocations == 6);
    while (head) { TrustCache_t *next = head->next; release(head->module); release(head); head = next; }
    assert(allocations == 0);
    puts("PASS: dynamic user trust, unlisted apps/updates/frameworks, concurrency, disabled scope and failures");
}
