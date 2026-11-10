# Nothing Phone \(2\)（pong）

[Chengdong-Yu/UniXNU-pong](https://github.com/Chengdong-Yu/UniXNU-pong)

<div v-pre>

Nothing Phone \(2\), native iPhone17,2 iOS18.6.2/22G100 Darwin24 arm64e/PAC

源记录: [porting.toml](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/porting.toml), `f85fbe118d1ec79fc776117408e4ca0ecfb73ea2`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `implemented` |
| [固件与启动](#firmware) | `implemented` |
| [CPU 与中断](#cpu) | `implemented` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [网络](#network) | `implemented` |
| [音频](#audio) | `implemented` |
| [电源](#power) | `implemented` |
| [镜像组装](#packaging) | `implemented` |
| [诊断](#diagnostics) | `implemented` |

## 配置 {#configuration}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- Native22G100board/profile/arm64e source selection
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [Native22G100board/profile/arm64e source selection; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 固件与启动 {#firmware}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- PongUEFI and original signed Qualcomm firmware integration
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [PongUEFI and original signed Qualcomm firmware integration; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## CPU 与中断 {#cpu}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- EightCPU PSCI/GIC and native timer
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [EightCPU PSCI/GIC and native timer; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 内存与 DMA {#memory}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- Native4KiB ownership and physical DMA translation
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [Native4KiB ownership and physical DMA translation; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 存储与根卷 {#storage}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- NativeUFS/APFS and128GB writableData
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [NativeUFS/APFS and128GB writableData; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 显示 {#display}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- Native brightness and hardware display output
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [Native brightness and hardware display output; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 输入 {#input}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- GoodixIRQ and nativeHID/button integration
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [GoodixIRQ and nativeHID/button integration; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## GPU {#gpu}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- A730/Turnip/Metal hardware rendering and per-processVA
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [A730/Turnip/Metal hardware rendering and per-processVA; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 网络 {#network}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- PongQCA6490 nativeWiFi; actual cellular qualification separate
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [PongQCA6490 nativeWiFi; actual cellular qualification separate; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 音频 {#audio}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- AudioReach/TFA9873 nativeIOAudio2 and software decoding
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [AudioReach/TFA9873 nativeIOAudio2 and software decoding; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 电源 {#power}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- Native battery/externalpower and AW20036Glyph
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [Native battery/externalpower and AW20036Glyph; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 镜像组装 {#packaging}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- Native kernel/bindings/closure/boot pipeline
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [Native kernel/bindings/closure/boot pipeline; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## 诊断 {#diagnostics}

`implemented`

组件: `PongPlatform24`.

### 硬件与依赖

- PongSM8475 actualDT/firmware and native22G100 originalABI

### 配置

- board.toml selectsios-18.6.2-22G100 andarm64e

### 操作步骤

- RealSIM/IPA/WAN/QMI status with no fabricated networking state
- Build native source and qualify hardware results separately

### 开发经验

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### 完成条件

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### 当前范围

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### 下一步

- Complete native cellular update-state and actual WANIP qualification

### 证据

- `source`: [RealSIM/IPA/WAN/QMI status with no fabricated networking state; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

</div>
