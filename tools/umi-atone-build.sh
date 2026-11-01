#!/bin/bash
# Build tools/umi-atone.c as a static, libc-free aarch64 Linux binary (shim/out/umi-atone).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p shim/out
/opt/homebrew/opt/llvm/bin/clang --target=aarch64-linux-gnu -fuse-ld=lld --ld-path=/opt/homebrew/opt/lld/bin/ld.lld \
    -O2 -ffreestanding -fno-builtin -nostdlib -static -fno-stack-protector -fno-pic -no-pie \
    -Wall -Wextra -o shim/out/umi-atone tools/umi-atone.c
ls -la shim/out/umi-atone
