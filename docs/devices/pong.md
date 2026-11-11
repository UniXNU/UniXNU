# Nothing Phone \(2\) \(pong\)

[Chengdong-Yu/UniXNU-pong](https://github.com/Chengdong-Yu/UniXNU-pong)

<div v-pre>

Nothing Phone \(2\), native iPhone17,2 iOS18.6.2/22G100 Darwin24 arm64e/PAC

Source record: [porting.toml](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/porting.toml), `3b0cf3ee4764cda6d01e69f30d1b78344b0994c5`.

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
| [native-root-source](#native-root-source) | `host-verified` |

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [Native22G100board/profile/arm64e source selection; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [PongUEFI and original signed Qualcomm firmware integration; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [EightCPU PSCI/GIC and native timer; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [Native4KiB ownership and physical DMA translation; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [NativeUFS/APFS and128GB writableData; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [Native brightness and hardware display output; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [GoodixIRQ and nativeHID/button integration; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [A730/Turnip/Metal hardware rendering and per-processVA; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [PongQCA6490 nativeWiFi; actual cellular qualification separate; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [AudioReach/TFA9873 nativeIOAudio2 and software decoding; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [Native battery/externalpower and AW20036Glyph; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [Native kernel/bindings/closure/boot pipeline; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

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

- Native source compiles; real SIM identities, network registration, IPv4/IPv6 WAN and cellular-only HTTP200 are observed; native calls/SMS and call audio remain incomplete

### Completion criteria

- Matching native kernel/runtime boots
- Actual interface functions observed and remaining limits recorded

### Current limits

- Native ABI/firmware inputs remain local
- Native calls/SMS, microphone PCM, receiver call audio, slow-frame and preview scenarios remain under qualification

### Next action

- Repair native call policy and qualify actual calls/SMS and audio routes

### Evidence

- `source`: [RealSIM/IPA/WAN/QMI status with no fabricated networking state; seeREADME for actual device evidence and limits](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/kits/PongPlatform24/NATIVE_IOS18E.md)

## native-root-source {#native-root-source}

`host-verified`

Components: `PongPlatform24`.

### Hardware and dependencies

- Native22G100 original ABI and Pong private firmware remain local

### Configuration

- Root source checkout with pinned driver gitlinks; no copied native-source overlay

### Procedure

- Compile native bootstrap/UI and complete source kernel from root
- Read requested REC files using native read-only APFS
- Temporary boot matching runtime without automatic restart

### Development findings

- services302 new bootstrap/input compiled and ran original launchd; real input reports observed
- Native read-only APFS obtained actual UID/GID and requested baseband files without a full-system capture

### Completion criteria

- Root scripts consume root sources and driver submodules
- Existing component licenses remain in their repositories; removed legacy sources are no longer linked

### Current limits

- Native VoLTE support remains false although physical IMS registration is real; calls/SMS are not qualified
- The source IOHIDDevice private ABI from upstream iOS17 is not reused on22G100 arm64e

### Next action

- Repair the native call policy and actual voice/SMS path

### Evidence

- `host`: [Full native22G100 arm64e kernel link returned0 from root sources and pinned driver submodules; native bootstrap/UI compilation returned0](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/migration/ios18e/services302-native-bootstrap-input-filesystem.md)
  Command: <code>scripts/build-pong-ios18e.py --phase full --configuration DEVELOPMENT --chained --optimize-size with local ABI/firmware inputs</code>. Revision: `ddc0a02d6d940f0e79ee4a598970cf2980b676f3`.
- `device`: [Original launchd, actual input and physical IMS registration observed; native calls/SMS still incomplete](https://github.com/Chengdong-Yu/UniXNU-pong/blob/3b0cf3ee4764cda6d01e69f30d1b78344b0994c5/migration/ios18e/services302-native-bootstrap-input-filesystem.md)
  Command: <code>fastboot boot services300/boot-final/pong-xnu-initial.img with services302 runtime; two bounded USB captures</code>. Revision: `ddc0a02d6d940f0e79ee4a598970cf2980b676f3`.

</div>
