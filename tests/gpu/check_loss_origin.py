#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check native loss recording without submitting GPU work.

Pass the fully patched tu_knl_darwin.cc selected by the build. This compiles
its production loss/wait-status functions over a fake IOKit transport.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--cxx', default='c++')
    args = parser.parse_args()
    source = args.source.read_text()
    start = source.index('static VkResult\ndw_device_lost_at(')
    end = source.index('/* Waits for a fence', start)
    production = source[start:end]
    assert source.count('vk_device_set_lost(') == 1, 'Unrecorded native device-loss path'
    fixture = r'''
#include <atomic>
#include <cassert>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>
#include <unistd.h>
#define MIN2(a,b) ((a)<(b)?(a):(b))
using VkResult=int; using kern_return_t=int;
constexpr int KERN_SUCCESS=0,kIOReturnTimeout=1,VK_SUCCESS=0,VK_TIMEOUT=2,VK_ERROR_DEVICE_LOST=-4;
constexpr int OS_LOG_DEFAULT=0;
struct darwin_retire_state {uint32_t loss_reported=0;};
struct tu_device {void *darwin_retire; int vk;};
static std::atomic<unsigned> calls{0};
static std::vector<std::string> messages;
static std::vector<std::vector<uint8_t>> records;
static bool accept=true;
static uint32_t p_atomic_cmpxchg(uint32_t *at,uint32_t expected,uint32_t value) {
    __atomic_compare_exchange_n(at,&expected,value,false,__ATOMIC_ACQ_REL,__ATOMIC_ACQUIRE);return expected;
}
static void os_log_error(int,const char *,const char *text) {messages.emplace_back(text);}
static int vk_device_set_lost(int *,const char *,...) {++calls;return VK_ERROR_DEVICE_LOST;}
static bool tu_darwin_frame_diagnostic(uint32_t method,const void *data,uint32_t bytes) {
    assert(method==0x7102 && bytes==120);
    const auto *p=static_cast<const uint8_t *>(data);records.emplace_back(p,p+bytes);return accept;
}
'''
    tests = r'''
static void verifyText(size_t begin,const std::string &text) {
    std::string restored;
    for(size_t i=begin;i<records.size();++i) {
        uint32_t event=0;uint64_t part=99;
        memcpy(&event,records[i].data()+16,4);memcpy(&part,records[i].data()+24,8);
        assert(event==65 && part==i-begin);
        const char *p=reinterpret_cast<const char *>(records[i].data()+32);
        restored.append(p,strnlen(p,88));
    }
    assert(restored==text);
}
int main() {
    setenv("SHENG_GPU_TRACE","1",1);
    darwin_retire_state state{};tu_device device{&state,0};
    assert(dw_status_to_vk(&device,KERN_SUCCESS,"wait fence",17)==VK_SUCCESS);
    assert(dw_status_to_vk(&device,kIOReturnTimeout,"wait fence",17)==VK_TIMEOUT);
    assert(calls==0 && messages.empty() && records.empty());
    assert(dw_status_to_vk(&device,99,"wait fence",17)==VK_ERROR_DEVICE_LOST);
    assert(messages.size()==1 && messages[0].find("wait fence failed: 0x63 fence=17")!=std::string::npos);
    verifyText(0,messages[0]);
    const auto kept=records.size();
    assert(dw_device_lost(&device,"later submit failure")==VK_ERROR_DEVICE_LOST);
    assert(messages.size()==1 && records.size()==kept && calls==2);
    darwin_retire_state concurrent{};tu_device next{&concurrent,0};
    std::vector<std::thread> threads;
    for(unsigned i=0;i<32;++i) threads.emplace_back([&]{assert(dw_device_lost(&next,"concurrent loss")==VK_ERROR_DEVICE_LOST);});
    for(auto &thread:threads)thread.join();
    assert(messages.size()==2 && calls==34);verifyText(kept,messages.back());
    const auto before=records.size();
    darwin_retire_state refused{};tu_device third{&refused,0};accept=false;
    std::string longReason(600,'x');
    assert(dw_device_lost(&third,"%s",longReason.c_str())==VK_ERROR_DEVICE_LOST);
    assert(messages.back().size()<352);verifyText(before,messages.back());
    unsetenv("SHENG_GPU_TRACE");darwin_retire_state quiet{};tu_device fourth{&quiet,0};
    const auto saved=records.size();assert(dw_device_lost(&fourth,"trace disabled")==VK_ERROR_DEVICE_LOST);
    assert(records.size()==saved && messages.size()==4);
    std::puts("PASS timeout classification, first-cause retention, concurrent loss, bounded text and refused transport");
}
'''
    with tempfile.TemporaryDirectory(prefix='gpu-loss-') as name:
        folder = Path(name)
        cpp = folder / 'loss.cpp'
        cpp.write_text(fixture + production + tests)
        binary = folder / 'loss'
        subprocess.run([args.cxx, '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pthread',
                        '-fsanitize=address,undefined', str(cpp), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True, timeout=30)


if __name__ == '__main__':
    main()
