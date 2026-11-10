# Nothing Phone \(2\) \(pong\)

[Chengdong-Yu/UniXNU-pong](https://github.com/Chengdong-Yu/UniXNU-pong)

<div v-pre>

Nothing Phone \(2\), native iPhone17,2 iOS18.6.2/22G100 Darwin24 arm64e/PAC

Source record: [porting.toml](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/porting.toml), `f85fbe118d1ec79fc776117408e4ca0ecfb73ea2`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `implemented` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `implemented` |
| [Audio](#audio) | `implemented` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `implemented` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- Native22G100board/profile/arm64e source selection
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [Native22G100board/profile/arm64e source selection; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Firmware and boot {#firmware}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- PongUEFI and original signed Qualcomm firmware integration
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [PongUEFI and original signed Qualcomm firmware integration; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## CPU and interrupts {#cpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- EightCPU PSCI/GIC and native timer
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [EightCPU PSCI/GIC and native timer; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Memory and DMA {#memory}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- Native4KiB ownership and physical DMA translation
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [Native4KiB ownership and physical DMA translation; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Storage and root {#storage}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- NativeUFS/APFS and128GB writableData
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [NativeUFS/APFS and128GB writableData; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Display {#display}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- Native brightness and hardware display output
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [Native brightness and hardware display output; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Input {#input}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- GoodixIRQ and nativeHID/button integration
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [GoodixIRQ and nativeHID/button integration; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## GPU {#gpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- A730/Turnip/Metal hardware rendering and per-processVA
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [A730/Turnip/Metal hardware rendering and per-processVA; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Network {#network}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- PongQCA6490 nativeWiFi; actual cellular qualification separate
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [PongQCA6490 nativeWiFi; actual cellular qualification separate; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Audio {#audio}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- AudioReach/TFA9873 nativeIOAudio2 and software decoding
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [AudioReach/TFA9873 nativeIOAudio2 and software decoding; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Power {#power}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- Native battery/externalpower and AW20036Glyph
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [Native battery/externalpower and AW20036Glyph; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Image assembly {#packaging}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- Native kernel/bindings/closure/boot pipeline
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [Native kernel/bindings/closure/boot pipeline; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

## Diagnostics {#diagnostics}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- PongSM8475 actualDT/firmware and native22G100 originalABI

### Configuration

- board.toml selectsios-18.6.2-22G100 andarm64e

### Procedure

- RealSIM/IPA/WAN/QMI status with no fabricated networking state
- Build native source and qualify hardware results separately

### Development findings

- Current native source compiles; realIPA init and rule cache are online; iOS cellular update status and IP traffic remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Remaining cellular registration, slow frames, audio resume and preview paths require device qualification

### Next action

- Complete native cellular update-state and actual WANIP qualification

### Evidence

- `source`: [RealSIM/IPA/WAN/QMI status with no fabricated networking state; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/f85fbe118d1ec79fc776117408e4ca0ecfb73ea2/kits/PongPlatform24/NATIVE_IOS18E.md)

</div>
