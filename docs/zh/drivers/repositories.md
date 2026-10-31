# 驱动仓库

驱动和库使用独立仓库。[组件目录](/zh/reference/components)记录范围、接口、依赖、版本、构建命令和输出。SoC 与设备配置选择规范 ID。维护中的驱动仓库带有 `unixnu` topic。

## 官方驱动

这些仓库由 UniXNU 组织维护。

| 驱动 | 仓库 | 层 | 页面 |
| --- | --- | --- | --- |
| Adreno740 | [UniXNU/Adreno740](https://github.com/UniXNU/Adreno740) | XNU GPU | [Adreno740](/zh/drivers/adreno740) |
| AdrenoMetal | [UniXNU/AdrenoMetal](https://github.com/UniXNU/AdrenoMetal) | XNU Metal 前端 | [AdrenoMetal](/zh/drivers/adreno-metal) |
| ShengUfs | [UniXNU/ShengUfs](https://github.com/UniXNU/ShengUfs) | XNU 存储 | [ShengUfs](/zh/drivers/sheng-ufs) |
| ShengHidInput | [UniXNU/ShengHidInput](https://github.com/UniXNU/ShengHidInput) | XNU 输入 | [ShengHidInput](/zh/drivers/sheng-hid-input) |
| RamBlock | [UniXNU/RamBlock](https://github.com/UniXNU/RamBlock) | XNU 存储 | [RamBlock](/zh/drivers/ram-block) |
| GopFramebuffer | [UniXNU/GopFramebuffer](https://github.com/UniXNU/GopFramebuffer) | XNU 显示 | [GopFramebuffer](/zh/drivers/gop-framebuffer) |
| QcomGeniSpi | [UniXNU/QcomGeniSpi](https://github.com/UniXNU/QcomGeniSpi) | XNU SPI | [QcomGeniSpi](/zh/drivers/qcom-geni-spi) |
| SoftwareAES | [UniXNU/SoftwareAES](https://github.com/UniXNU/SoftwareAES) | XNU 加密 | [SoftwareAES](/zh/drivers/software-aes) |
| AppleKeyStoreState | [UniXNU/AppleKeyStoreState](https://github.com/UniXNU/AppleKeyStoreState) | XNU keystore | [AppleKeyStoreState](/zh/drivers/apple-key-store-state) |
| VirtioMmioBlock | [UniXNU/VirtioMmioBlock](https://github.com/UniXNU/VirtioMmioBlock) | XNU 存储 | [VirtioMmioBlock](/zh/drivers/virtio-mmio-block) |
| VirtioMmioConsole | [UniXNU/VirtioMmioConsole](https://github.com/UniXNU/VirtioMmioConsole) | XNU 控制台 | [VirtioMmioConsole](/zh/drivers/virtio-mmio-console) |
| ShengNovatekTouch | [UniXNU/ShengNovatekTouch](https://github.com/UniXNU/ShengNovatekTouch) | XNU 触控 | [ShengNovatekTouch](/zh/drivers/sheng-novatek-touch) |
| XnuPrelink | [UniXNU/XnuPrelink](https://github.com/UniXNU/XnuPrelink) | 内核工具 | [XnuPrelink](/zh/drivers/xnu-prelink) |
| Ath12kWifi | [UniXNU/Ath12kWifi](https://github.com/UniXNU/Ath12kWifi) | XNU Wi-Fi | [Ath12kWifi](/zh/drivers/ath12k-wifi) |
| ArmCpu | [UniXNU/ArmCpu](https://github.com/UniXNU/ArmCpu) | XNU CPU 和 GIC | [ArmCpu](/zh/drivers/arm-cpu) |
| ArmDTPlatform | [UniXNU/ArmDTPlatform](https://github.com/UniXNU/ArmDTPlatform) | XNU 平台专家 | [ArmDTPlatform](/zh/drivers/arm-dt-platform) |
| ArmVirtPlatform | [UniXNU/ArmVirtPlatform](https://github.com/UniXNU/ArmVirtPlatform) | XNU 平台 | [ArmVirtPlatform](/zh/drivers/arm-virt-platform) |
| ArmSmmu4K | [UniXNU/ArmSmmu4K](https://github.com/UniXNU/ArmSmmu4K) | XNU SMMU kit | [ArmSmmu4K](/zh/drivers/arm-smmu4k) |
| AirNir | [UniXNU/AirNir](https://github.com/UniXNU/AirNir) | 编译器 kit | [AirNir](/zh/drivers/air-nir) |
| AdrenoPM4 | [UniXNU/AdrenoPM4](https://github.com/UniXNU/AdrenoPM4) | GPU 命令 kit | [AdrenoPM4](/zh/drivers/adreno-pm4) |
| AdrenoFirmware | [UniXNU/AdrenoFirmware](https://github.com/UniXNU/AdrenoFirmware) | GPU 固件 kit | [AdrenoFirmware](/zh/drivers/adreno-firmware) |
| Sm8550Platform | [UniXNU/UniXNU-sm8550-common](https://github.com/UniXNU/UniXNU-sm8550-common) | SM8550 GPU 平台 kit | [Sm8550Platform](/zh/drivers/sm8550-platform) |
| DarwinBoot | [UniXNU/DarwinBoot](https://github.com/UniXNU/DarwinBoot) | UEFI 加载器 | [DarwinBoot](/zh/drivers/darwin-boot) |
| VerifiedRoot | [UniXNU/VerifiedRoot](https://github.com/UniXNU/VerifiedRoot) | 根信任工具 | [VerifiedRoot](/zh/drivers/verified-root) |
| ShengPreflight | [UniXNU/ShengPreflight](https://github.com/UniXNU/ShengPreflight) | UEFI 预检 | [ShengPreflight](/zh/drivers/sheng-preflight) |

## 社区驱动

这些仓库由各自维护者维护，由使用它的设备仓库链接。

| 驱动 | 设备 | 仓库 | 页面 |
| --- | --- | --- | --- |
| NativeMsdc | Benesse TAB-A04-BR3（MT8167） | [mouseos/NativeMsdc](https://github.com/mouseos/NativeMsdc) | [NativeMsdc](/zh/drivers/community-native-msdc) |
| NativeAdreno-myron | Redmi K90 Pro Max / Poco F8 Ultra | [zg7681/NativeAdreno-myron](https://github.com/zg7681/NativeAdreno-myron) | [NativeAdreno-myron](/zh/drivers/community-native-adreno-myron) |
| NativeUfs-myron | Redmi K90 Pro Max / Poco F8 Ultra | [zg7681/NativeUfs-myron](https://github.com/zg7681/NativeUfs-myron) | [NativeUfs-myron](/zh/drivers/community-native-ufs-myron) |
| NativeAdreno-fuxi | 小米 13 | [ljhhkx529/NativeAdreno-fuxi](https://github.com/ljhhkx529/NativeAdreno-fuxi) | [NativeAdreno-fuxi](/zh/drivers/community-native-adreno-fuxi) |
| NativeUfs-alioth | Redmi K40 / Poco F3 | [FFT-infra/NativeUfs-alioth](https://github.com/FFT-infra/NativeUfs-alioth) | [NativeUfs-alioth](/zh/drivers/community-native-ufs-alioth) |
| unixnu-nativeufs | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativeufs](https://github.com/RigoLigoRLC/unixnu-nativeufs) | [unixnu-nativeufs](/zh/drivers/community-unixnu-nativeufs) |
| unixnu-nativemobiledisplay | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativemobiledisplay](https://github.com/RigoLigoRLC/unixnu-nativemobiledisplay) | [unixnu-nativemobiledisplay](/zh/drivers/community-unixnu-nativemobiledisplay) |
| unixnu-nativeramblock | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativeramblock](https://github.com/RigoLigoRLC/unixnu-nativeramblock) | [unixnu-nativeramblock](/zh/drivers/community-unixnu-nativeramblock) |
| NativeEmmc | Redmi Note 9 | [Dracen-W/NativeEmmc](https://github.com/Dracen-W/NativeEmmc) | [NativeEmmc](/zh/drivers/community-native-emmc) |
| NativeDwc3 | 小米平板 5 | [Lux12138/NativeDwc3](https://github.com/Lux12138/NativeDwc3) | [NativeDwc3](/zh/drivers/community-native-dwc3) |
| unixnu-nativefocaltechtouch | Galaxy Tab S7 FE Wi-Fi | [RigoLigoRLC/unixnu-nativefocaltechtouch](https://github.com/RigoLigoRLC/unixnu-nativefocaltechtouch) | [unixnu-nativefocaltechtouch](/zh/drivers/community-nativefocaltechtouch) |

## 设备分支

这些仓库是跟随官方驱动的设备分支，由对应设备仓库链接，不单独建驱动页。

| 设备 | 驱动 | 仓库 |
| --- | --- | --- |
| Sony Xperia 1 II | NativeAdreno | [chardidathing/NativeAdreno](https://github.com/chardidathing/NativeAdreno) |
| 小米平板 7 | NativeAdreno、NativeMobileDisplay | [Allenwdk/NativeAdreno](https://github.com/Allenwdk/NativeAdreno)、[Allenwdk/NativeMobileDisplay](https://github.com/Allenwdk/NativeMobileDisplay) |
| Nothing Phone (3a) | NativeAdreno、NativeUfs | [rootstockos/NativeAdreno](https://github.com/rootstockos/NativeAdreno)、[rootstockos/NativeUfs](https://github.com/rootstockos/NativeUfs) |
| 一加 6T | NativeAdreno、NativeMetal | [johnpanos/NativeAdreno](https://github.com/johnpanos/NativeAdreno)、[johnpanos/NativeMetal](https://github.com/johnpanos/NativeMetal) |
| 小米 13 Pro | NativeUfs | [pubglite55/NativeUfs](https://github.com/pubglite55/NativeUfs) |
| 一加 5 | NativeUfs | [lss717/NativeUfs](https://github.com/lss717/NativeUfs) |
| QEMU virt | NativeAdreno、NativeMetal、NativeMobileDisplay、NativeUfs | [xVanTuring/NativeAdreno](https://github.com/xVanTuring/NativeAdreno)、[xVanTuring/NativeMetal](https://github.com/xVanTuring/NativeMetal)、[xVanTuring/NativeMobileDisplay](https://github.com/xVanTuring/NativeMobileDisplay)、[xVanTuring/NativeUfs](https://github.com/xVanTuring/NativeUfs) |
| Benesse TAB-A04-BR3 | NativeMetal | [mouseos/NativeMetal](https://github.com/mouseos/NativeMetal) |
| Unisoc 设备 | NativeUfs | [N1709/NativeUfs](https://github.com/N1709/NativeUfs) |

## 规则

- 每个硬件驱动单独一个仓库。
- SoC 和设备配置按 ID 选择目录组件，feeds 与子模块提供额外源码。
- 官方机型或通用栈的驱动可以贡献到 UniXNU 组织。
- 其他驱动由维护者独立维护，以子模块链接。
- 每个驱动仓库都带 `unixnu` topic。
