# Driver repositories

Drivers and libraries have independent repositories. The [component catalog](/reference/components) records their scope, interfaces, dependencies, revisions, build commands, and outputs. SoC and device profiles select canonical IDs. Every maintained driver repository carries the `unixnu` topic.

## Official drivers

These repositories are maintained in the UniXNU organization.

| Driver | Repository | Layer | Page |
| --- | --- | --- | --- |
| Adreno740 | [UniXNU/Adreno740](https://github.com/UniXNU/Adreno740) | XNU GPU | [Adreno740](/drivers/adreno740) |
| AdrenoMetal | [UniXNU/AdrenoMetal](https://github.com/UniXNU/AdrenoMetal) | XNU Metal frontend | [AdrenoMetal](/drivers/adreno-metal) |
| ShengUfs | [UniXNU/ShengUfs](https://github.com/UniXNU/ShengUfs) | XNU storage | [ShengUfs](/drivers/sheng-ufs) |
| ShengHidInput | [UniXNU/ShengHidInput](https://github.com/UniXNU/ShengHidInput) | XNU input | [ShengHidInput](/drivers/sheng-hid-input) |
| RamBlock | [UniXNU/RamBlock](https://github.com/UniXNU/RamBlock) | XNU storage | [RamBlock](/drivers/ram-block) |
| GopFramebuffer | [UniXNU/GopFramebuffer](https://github.com/UniXNU/GopFramebuffer) | XNU display | [GopFramebuffer](/drivers/gop-framebuffer) |
| QcomGeniSpi | [UniXNU/QcomGeniSpi](https://github.com/UniXNU/QcomGeniSpi) | XNU SPI | [QcomGeniSpi](/drivers/qcom-geni-spi) |
| SoftwareAES | [UniXNU/SoftwareAES](https://github.com/UniXNU/SoftwareAES) | XNU crypto | [SoftwareAES](/drivers/software-aes) |
| AppleKeyStoreState | [UniXNU/AppleKeyStoreState](https://github.com/UniXNU/AppleKeyStoreState) | XNU keystore | [AppleKeyStoreState](/drivers/apple-key-store-state) |
| VirtioMmioBlock | [UniXNU/VirtioMmioBlock](https://github.com/UniXNU/VirtioMmioBlock) | XNU storage | [VirtioMmioBlock](/drivers/virtio-mmio-block) |
| VirtioMmioConsole | [UniXNU/VirtioMmioConsole](https://github.com/UniXNU/VirtioMmioConsole) | XNU console | [VirtioMmioConsole](/drivers/virtio-mmio-console) |
| ShengNovatekTouch | [UniXNU/ShengNovatekTouch](https://github.com/UniXNU/ShengNovatekTouch) | XNU touch | [ShengNovatekTouch](/drivers/sheng-novatek-touch) |
| XnuPrelink | [UniXNU/XnuPrelink](https://github.com/UniXNU/XnuPrelink) | Kernel tooling | [XnuPrelink](/drivers/xnu-prelink) |
| Ath12kWifi | [UniXNU/Ath12kWifi](https://github.com/UniXNU/Ath12kWifi) | XNU Wi-Fi | [Ath12kWifi](/drivers/ath12k-wifi) |
| ArmCpu | [UniXNU/ArmCpu](https://github.com/UniXNU/ArmCpu) | XNU CPU and GIC | [ArmCpu](/drivers/arm-cpu) |
| ArmDTPlatform | [UniXNU/ArmDTPlatform](https://github.com/UniXNU/ArmDTPlatform) | XNU platform expert | [ArmDTPlatform](/drivers/arm-dt-platform) |
| ArmVirtPlatform | [UniXNU/ArmVirtPlatform](https://github.com/UniXNU/ArmVirtPlatform) | XNU platform | [ArmVirtPlatform](/drivers/arm-virt-platform) |
| ArmSmmu4K | [UniXNU/ArmSmmu4K](https://github.com/UniXNU/ArmSmmu4K) | XNU SMMU kit | [ArmSmmu4K](/drivers/arm-smmu4k) |
| AirNir | [UniXNU/AirNir](https://github.com/UniXNU/AirNir) | Compiler kit | [AirNir](/drivers/air-nir) |
| AdrenoPM4 | [UniXNU/AdrenoPM4](https://github.com/UniXNU/AdrenoPM4) | GPU command kit | [AdrenoPM4](/drivers/adreno-pm4) |
| AdrenoFirmware | [UniXNU/AdrenoFirmware](https://github.com/UniXNU/AdrenoFirmware) | GPU firmware kit | [AdrenoFirmware](/drivers/adreno-firmware) |
| Sm8550Platform | [UniXNU/UniXNU-sm8550-common](https://github.com/UniXNU/UniXNU-sm8550-common) | SM8550 GPU platform kit | [Sm8550Platform](/drivers/sm8550-platform) |
| DarwinBoot | [UniXNU/DarwinBoot](https://github.com/UniXNU/DarwinBoot) | UEFI loader | [DarwinBoot](/drivers/darwin-boot) |
| VerifiedRoot | [UniXNU/VerifiedRoot](https://github.com/UniXNU/VerifiedRoot) | Root trust tooling | [VerifiedRoot](/drivers/verified-root) |
| ShengPreflight | [UniXNU/ShengPreflight](https://github.com/UniXNU/ShengPreflight) | UEFI preflight | [ShengPreflight](/drivers/sheng-preflight) |

## Community drivers

These repositories are maintained by their owners. They are linked from the device repository that uses them.

| Driver | Device | Repository | Page |
| --- | --- | --- | --- |
| NativeMsdc | Benesse TAB-A04-BR3 (MT8167) | [mouseos/NativeMsdc](https://github.com/mouseos/NativeMsdc) | [NativeMsdc](/drivers/community-native-msdc) |
| NativeAdreno-myron | Redmi K90 Pro Max / Poco F8 Ultra | [zg7681/NativeAdreno-myron](https://github.com/zg7681/NativeAdreno-myron) | [NativeAdreno-myron](/drivers/community-native-adreno-myron) |
| NativeUfs-myron | Redmi K90 Pro Max / Poco F8 Ultra | [zg7681/NativeUfs-myron](https://github.com/zg7681/NativeUfs-myron) | [NativeUfs-myron](/drivers/community-native-ufs-myron) |
| NativeAdreno-fuxi | Xiaomi 13 | [ljhhkx529/NativeAdreno-fuxi](https://github.com/ljhhkx529/NativeAdreno-fuxi) | [NativeAdreno-fuxi](/drivers/community-native-adreno-fuxi) |
| NativeUfs-alioth | Redmi K40 / Poco F3 | [FFT-infra/NativeUfs-alioth](https://github.com/FFT-infra/NativeUfs-alioth) | [NativeUfs-alioth](/drivers/community-native-ufs-alioth) |
| unixnu-nativeufs | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativeufs](https://github.com/RigoLigoRLC/unixnu-nativeufs) | [unixnu-nativeufs](/drivers/community-unixnu-nativeufs) |
| unixnu-nativemobiledisplay | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativemobiledisplay](https://github.com/RigoLigoRLC/unixnu-nativemobiledisplay) | [unixnu-nativemobiledisplay](/drivers/community-unixnu-nativemobiledisplay) |
| unixnu-nativeramblock | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativeramblock](https://github.com/RigoLigoRLC/unixnu-nativeramblock) | [unixnu-nativeramblock](/drivers/community-unixnu-nativeramblock) |
| NativeEmmc | Redmi Note 9 | [Dracen-W/NativeEmmc](https://github.com/Dracen-W/NativeEmmc) | [NativeEmmc](/drivers/community-native-emmc) |
| NativeDwc3 | Xiaomi Pad 5 | [Lux12138/NativeDwc3](https://github.com/Lux12138/NativeDwc3) | [NativeDwc3](/drivers/community-native-dwc3) |
| unixnu-nativefocaltechtouch | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativefocaltechtouch](https://github.com/RigoLigoRLC/unixnu-nativefocaltechtouch) | [unixnu-nativefocaltechtouch](/drivers/community-nativefocaltechtouch) |

## Device forks

These repositories are device forks that track an official driver. They are linked from their device repositories and do not have a separate driver page.

| Device | Driver | Repository |
| --- | --- | --- |
| Sony Xperia 1 II | NativeAdreno | [chardidathing/NativeAdreno](https://github.com/chardidathing/NativeAdreno) |
| Xiaomi Pad 7 | NativeAdreno, NativeMobileDisplay | [Allenwdk/NativeAdreno](https://github.com/Allenwdk/NativeAdreno), [Allenwdk/NativeMobileDisplay](https://github.com/Allenwdk/NativeMobileDisplay) |
| Nothing Phone (3a) | NativeAdreno, NativeUfs | [rootstockos/NativeAdreno](https://github.com/rootstockos/NativeAdreno), [rootstockos/NativeUfs](https://github.com/rootstockos/NativeUfs) |
| OnePlus 6T | NativeAdreno, NativeMetal | [johnpanos/NativeAdreno](https://github.com/johnpanos/NativeAdreno), [johnpanos/NativeMetal](https://github.com/johnpanos/NativeMetal) |
| Xiaomi 13 Pro | NativeUfs | [pubglite55/NativeUfs](https://github.com/pubglite55/NativeUfs) |
| OnePlus 5 | NativeUfs | [lss717/NativeUfs](https://github.com/lss717/NativeUfs) |
| QEMU virt | NativeAdreno, NativeMetal, NativeMobileDisplay, NativeUfs | [xVanTuring/NativeAdreno](https://github.com/xVanTuring/NativeAdreno), [xVanTuring/NativeMetal](https://github.com/xVanTuring/NativeMetal), [xVanTuring/NativeMobileDisplay](https://github.com/xVanTuring/NativeMobileDisplay), [xVanTuring/NativeUfs](https://github.com/xVanTuring/NativeUfs) |
| Benesse TAB-A04-BR3 | NativeMetal | [mouseos/NativeMetal](https://github.com/mouseos/NativeMetal) |
| Unisoc devices | NativeUfs | [N1709/NativeUfs](https://github.com/N1709/NativeUfs) |

## Rules

- One hardware driver per repository.
- SoC and device profiles select catalog components by ID. Feeds and submodules supply additional sources.
- A driver for an official device or the generic stack can be contributed to the UniXNU organization.
- Other drivers stay independently maintained and are linked as submodules.
- Every driver repository carries the `unixnu` topic.
