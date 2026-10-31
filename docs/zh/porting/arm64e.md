# arm64e OS 配置

**仅适用于受支持的设备。** 只有满足全部[要求](#requirements)并列入[受支持设备](#supported-devices)的设备才能使用本方法。
其他设备使用 arm64 配置 `ipados-17.7.11-21H461` 和常规[移植步骤](/zh/porting/steps)。

iPadOS 18 及以后版本只提供 arm64e 用户空间，因此 arm64 是最后的退路，其终点是 iOS 17 和 iPadOS 18。
arm64e 配置以指针认证（PAC）编译 XNU，并链接目标 kernelcache 中的原版 arm64e kext。

新移植应选择满足下列要求的设备。优先使用 iOS 或 iPadOS 27 配置：其驱动、补丁和构建配方
处于持续维护中，本仓库的每个驱动和优化都同时面向 17 和 27 维护，只靠构建参数选择。

## 要求 {#requirements}

| 要求 | 检查方法 |
| --- | --- |
| 每个启用的 CPU 实现 FEAT_PAuth，包括地址密钥和通用密钥 | `ID_AA64ISAR1_EL1` 的 APA 或 API、GPA 或 GPI 非零；或 `ID_AA64ISAR2_EL1` 的 APA3 和 GPA3 非零 |
| XNU 运行在 EL1，并能写五组密钥寄存器 | 在 EL1 写 `APIAKey`、`APIBKey`、`APDAKey`、`APDBKey`、`APGAKey` 不产生陷入 |
| PAC 指令在 EL1 和 EL0 不陷入 | 每个核上 `PACIA` 改变指针，`AUTIA` 还原指针 |
| 已有 SoC 支持 | SoC 仓库列在 [SoC 支持](/zh/porting/soc-support) 中 |
| 原生 4 KiB 一级翻译 | 与 arm64 配置相同，见[4 KiB 页](/zh/xnu/four-k-page-tables) |

清除 `HCR_EL2.APK` 或 `HCR_EL2.API` 的虚拟机监控程序会使这些访问陷入。
每项检查结果记录在设备的 `porting.toml` 中。

## 受支持设备 {#supported-devices}

| 设备 | SoC | OS 配置 | 状态 |
| --- | --- | --- | --- |
| sheng | SM8550 | `ipados-27.0.1-24A446` | 开发中 |
| sheng | SM8550 | `ipados-26.5.2-23F84` | 保留为其早期 arm64e 配置 |

## 配置结构

| 位置 | 内容 |
| --- | --- |
| `profiles/arch/arm64e` | arm64e 编译配置、PAC 密钥管理和 XNU 补丁系列 |
| `profiles/os/ipados-27.0.1-24A446` | XNU `12377.121.6` 加 Darwin 26 调用、iPadOS 27.0.1 IPSW 固定版本、预链接根组件和 OS 补丁 |
| `profiles/os/ipados-26.5.2-23F84` | 先前的 arm64e 配置，同一 XNU 修订与各自的 IPSW 固定版本 |

OS 配置用 `[os] arch = "arm64e"` 选择架构。没有该项的配置使用 `profiles/arch/arm64`。
两种架构使用相同的组件，arm64e 构建把它们编译为 arm64e。

## 指针认证

arm64e 镜像把认证指针存为链式修复，只记录密钥和混淆值。dyld 在加载镜像时为用户指针签名，
XNU 在早期启动时为 kernel collection 的指针签名。签名都不在设备以外生成，
所以 CPU 的 PAC 算法不需要与 Apple 相同。

公开 XNU 源码只在 `osfmk/arm64/pac_asm.h` 中为半虚拟化的 `VMAPPLE` 平台设置密钥。
arm64e 配置为 ARMv8.3 密钥寄存器提供原生的密钥设置。

ARMv8.3 的 EL0 和 EL1 共用同一组密钥寄存器。当前配置每次启动生成一组随机密钥，
写入每个 CPU，并打开 `SCTLR_EL1` 的 EnIA、EnIB、EnDA、EnDB。
内核和所有进程共用这组密钥，所以 PAC 不在进程之间做隔离。

## CPU 特性

XNU 只通过 `hw.optional` sysctl 和 commpage 能力字公布 CPU 实际具备的特性。
SM8550 没有 SME。iPadOS 26.5.2 的 dyld cache 在以 SME 命名的函数中包含 SME 代码。

## 操作步骤

1. 在每个启用的 CPU 上完成[要求](#requirements)中的检查并记录结果。
2. 在设备配置中设置 `board.os_profile = "ipados-27.0.1-24A446"`，或对单次运行给 `./unixnu` 传 `--os 27`。
3. 运行 `./unixnu fetch` 和 `./unixnu status --json`，确认 arm64e 配置、XNU 版本和补丁顺序。
4. 按[构建](/zh/building)依次构建内核、package、固件、payload、userdata 和启动镜像。
5. 按[启动验证顺序](/zh/porting/bring-up)记录每个检查点。

## 事实与待确认问题

事实：

- iPad17,1 至 iPad17,4 的 iPadOS 26.5.2 kernelcache 报告 `xnu-12377.122.8`，最接近的公开源码是 `xnu-12377.121.6`。
- 公开的 `xnu-12377.121.6` 源码在 `osfmk/arm/pmap` 中保留非 SPTM 的 pmap。
- arm64e 内核使用 `BCM2837` 机器配置和非 SPTM 的 pmap 编译，并关闭 Apple CPU 计数器。
- iPadOS 26.5.2 的 kernelcache 是 `MH_FILESET`，符号表已删除。kext 代码直接跳转到内核，所以 iPadOS 17 的 prelink 步骤不适用。

待确认：

- dyld cache 中的 SME 函数可能在运行时按公布的 CPU 特性选择，尚未确认。
