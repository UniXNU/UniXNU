# 构建内核

内核步骤从 Apple XNU 源码构建，并打上 UniXNU 补丁，然后与原始 kernelcache 预链接。

## 源码与构建树

| 路径 | 内容 |
| --- | --- |
| `out/<board>/tree/refer/xnu` | 固定版本的 XNU 源码 |
| `out/<board>/tree/.cache/xnu-work` | 应用补丁的工作克隆 |
| `out/<board>/tree/build/xnu/ios-obj` | 目标文件和编译命令记录 |
| `out/<board>/tree/build/xnu/ios-sym` | 符号 |
| `out/<board>/tree/build/xnu/ios-dst` | 安装头文件 |
| `out/<board>/tree/.cache/fakeroot` | 内核 SDK 根 |
| `out/<board>/tree/.cache/firmware` | 设备专有输入，链接自设备仓库 |
| `out/<board>/kernel/kernel.macho` | 预链接内核 |

源码版本来自 `feeds.toml`：

```toml
[[source]]
name = "xnu"
kind = "refer"
git = "https://github.com/apple-oss-distributions/xnu.git"
ref = "xnu-10063.141.1"
commit = "d8b80295118ef25ac3a784134bcf95cd8e88109f"
darwin = "23.6.0"
version = "10063.141.1"
driverkit_tag = "xnu-10063.121.3"
trustcache_tag = "xnu-8796.101.5"
```

`unixnu build kernel` 把这些值作为 `UNIXNU_XNU_TAG`、`UNIXNU_XNU_COMMIT`、`UNIXNU_XNU_DARWIN`、`UNIXNU_XNU_VERSION`、`UNIXNU_DRIVERKIT_TAG` 和 `UNIXNU_TRUSTCACHE_TAG` 传给 `scripts/build-xnu-4k-baseline.sh`。

内核参考源码还固定了 `libpthread`（`libpthread-519.120.4`）和 `corecrypto-2023`（commit `11fba65`）。源码提供者按 XNU 编译记录构建。

构建目标：

```
SDKROOT=iphoneos
ARCH_CONFIGS=ARM64
MACHINE_CONFIGS=BCM2837
KERNEL_CONFIGS=DEVELOPMENT
ARM64_LINK_ADDR=0xfffffff007004000
ARM64_PLKSEG_ADDR=0xfffffff004004000
DEPLOYMENT_TARGET_FLAGS="-miphoneos-version-min=17.0 -DXNU_TARGET_OS_IOS"
```

`BCM2837` 携带 4 KiB 页布局。内核仍以 iOS 17 为目标，以匹配 iPadOS kernelcache 的预链接 ABI。

## defconfig 开关

每个 `CONFIG_XNU_<NAME>` 变成构建环境中的 `XNU_<NAME>`。`y` 变成 `1`，`n` 变成 `0`，字符串按文本传入，字符串中的 `{tree}` 替换为构建树路径。

| 开关 | 作用 | 静态库 |
| --- | --- | --- |
| `XNU_SOURCE_CORECRYPTO14` | 构建并链接源码 corecrypto | `build/corecrypto-2023/libcorecrypto_kernel_noasm-namespaced.a` |
| `XNU_SOURCE_PTHREAD` | 构建并注册源码 pthread | `build/libpthread-kernel/libpthread_kernel.a` |
| `XNU_ARM_DT_PLATFORM` | 链接 Apple 格式设备树平台专家 | `build/armdt-platform/libArmDTPlatform.a` |
| `XNU_ARMVIRT_PLATFORM` | 链接 QEMU virt 平台专家 | `build/armvirt-platform/libArmVirtPlatform.a` |
| `XNU_ARMCPU` | 链接 CPU 与中断控制器 | `build/armcpu/libArmCpu.a` |
| `XNU_NATIVE_UFS` | 链接 UFS 存储驱动 | `build/native-ufs/libNativeUfs.a` |
| `XNU_NATIVE_AES` | 链接 AES 加速器驱动 | `build/native-aes/libNativeAES.a` |
| `XNU_NATIVE_VIRTIO_BLOCK` | 链接 VirtIO 块驱动 | `XNU_NATIVE_VIRTIO_BLOCK_ARCHIVE` 或 `build/native-virtio-block/libNativeVirtioBlock.a` |
| `XNU_NATIVE_RAM_BLOCK` | 链接 RAM 块驱动 | `build/native-ram-block/libNativeRamBlock.a` |
| `XNU_NATIVE_VIRTIO_CONSOLE` | 链接 VirtIO 控制台 | `build/native-virtio-console/libNativeVirtioConsole.a` |
| `XNU_NATIVE_MOBILE_DISPLAY` | 链接移动显示驱动 | `build/native-mobile-display/libNativeMobileDisplay.late.a` |
| `XNU_NATIVE_LEGACY_DISPLAY` | 链接旧式显示驱动 | `build/native-legacy-display/libNativeLegacyDisplay.late.a` |
| `XNU_NATIVE_ADRENO` | 链接 Adreno GPU 驱动 | `build/native-adreno/libNativeAdreno.a` |
| `XNU_NATIVE_OFFLINE_GPU` | 链接离线 GPU broker | `build/native-offline-gpu/libNativeOfflineGPU.late.a` |
| `XNU_VERIFIED_ROOT_PROBE` | 链接 verified root | `XNU_VERIFIED_ROOT_ARCHIVE` 或 `build/verified-root-xnu/libVerifiedRootProbe.a` |
| `XNU_NATIVE_CS_HASH_CACHE` | 从已验证 16 KiB 块派生 4 KiB 签名哈希 | 无 |
| `XNU_NATIVE_ARCH_TIMER` | 使用架构定时器入口 | 无 |
| `XNU_NATIVE_PAN` | 启用 ARMv8.1 PAN | 无 |
| `XNU_DT_PANIC_REGION` | 从设备树读取 panic 区域 | 无 |
| `XNU_TRUST_CACHE_RUNTIME` | 初始化 trust cache 运行时 | 无 |
| `XNU_BOOT_PROGRESS` | 加入启动进度层 | `build/boot-progress/libBootProgress.a` |
| `XNU_SOURCE_MOCKFS` | 加入 mockfs 测试文件 | `build/mockfs-fixture/libmockfs_fixture.a` |

