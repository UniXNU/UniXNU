#!/usr/bin/env python3
"""Host ASan+UBSan tests for SoftwareAES 0x899/0x8a4 key derivation and telemetry."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
AES_DIR = ROOT / 'drivers/SoftwareAES'


HARNESS_HEADERS = {
    'IOKit/IOService.h': r'''#pragma once
#include <cstddef>
#include <cstdint>

using IOReturn = int;
using IOOptionBits = unsigned;
using task_t = void *;
using mach_vm_address_t = uintptr_t;

constexpr IOReturn kIOReturnSuccess = 0;
constexpr IOReturn kIOReturnNoMemory = -536870211;
constexpr IOReturn kIOReturnBadArgument = -536870206;
constexpr IOReturn kIOReturnUnsupported = -536870201;
constexpr IOReturn kIOReturnIOError = -536870186;

class OSSymbol;
class OSObject {
public:
  virtual ~OSObject() = default;
  virtual void release() { delete this; }
};

#define OSDeclareDefaultStructors(cls)
#define OSDefineMetaClassAndStructors(cls, super)
#define OSDynamicCast(cls, obj) dynamic_cast<cls *>(obj)

class OSData : public OSObject {
  const uint8_t *ptr_;
  size_t len_;
public:
  OSData(const void *p, size_t n) : ptr_(static_cast<const uint8_t *>(p)), len_(n) {}
  size_t getLength() const { return len_; }
  const void *getBytesNoCopy() const { return ptr_; }
};

class IORegistryPlane {};
extern const IORegistryPlane *gIODTPlane;

class IORegistryEntry : public OSObject {
public:
  static IORegistryEntry *fromPath(const char *path, const IORegistryPlane *plane = nullptr);
  virtual OSObject *getProperty(const char *key) const;
};

class IOWorkLoop;
class alignas(8) IOService : public IORegistryEntry {
public:
  bool started = false;
  bool registered = false;
  bool softwareKeysOnly = false;
private:
  uint8_t pad_[0x88 - sizeof(IORegistryEntry) - 8]{};
public:
  virtual bool start(IOService *) { started = true; return true; }
  virtual IOWorkLoop *getWorkLoop() const { return nullptr; }
  virtual IOReturn callPlatformFunction(const OSSymbol *, bool, void *, void *, void *, void *) { return kIOReturnUnsupported; }
  void setProperty(const char *key, bool val);
  void registerService() { registered = true; }
};
''',
    'IOKit/IOMemoryDescriptor.h': r'''#pragma once
#include <IOKit/IOService.h>
#include <algorithm>
#include <cstring>
#include <vector>

enum IODirection : int { kIODirectionNone = 0, kIODirectionIn = 1, kIODirectionOut = 2, kIODirectionInOut = 3 };

class IOMemoryDescriptor : public OSObject {
protected:
  uint8_t *external_ = nullptr;
  std::vector<uint8_t> owned_;
  size_t length_ = 0;
public:
  static IOMemoryDescriptor *withAddressRange(mach_vm_address_t addr, size_t len, int, task_t) {
    auto *d = new IOMemoryDescriptor();
    d->external_ = reinterpret_cast<uint8_t *>(addr);
    d->length_ = len;
    return d;
  }
  size_t getLength() const { return length_; }
  IOReturn prepare() { return kIOReturnSuccess; }
  void complete() {}
  size_t readBytes(size_t offset, void *dst, size_t count) {
    if (offset > length_) return 0;
    size_t n = std::min(count, length_ - offset);
    const uint8_t *base = external_ ? external_ : owned_.data();
    if (n) std::memcpy(dst, base + offset, n);
    return n;
  }
  size_t writeBytes(size_t offset, const void *src, size_t count) {
    if (offset > length_) return 0;
    size_t n = std::min(count, length_ - offset);
    uint8_t *base = external_ ? external_ : owned_.data();
    if (n) std::memcpy(base + offset, src, n);
    return n;
  }
};
''',
    'IOKit/IOBufferMemoryDescriptor.h': r'''#pragma once
#include <IOKit/IOMemoryDescriptor.h>

class IOBufferMemoryDescriptor : public IOMemoryDescriptor {
public:
  static IOBufferMemoryDescriptor *withCapacity(size_t cap, int) {
    auto *d = new IOBufferMemoryDescriptor();
    d->owned_.assign(cap, 0);
    d->length_ = cap;
    return d;
  }
};
''',
    'IOKit/IOLib.h': r'''#pragma once
#include <cstdlib>
#include <cstdint>

inline void *IOMalloc(size_t n) { return std::malloc(n); }
inline void IOFree(void *p, size_t) { std::free(p); }
inline uint64_t mach_absolute_time() { static uint64_t t = 100; t += 25; return t; }
''',
    'IOKit/IODeviceTreeSupport.h': r'''#pragma once
#include <IOKit/IOService.h>
''',
    'kern/task.h': r'''#pragma once
#include <IOKit/IOService.h>
extern task_t kernel_task;
''',
    'corecrypto/cc.h': r'''#pragma once
#include <cstddef>
extern size_t gCcClearLastLen;
extern size_t gCcClearKeyDataCount;
inline void cc_clear(size_t len, void *dst) {
  gCcClearLastLen = len;
  if (len == 40) ++gCcClearKeyDataCount;
  volatile unsigned char *p = static_cast<volatile unsigned char *>(dst);
  while (len--) *p++ = 0;
}
''',
    'libkern/crypto/crypto_internal.h': r'''#pragma once
struct crypto_functions {
  void *ccaes_cbc_encrypt;
  void *ccaes_cbc_decrypt;
};
extern const crypto_functions *g_crypto_funcs;
''',
    'libkern/crypto/aes.h': r'''#pragma once
#include <cstdint>
struct aes_encrypt_ctx { uint32_t rk[60]; int nr; };
struct aes_decrypt_ctx { uint32_t rk[60]; int nr; };
int aes_encrypt_key(const unsigned char *key, int key_len, aes_encrypt_ctx *ctx);
int aes_decrypt_key(const unsigned char *key, int key_len, aes_decrypt_ctx *ctx);
int aes_encrypt_cbc(const unsigned char *in, const unsigned char *iv, unsigned num_blk,
                    unsigned char *out, const aes_encrypt_ctx *ctx);
int aes_decrypt_cbc(const unsigned char *in, const unsigned char *iv, unsigned num_blk,
                    unsigned char *out, const aes_decrypt_ctx *ctx);
''',
    'libkern/crypto/sha2.h': r'''#pragma once
#include <cstddef>
#include <cstdint>
constexpr size_t SHA256_DIGEST_LENGTH = 32;
struct SHA256_CTX {
  uint32_t state[8];
  uint64_t bitcount;
  uint8_t buffer[64];
};
void SHA256_Init(SHA256_CTX *ctx);
void SHA256_Update(SHA256_CTX *ctx, const void *data, size_t len);
void SHA256_Final(unsigned char digest[SHA256_DIGEST_LENGTH], SHA256_CTX *ctx);
''',
}

HARNESS_MAIN = r'''
#include <CommonCrypto/CommonCryptor.h>
#include <CommonCrypto/CommonDigest.h>
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

#include "NativeAES.cpp"

size_t gCcClearLastLen = 0;
size_t gCcClearKeyDataCount = 0;
static_assert(sizeof(IOAESKeyData) == 40, "IOAESKeyData size matches cc_clear probe");

static int dummy_cbc_fn = 1;
static const crypto_functions kCryptoFuncs = { &dummy_cbc_fn, &dummy_cbc_fn };
const crypto_functions *g_crypto_funcs = &kCryptoFuncs;
const IORegistryPlane *gIODTPlane = reinterpret_cast<const IORegistryPlane *>(1);
static int dummy_kernel_task = 1;
task_t kernel_task = &dummy_kernel_task;

static std::vector<uint8_t> gChipIdBytes;
static bool gChosenPresent = true;

IORegistryEntry *IORegistryEntry::fromPath(const char *path, const IORegistryPlane *) {
  if (!gChosenPresent || std::strcmp(path, "/chosen") != 0) return nullptr;
  return new IORegistryEntry();
}

OSObject *IORegistryEntry::getProperty(const char *key) const {
  if (std::strcmp(key, "unique-chip-id") != 0 || gChipIdBytes.empty()) return nullptr;
  return new OSData(gChipIdBytes.data(), gChipIdBytes.size());
}

void IOService::setProperty(const char *key, bool val) {
  if (std::strcmp(key, "NativeAESSoftwareKeysOnly") == 0) softwareKeysOnly = val;
}

const char *IOCryptoAccelerator::getAlgorithmName() { return "AES"; }
bool IOAESAccelerator::start(IOService *p) { return IOService::start(p); }
IOWorkLoop *IOAESAccelerator::getWorkLoop() const { return nullptr; }
IOReturn IOAESAccelerator::callPlatformFunction(const OSSymbol *, bool, void *, void *, void *, void *) { return kIOReturnUnsupported; }
const char *IOAESAccelerator::getAlgorithmName() { return "AES"; }
IOReturn IOAESAccelerator::performAES(void *, void *, task_t, unsigned long long, IOAESIV *, IOAESOperation, IOAESKeyData *, IOAESCompletion, void *) { return kIOReturnUnsupported; }
IOReturn IOAESAccelerator::performAES(IOMemoryDescriptor *, IOMemoryDescriptor *, unsigned long long, IOAESIV *, IOAESOperation, IOAESKeyData *, unsigned long long, unsigned long long, IOAESCompletion, void *) { return kIOReturnUnsupported; }
bool IOAESAccelerator::isKeySupported(unsigned) { return false; }
unsigned IOAESAccelerator::getSupportedOptions() { return 0; }
IOReturn IOAESAccelerator::performAESQuantum(IOAESAcceleratorCommand *) { return kIOReturnUnsupported; }
void IOAESAccelerator::completeAESQuantum(IOAESAcceleratorCommand *) {}
IOReturn IOAESAccelerator::performImmediateAES(IOAESAcceleratorCommand *) { return kIOReturnUnsupported; }
void IOAESAccelerator::disableHardwareKey(unsigned) {}
void IOAESAccelerator::createSpecialKeys() {}
IOReturn IOAESAccelerator::_queueLocked(IOAESAcceleratorCommand *) { return kIOReturnUnsupported; }
void IOAESAccelerator::_startCommand() {}
void IOAESAccelerator::_completeAES(IOAESAcceleratorCommand *) {}

int aes_encrypt_key(const unsigned char *key, int key_len, aes_encrypt_ctx *ctx) {
  if (key_len != 16 && key_len != 24 && key_len != 32) return -1;
  std::memset(ctx, 0, sizeof(*ctx));
  std::memcpy(ctx->rk, key, static_cast<size_t>(key_len));
  ctx->nr = key_len;
  return 0;
}
int aes_decrypt_key(const unsigned char *key, int key_len, aes_decrypt_ctx *ctx) {
  if (key_len != 16 && key_len != 24 && key_len != 32) return -1;
  std::memset(ctx, 0, sizeof(*ctx));
  std::memcpy(ctx->rk, key, static_cast<size_t>(key_len));
  ctx->nr = key_len;
  return 0;
}
int aes_encrypt_cbc(const unsigned char *in, const unsigned char *iv, unsigned num_blk,
                    unsigned char *out, const aes_encrypt_ctx *ctx) {
  size_t moved = 0;
  CCCryptorStatus st = CCCrypt(kCCEncrypt, kCCAlgorithmAES, 0, ctx->rk, static_cast<size_t>(ctx->nr),
                               iv, in, static_cast<size_t>(num_blk) * 16, out, static_cast<size_t>(num_blk) * 16, &moved);
  return st == kCCSuccess && moved == static_cast<size_t>(num_blk) * 16 ? 0 : -1;
}
int aes_decrypt_cbc(const unsigned char *in, const unsigned char *iv, unsigned num_blk,
                    unsigned char *out, const aes_decrypt_ctx *ctx) {
  size_t moved = 0;
  CCCryptorStatus st = CCCrypt(kCCDecrypt, kCCAlgorithmAES, 0, ctx->rk, static_cast<size_t>(ctx->nr),
                               iv, in, static_cast<size_t>(num_blk) * 16, out, static_cast<size_t>(num_blk) * 16, &moved);
  return st == kCCSuccess && moved == static_cast<size_t>(num_blk) * 16 ? 0 : -1;
}

static_assert(sizeof(CC_SHA256_CTX) <= 128, "CC_SHA256 fits");
void SHA256_Init(SHA256_CTX *ctx) {
  auto *cc = reinterpret_cast<CC_SHA256_CTX *>(ctx);
  CC_SHA256_Init(cc);
}
void SHA256_Update(SHA256_CTX *ctx, const void *data, size_t len) {
  auto *cc = reinterpret_cast<CC_SHA256_CTX *>(ctx);
  CC_SHA256_Update(cc, data, static_cast<CC_LONG>(len));
}
void SHA256_Final(unsigned char digest[SHA256_DIGEST_LENGTH], SHA256_CTX *ctx) {
  auto *cc = reinterpret_cast<CC_SHA256_CTX *>(ctx);
  CC_SHA256_Final(digest, cc);
}

static void setChipU64(uint64_t v) {
  gChosenPresent = true;
  gChipIdBytes.resize(8);
  std::memcpy(gChipIdBytes.data(), &v, 8);
}

int main() {
  auto *provider = new NativeAES();
  IOService dummyProvider;
  assert(provider->start(&dummyProvider));
  assert(native_aes_kat_status == 1);
  assert(native_aes_registered == 1);
  assert(native_aes_last_unsupported_selector == 0);
  assert(provider->softwareKeysOnly);

  // Selector support matrix without unique-chip-id: derived selectors stay unsupported
  assert(provider->isKeySupported(0));
  assert(!provider->isKeySupported(0x899));
  assert(!provider->isKeySupported(0x8a4));
  assert(!provider->isKeySupported(0x8a1));
  assert(!provider->isKeySupported(1000));
  assert(!provider->isKeySupported(1001));
  assert(!provider->isKeySupported(2000));
  assert(!provider->isKeySupported(2001));

  // Valid non-zero chip ID enables 0x899/0x8a4 capability reporting and derivation
  const uint64_t kChip = 0x1122334455667788ULL;
  setChipU64(kChip);
  assert(provider->isKeySupported(0x899));
  assert(provider->isKeySupported(0x8a4));
  assert(!provider->isKeySupported(0x8a1));
  std::vector<uint8_t> plain(4160), cipher899(4160), roundtrip(4160), cipher8a4(4160);
  for (size_t i = 0; i < plain.size(); ++i) plain[i] = static_cast<uint8_t>((i * 37 + 11) & 0xff);

  IOAESIV iv = {}, ivOrig = {};
  for (unsigned i = 0; i < 16; ++i) ivOrig.bytes[i] = static_cast<unsigned char>(0xa0 + i);
  iv = ivOrig;

  IOAESKeyData key899 = {};
  key899.bits = 128;
  key899.selector = 0x899;
  uint32_t before899 = native_aes_fairplay_key_uses;
  assert(provider->performAES(plain.data(), cipher899.data(), kernel_task, plain.size(),
                              &iv, IOAESEncrypt, &key899, nullptr, nullptr) == kIOReturnSuccess);
  assert(native_aes_fairplay_key_uses == before899 + 1);
  assert(std::memcmp(iv.bytes, cipher899.data() + plain.size() - 16, 16) == 0);

  // Verify exact expected key formula: SHA256("UniXNU software AES key 0x899\0" || le64(chip))[0:16]
  unsigned char expectedDigest899[32];
  {
    CC_SHA256_CTX cctx;
    CC_SHA256_Init(&cctx);
    const char label899[] = "UniXNU software AES key 0x899";
    CC_SHA256_Update(&cctx, label899, sizeof(label899));
    CC_SHA256_Update(&cctx, &kChip, sizeof(kChip));
    CC_SHA256_Final(expectedDigest899, &cctx);
  }
  std::vector<uint8_t> refCipher899(plain.size());
  size_t moved = 0;
  assert(CCCrypt(kCCEncrypt, kCCAlgorithmAES, 0, expectedDigest899, 16, ivOrig.bytes,
                 plain.data(), plain.size(), refCipher899.data(), refCipher899.size(), &moved) == kCCSuccess);
  assert(cipher899 == refCipher899);

  // Decrypt roundtrip with 0x899
  iv = ivOrig;
  assert(provider->performAES(cipher899.data(), roundtrip.data(), kernel_task, plain.size(),
                              &iv, IOAESDecrypt, &key899, nullptr, nullptr) == kIOReturnSuccess);
  assert(roundtrip == plain);
  assert(native_aes_fairplay_key_uses == before899 + 2);

  // Verify 0x8a4 regression compatibility & domain separation against 0x899
  IOAESKeyData key8a4 = {};
  key8a4.bits = 128;
  key8a4.selector = 0x8a4;
  iv = ivOrig;
  uint32_t before8a4 = native_aes_nonce_key_uses;
  assert(provider->performAES(plain.data(), cipher8a4.data(), kernel_task, plain.size(),
                              &iv, IOAESEncrypt, &key8a4, nullptr, nullptr) == kIOReturnSuccess);
  assert(native_aes_nonce_key_uses == before8a4 + 1);
  assert(cipher8a4 != cipher899);

  unsigned char expectedDigest8a4[32];
  {
    CC_SHA256_CTX cctx;
    CC_SHA256_Init(&cctx);
    const char label8a4[] = "UniXNU software AES key 0x8a4";
    CC_SHA256_Update(&cctx, label8a4, sizeof(label8a4));
    CC_SHA256_Update(&cctx, &kChip, sizeof(kChip));
    CC_SHA256_Final(expectedDigest8a4, &cctx);
  }
  std::vector<uint8_t> refCipher8a4(plain.size());
  assert(CCCrypt(kCCEncrypt, kCCAlgorithmAES, 0, expectedDigest8a4, 16, ivOrig.bytes,
                 plain.data(), plain.size(), refCipher8a4.data(), refCipher8a4.size(), &moved) == kCCSuccess);
  assert(cipher8a4 == refCipher8a4);

  // Review Focus #1: zero or short or missing unique-chip-id must refuse 0x899 and report unsupported
  std::vector<uint8_t> untouched(64, 0x5a);
  const std::vector<uint8_t> sentinel(64, 0x5a);
  setChipU64(0);
  assert(!provider->isKeySupported(0x899));
  assert(!provider->isKeySupported(0x8a4));
  uint32_t unsupBefore = native_aes_unsupported_key;
  native_aes_last_unsupported_selector = 0;
  iv = ivOrig;
  assert(provider->performAES(plain.data(), untouched.data(), kernel_task, 64,
                              &iv, IOAESEncrypt, &key899, nullptr, nullptr) == kIOReturnUnsupported);
  assert(native_aes_unsupported_key == unsupBefore + 1);
  assert(native_aes_last_unsupported_selector == 0x899);
  assert(untouched == sentinel);

  gChipIdBytes.assign(4, 0x11); // < 8 bytes
  assert(!provider->isKeySupported(0x899));
  assert(provider->performAES(plain.data(), untouched.data(), kernel_task, 64,
                              &iv, IOAESEncrypt, &key899, nullptr, nullptr) == kIOReturnUnsupported);
  assert(native_aes_unsupported_key == unsupBefore + 2);
  assert(native_aes_last_unsupported_selector == 0x899);

  gChosenPresent = false;
  assert(!provider->isKeySupported(0x899));
  assert(provider->performAES(plain.data(), untouched.data(), kernel_task, 64,
                              &iv, IOAESEncrypt, &key899, nullptr, nullptr) == kIOReturnUnsupported);
  assert(native_aes_unsupported_key == unsupBefore + 3);
  assert(native_aes_last_unsupported_selector == 0x899);

  // Early-return error path after deriving 0x899 must still scrub derived key on stack
  setChipU64(kChip);
  auto *inDesc = IOMemoryDescriptor::withAddressRange(reinterpret_cast<mach_vm_address_t>(plain.data()), 64, kIODirectionOut, kernel_task);
  auto *outDesc = IOMemoryDescriptor::withAddressRange(reinterpret_cast<mach_vm_address_t>(untouched.data()), 64, kIODirectionIn, kernel_task);
  size_t clearsBefore = gCcClearKeyDataCount;
  assert(provider->performAES(inDesc, outDesc, 64, &iv, IOAESEncrypt, &key899, 128, 0, nullptr, nullptr) == kIOReturnBadArgument);
  assert(gCcClearKeyDataCount > clearsBefore);
  inDesc->release();
  outDesc->release();

  // Review Focus #2: 0x899 with non-128-bit length (bits = 256) must fail with kIOReturnUnsupported
  setChipU64(kChip);
  IOAESKeyData wide899 = {};
  wide899.bits = 256;
  wide899.selector = 0x899;
  native_aes_last_unsupported_selector = 0;
  assert(provider->performAES(plain.data(), untouched.data(), kernel_task, 64,
                              &iv, IOAESEncrypt, &wide899, nullptr, nullptr) == kIOReturnUnsupported);
  assert(native_aes_last_unsupported_selector == 0x899);
  assert(untouched == sentinel);

  // GID1 (0x8a1 = 2209) and raw UID (2000) must stay rejected and record selector
  IOAESKeyData gidKey = {};
  gidKey.bits = 128;
  gidKey.selector = 0x8a1;
  assert(provider->performAES(plain.data(), untouched.data(), kernel_task, 64,
                              &iv, IOAESEncrypt, &gidKey, nullptr, nullptr) == kIOReturnUnsupported);
  assert(native_aes_last_unsupported_selector == 0x8a1);
  assert(untouched == sentinel);

  gidKey.selector = 2000;
  assert(provider->performAES(plain.data(), untouched.data(), kernel_task, 64,
                              &iv, IOAESEncrypt, &gidKey, nullptr, nullptr) == kIOReturnUnsupported);
  assert(native_aes_last_unsupported_selector == 2000);
  assert(untouched == sentinel);

  provider->release();
  std::puts("PASS: SoftwareAES 0x899/0x8a4 selectors and unsupported telemetry");
  return 0;
}
'''


class SoftwareAesSelectorTests(unittest.TestCase):
    def test_0x899_derivation_and_unsupported_selector_telemetry(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for rel, content in HARNESS_HEADERS.items():
                target = tmp_path / 'include' / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            harness_cpp = tmp_path / 'harness.cpp'
            harness_cpp.write_text(HARNESS_MAIN)
            exe = tmp_path / 'software-aes-test'
            cmd = [
                'clang++', '-std=c++17', '-O1', '-g',
                '-Wall', '-Wextra', '-Werror', '-Wno-unused-private-field',
                '-fsanitize=address,undefined',
                '-DNATIVE_AES_DARWIN26=1',
                '-I', str(tmp_path / 'include'),
                '-I', str(AES_DIR),
                str(harness_cpp),
                '-o', str(exe),
            ]
            build = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, f'compile failed:\n{build.stderr}')
            run = subprocess.run([str(exe)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, f'run failed:\n{run.stdout}\n{run.stderr}')
            self.assertIn('PASS: SoftwareAES 0x899/0x8a4 selectors', run.stdout)


if __name__ == '__main__':
    unittest.main()