`board.toml` 的 `[kernel] archives` 按顺序列出静态库脚本。每个条目是构建树中的脚本及其参数。例如：

```toml
[kernel]
defconfig = "sheng_defconfig"
archives = [
  "scripts/build-native-aes-bindings.py",
  "scripts/build-libpthread-kernel.py",
  "scripts/build-corecrypto-14.py",
  "scripts/build-corecrypto-14.py --namespace",
]
```

`unixnu build kernel` 在编译记录存在后运行这些脚本，然后链接内核。条目按顺序执行，依赖另一个脚本输出的条目排在它后面。没有脚本生成的静态库需要放入构建树。配置用 `CONFIG_XNU_BUILD_ARCHIVES=y` 选择运行；bootstrap pass 和 first-console 配置不设置该值。

脚本通过 `scripts/xnu_symbols.py` 读取符号名。它使用已记录的 checkpoint 内核，或 `build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/link.filelist` 中的目标文件以及 `all-alias.exp` 中的别名。新构建树因此只需要一轮生成编译记录的内核构建，静态库输出也不会与上一次链接的内核冲突。

内核步骤还会在静态库脚本运行前，把公开的 `IOStorageFamily` 头文件放到 `build/storage-abi/include`。

`build-native-aes-bindings.py` 和 `build-native-adreno-accelerator.py` 在原始硬件证据缺失时使用 `scripts/data/` 中记录的审计结果。记录的地址属于 `board.toml` 固定的 kernelcache。

## 构建顺序

1. `unixnu fetch` 克隆 XNU、libpthread、corecrypto-2023 和 Apple 参考源码。
2. `unixnu build kernel` 应用补丁并恢复缺失头文件。
3. 编译记录不存在时，先运行一次 XNU 生成记录。该轮可以在链接前停止。
4. 按 `[kernel] archives` 的顺序运行静态库脚本。
5. 构建并链接内核，然后与原始 kernelcache 预链接。
6. `unixnu build prelink` 只重做预链接。它会替换上一轮的结果和报告。

预链接内核为 `out/<board>/kernel/kernel.macho`。

预链接读取 `board.toml` 的 `[kernel.prelink]`：

```toml
[kernel.prelink]
tool = "kits/NativePrelink/emit_prelink.py"
kernel = "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf"
kernelcache_sha256 = "..."
slide = "-0x1000000"
early_security_init = "com.apple.driver.AppleMobileFileIntegrity=0xfffffff005ab4ae0"
roots = [
  "com.apple.driver.AppleARMPlatform",
  "com.apple.filesystems.apfs",
]
```

`roots` 列出原生内核使用的原始 kernelcache 组件。`early_security_init` 指定在预链接安全初始化期间运行的组件地址。

## 新增内核开关

1. 在设备 defconfig 中加入 `CONFIG_XNU_<NAME>=y`。
2. 在 `scripts/build-xnu-4k-baseline.sh` 中读取 `XNU_<NAME>`。
3. 用 `EXTRA_MAKE_ARGS+=("<file>.o_CFLAGS_ADD=-DXNU_<NAME>=$VALUE")` 加入目标文件开关。
4. 把构建脚本加入 `[kernel] archives`，再把静态库加入 `KERNEL_EXTRA_ARCHIVES` 和 `KERNEL_ARCHIVE_DEPENDENCIES`。
5. 通过补丁把 personality 加入 `iokit/KernelConfigTables.cpp`。

## 使用已有内核

`unixnu build payload --kernel FILE` 用已有的预链接内核打包，跳过 XNU 构建。

## 下一步

- [4 KiB 页表](/zh/xnu/four-k-page-tables)
- [补丁参考](/zh/xnu/patch-reference)
- [预链接](/zh/concepts/prelink)
