# Xiaomi Redmi Turbo 4 \(rodin, MediaTek Dimensity 8400-Ultra / MT6899\) \(nvhv460-sketch\)

[nvhv460-sketch/UniXNU-rodin](https://github.com/nvhv460-sketch/UniXNU-rodin)

<div v-pre>

Xiaomi Redmi Turbo 4 \(rodin, Dimensity 8400-Ultra / MT6899\) port. Baseline: rothko \(K70 Ultra, MT6989\). Hardware inventory largely filled from HyperOS 3.0.305.0 package \(PGPT\_UFS / vendor\_boot DTB / dtbo\).

源记录: [porting.toml](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/porting.toml), `224c29a530c45f1e9363faec41ab493bcdb9a1d9`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `planned` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `planned` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `planned` |
| [显示](#display) | `implemented` |
| [输入](#input) | `implemented` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [cellular](#cellular) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `planned` |
| [诊断](#diagnostics) | `planned` |

## 配置 {#configuration}

`planned`

组件: `ArmDTPlatform`, `ArmCpu`, `SoftwareAES`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- SoC 型号确认、stock DTS、内存版本（见 docs/hardware-inventory.md）

### 配置

- TODO: 填入 board.toml 字段、DTS 属性与 defconfig 值

### 操作步骤

- TODO: 记录实际执行的配置命令

### 开发经验

- TODO
- 2026-11-14: board.toml 接线 \[firmware\] preflight 与 \[bootimg\] dtb（stock DTS→dtc→boot.img）；configuration 区域引用不变，仅随 board.toml 记录该提交。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- 所有 source pin 可解析；status 显示预期的覆盖与补丁顺序

### 当前范围

- 硬件输入未收集

### 下一步

- 按 docs/hardware-inventory.md 收集配置输入

### 证据

按下一步操作收集证据。

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- 官方线刷包、UEFI fork（nvhv460-sketch/Silicium-Rothko，已 add rodinPkg）、lk/preloader 日志

### 配置

- external\_repository=https://github.com/nvhv460-sketch/Silicium-Rothko.git; config=rodin; dsc=Platforms/Xiaomi/rodinPkg/rodin.dsc; fd=Build/rodinPkg/&\#123;target&\#125;\_CLANGPDB/FV/SILICIUM\_UEFI.fd; defines ENABLE\_SECUREBOOT=0 DEVICE\_MODEL=0 MEMORY\_PROTECTION=TRUE SHIP\_MODE=FALSE; submodules Mu\_Basecore/Common/Mu/Common/Mu\_OEM\_Sample（linux.yml checkout 不带子模块）; packages 含 Silicon/Silicium + Silicon/MediaTek + Platforms/Xiaomi + Common/Mu\(\_OEM\_Sample\) + Mu\_Basecore，因 EDK2 \!include 沿 PACKAGES\_PATH 解析

### 操作步骤

- TODO: GitHub Actions Linux full build \(steps=full, uefi\_repository=nvhv460-sketch/Silicium-Rothko\) 产出 SILICIUM\_UEFI.fd；再 fastboot boot

### 开发经验

- MT6899 SoC mmio 全部与 rothko \(MT6989\) 一致：GIC 0x0C400000/0x0C440000，watchdog 0x1C00B000，pinctrl 0x10005000，PMIF 0x1CC04000，UFS PHY/HCI 0x112A0000/0x112B0000；DSC0@0x14206000、DSI0@0x1420a000、MUTEX/DISPSYS/MMSYS/OVLSYS 地址均相同。面板 o10\_42\_02\_0a\_dsc\_vdo\_lcm\_drv，1220x2712 stride 1248，32bpp；LK 帧缓冲 atag,videolfb = 0xFCC20000/0x33D0000，真机实测验证。RodinHighMemDxe 使用 rodin 实际 12GiB 单段布局。MemoryMapLib v1 保守映射低段 124MiB 固件区+所有 MMIO+LK handoff 结构（DTB 0x47C80000、initrd 0x66F00000、Display Reserved 0xFCC20000）。高段至 0xC0000000 从 live iomem 转录。DSI mode 为 VDO（非 rothko CMD），现有 mode-check 路径自动跳过 command-mode push，GOP 通过 LK framebuffer 发布。
- 2026-11-14: linux.yml 的 uefi\_repository 默认值钉为 nvhv460-sketch/Silicium-Rothko —— 首次手工触发（run 43571077006）因输入留空在 Check the inputs 阶段即失败。
- 2026-11-14 本地 EDK II CLANGPDB 构建（clang 14.0.6，repo Mu\_Basecore b2382909 + libfdt/brotli/libspdm 子模块）打通到 FD：SILICIUM\_UEFI.fd 2,097,152 字节 sha256 27e8a9d0...8279，FVMAIN\_COMPACT 22% 满、FVMAIN 99% 满（72 字节余量）。过程中修掉三个真实阻塞：DarwinBoot 是独立组件包（DarwinBootPkg）而非 UniXNUPkg 子模块；UniXNUPkg 已删除 RamDisk 偏移/大小 PCD；PACKAGES\_PATH 必须含 Silicon/Silicium、Silicon/MediaTek、Platforms/Xiaomi、Common/Mu\(\_OEM\_Sample\) 与 &\#123;tree&\#125;/drivers/DarwinBoot。
- 2026-11-14 首次 Linux full build（run 43571244515）：内核两遍构建后产出 kernel.macho sha256 fe35b1b3...（第一遍 make 因 mockfs 符号缺失而失败是有意的，第二遍通过），package 产出 UniXNU.efi；固件步骤失败于 fork 专有的 Library/RothkoStage.h 在官方 mu\_basecore 中不存在（RodinDisplayDxe.c:1）。修复：驱动自带 RodinStage.h（0x1C00B000 看门狗舞台记录），本地增量构建通过；workflow 增加 firmware \(package firmware\) 快速通道，跳过内核与 bootimg。
- 2026-11-14 真机冒烟（解锁 + A/B 双槽）：MTK LK fastboot 0.5 不支持 fastboot boot（remote: unknown command），改用 root dd 写非活动槽 boot\_b + fastboot set\_active b 启动；UEFI Boot Manager 与 UniXNU 0.1.0 界面在面板正常显示，音量键移动选择、电源键确认，红字 no boot entry found（空 ramdisk 预期）。恢复命令 fastboot set\_active a。
- 2026-11-14: CI 固件步骤已成功（run 43576572068，firmware-only 通道，FD 产出 Build/rodinPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd）；新增 firmware preflight 生成 boot.img 基础 DTB，bootimg 需要 --dtb 因此 workflow 显式传入；payload 步骤补 unique-chip-id secret 环境变量。
- 2026-11-14: workflow 增加 boot.img 产物上传（含预链接内核，机主专用：下载后删除该 run）；firmware 区域记录该产物与删除要求。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- 固件构建通过，进入 DarwinBoot，发布 framebuffer，保持内存契约

### 当前范围

- 首次 fastboot boot 尚未执行；高段 0xC0..0x33FF 内存未验证；payload trust cache 待填充；FD 基址沿用 rothko 的 0x40400000，rodin LK 的实际内核加载地址是运行时变量，需第一次 fastboot boot 的屏幕/日志确认（备选 0x40000000）；本地构建用 clang 14，CI 用较新 clang + 流水线 &\#123;edk2&\#125;（mu\_basecore release/202608），两者源码相同但工具链不同

### 下一步

- 触发 github workflow 'Linux full build' steps=full，下载 .fd 产物，fastboot boot

### 证据

- `source`: [真机 /proc/iomem 全量（2026-11-14）：System RAM/保留区用于 MemoryMapLib v1 自由区与保留区转录，以及 RodinHighMemDxe 高段范围](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/docs/device-proc-iomem.txt)
- `source`: [GIC 0x0C400000/0x0C440000、watchdog 0x1C00B000、UFS 0x112A/0x112B0000、面板 o10\_42\_02\_0a\_dsc\_vdo 与 rothko 完全一致；hwcode 0x6899、DRAM 12GiB 单段](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/docs/hardware-inventory.md)
- `source`: [\[firmware\] external\_repository/config/dsc/fd 指向 nvhv460-sketch/Silicium-Rothko + rodinPkg，CLANGPDB 输出路径与 UniXNU firmware.py 硬编码工具链一致](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/board.toml)
- `host`: [Build ended with '- Done -'; Build/rodinPkg/DEBUG\_CLANGPDB/FV/SILICIUM\_UEFI.fd is 2,097,152 bytes with FV header FvLength 0x200000, sha256 27e8a9d0baf5ac16121efacdd1e5207cdad4901b2b140c3602b00b41ade82979. Every module compiles and links: the UFS stack, keypad pair, RodinDisplayDxe, RodinHighMemDxe, RodinWatchdogDxe, UniXNUPkg modules and DarwinBootPkg. FVMAIN is 99% full \(72 bytes free\) as expected for a DEBUG volume; FVMAIN\_COMPACT is 22% full.](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/board.toml)
  Command: <code>WORKSPACE=&lt;uefi&gt; EDK_TOOLS_PATH=&lt;mu_basecore&gt;/BaseTools CLANG_BIN=&lt;clang dir&gt;/ PACKAGES_PATH=&lt;uefi&gt;:&lt;uefi&gt;/Platforms/Xiaomi:&lt;uefi&gt;/Common/Mu:&lt;uefi&gt;/Common/Mu_OEM_Sample:&lt;mu_basecore&gt;:&lt;uefi&gt;/Silicon/MediaTek:&lt;uefi&gt;/Silicon/Silicium:&lt;tree&gt;/package:&lt;tree&gt;/drivers/DarwinBoot python3 &lt;mu_basecore&gt;/BaseTools/Source/Python/build/build.py -p Platforms/Xiaomi/rodinPkg/rodin.dsc -a AARCH64 -b DEBUG -t CLANGPDB -n 8 -D FD_BASE=0x40400000 -D FD_SIZE=0x200000 -D FD_BLOCKS=0x200 -D ENABLE_SECUREBOOT=0 -D DEVICE_MODEL=0 -D MEMORY_PROTECTION=TRUE -D SHIP_MODE=FALSE</code>. Revision: `b9150d592fc29b029317f3ab9fc03dcd7de4ec28`.
- `device`: [Rodin's panel shows the UEFI Boot Manager \('Please select boot device', UniXNU, UniXNU, Power Off, Exit, key hints\) and, on selecting UniXNU, the UniXNU 0.1.0 screen \(Return to Firmware/Restart/Power off/Tools, red 'no boot entry found', 'drivers 0 loaded / 0 failed'\). Volume Up/Down move the selection and the power key activates it, exercising the MT6363/PMIC-GPIO-196 key path and the DSC+VDO framebuffer GOP on hardware. boot-smoke.img sha256 4ad1daace0ecb2584d295541a824cb22ca221df8a04fdec3302b7fe787ed387b = gzip\(BootShim + SILICIUM\_UEFI.fd\) with the stock vendor\_boot DTB appended.](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/board.toml)
  Command: <code>adb push boot-smoke.img /data/local/tmp/; adb shell su -c 'dd if=/data/local/tmp/boot-smoke.img of=/dev/block/by-name/boot_b bs=4096 conv=fsync'; adb reboot bootloader; fastboot set_active b; fastboot reboot</code>. Revision: `fb30ebe5f837bdd55f4ff128a8ca799122577f08`.

## CPU 与中断 {#cpu}

`planned`

### 硬件与依赖

- CPU 拓扑、GIC、计时器、PSCI —— 已实测：8 核 4+3+1 三簇，MPIDR 0x0..0x700，GIC500@0xc000000，timer 13 MHz，PSCI enable-method（vendor\_boot DTB）

### 配置

- board.toml cpu\_regs=0x0,0x100,...,0x700（与 rothko 相同）；DTS timebase-frequency=13 MHz

### 操作步骤

- TODO: 真机记录 K1-K4/timer/IPI 标记

### 开发经验

- CPU 拓扑与 rothko 同构，mt6989-common 的 CPU/GIC/timer 资源预期可直接复用
- 2026-11-14: dts/rodin.dts 的 cpus 段沿用 mt6989.dtsi（8 核 4+3+1，unixnu,cluster-type E/P，PSI/psci 均由 dtsi 提供）；本次仅改 memory/占位符，CPU 拓扑未变，ADT 生成器本地验证通过。

### 完成条件

- 每个启用的 CPU 到达 entry 检查点，timer/IPI 正常

### 当前范围

- 频率/GDVFS 行为未验证（rothko 的 MtkCpuFreq 也只是固定请求）

### 下一步

- 从 lk 日志确认 FDVFS 接口与内存映射

### 证据

按下一步操作收集证据。

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- lk mblock 运行时内存映射、保留区、SMMU

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO
- 2026-11-14: dts/rodin-stock.dts（stock vendor\_boot 树反编译件）入库，dtc 往返 1989 节点一致、/chosen 与 memory 完全一致（444,761 vs 444,777 字节，差异来自 \_\_symbols\_\_ 文本）；boot.img 基础树由此生成。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- 交接区全部记账，DMA 范围与缓存策略符合记录

### 当前范围

- stock 静态 memory 节点 ≠ 运行时映射（rothko 已验证此教训）
- MemoryMapLib v1 已让固件从 SEC 跑到 BDS 菜单（2026-11-14），但高段 0xC0..0x33FF 未纳入、DMA/SMMU 记账尚未验证

### 下一步

- 抓取 lk mblock 日志

### 证据

- `device`: [The firmware reached the BDS menu with the transcribed map: low firmware extents, LK DTB at 0x47C80000, pstore 0x48080000, the 0x66F00000 initrd window and the Display Reserved carve at 0xFCC20000 all behave; no translation fault or GCD assert appeared on the panel.](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/docs/device-proc-iomem.txt)
  Command: <code>boot boot-smoke.img; the firmware's GCD map comes from MemoryMapLib (iomem transcription)</code>. Revision: `fb30ebe5f837bdd55f4ff128a8ca799122577f08`.

## 存储与根卷 {#storage}

`planned`

组件: `SoftwareAES`, `RamBlock`, `AppleKeyStoreState`, `VerifiedRoot`.

### 硬件与依赖

- 已实测：UFS host @0x112b0000 len 0x2a00（与 rothko 相同），PHY @0x112a0000 mt8183-ufsphy；GPT 已导出（92 分区，4K LBA）；LU 块大小待确认（预期 4096）

### 配置

- board.toml userdata.first\_lba=0xD50C0（scatter 0x354300000 / 4096）；last\_lba 按容量版本待填

### 操作步骤

- TODO

### 开发经验

- GPT 解析自 PGPT\_UFS：super LBA 524288..3407871；boot\_a 269056..285439；lk\_a 264960..269055；存在 pstore 133 MiB 分区
- 2026-11-14: board.toml 变更仅涉及 firmware/bootimg 段，storage 区域（userdata/root\_match）未变；记录本次 board.toml 提交。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- host/link/read/root/persistence 边界与清单一致，无越界写

### 当前范围

- UFS 参考时钟为高危项，需双重核对（rothko 事故）

### 下一步

- 解 lk.img 字符串，找 UFS refclk/PHY 初始化参数

### 证据

按下一步操作收集证据。

## 显示 {#display}

`implemented`

组件: `GopFramebuffer`.

### 硬件与依赖

- 面板 IC：o10\_42\_02\_0a\_dsc\_vdo / o10\_36\_02\_0b\_dsc\_vdo（dtbo，两款候选）；DSI0@0x1420a000 mt6899-dsi；背光 disp-leds 14-bit max 0x3fff；注意 DSC+VDO 与 rothko CMD 模式不同

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO
- 2026-11-14: board.toml 变更不触及 display 配置；UEFI GOP 已在真机确认（见 firmware 区域 device 证据）。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- 已知帧几何/颜色正确，userland 显示与背光可控

### 当前范围

- 分辨率与初始化序列待提取
- UEFI GOP 已真机验证（2026-11-14），但 XNU userland 显示与背光控制尚未测试

### 下一步

- 从 super.img vendor 分区解面板驱动参数，确认分辨率

### 证据

- `device`: [The UEFI Boot Manager and UniXNU 0.1.0 UI render on rodin's panel: 1220x2712 DSC+VDO panel \(o10\_42\_02\_0a\_dsc\_vdo\_lcm\_drv\) keeps scanning the LK framebuffer at 0xFCC20000 and the GOP sits on it, so text and the full menu are pixel-correct with no display register writes from the firmware.](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/board.toml)
  Command: <code>boot boot-smoke.img from slot b (dd + fastboot set_active b); observe the panel</code>. Revision: `fb30ebe5f837bdd55f4ff128a8ca799122577f08`.

## 输入 {#input}

`implemented`

### 硬件与依赖

- 触控已确认：Goodix + Focaltech 双方案（xiaomi\_touch 框架，SPI 15 MHz），goodix\_firmware\_rodin 固件名存在于 lk；按键路由待确认

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO

### 完成条件

- 触点映射到屏幕，多点 ID 稳定，释放事件到达，按键产生 HID 报告

### 当前范围

- 批次 IC 选择待真机日志确认
- 按键路径已真机验证（UEFI 菜单用音量键/电源键操作），触控尚未开始

### 下一步

- 确认 SPI 总线号与固件文件位置，参考 rothko GoodixBerlin9916K 组件

### 证据

- `device`: [Volume Up/Down moved the boot-device selection and the power key activated the UniXNU entry, so the PMIC GPIO 196 \(volume up\) and MT6363 PWRKEY/HOMEKEY \(power/down\) routes work through GpioDxe + KeypadDeviceDxe under UEFI.](https://github.com/nvhv460-sketch/UniXNU-rodin/blob/224c29a530c45f1e9363faec41ab493bcdb9a1d9/board.toml)
  Command: <code>boot boot-smoke.img and drive the Boot Manager menu with Volume Up/Down and the power key</code>. Revision: `fb30ebe5f837bdd55f4ff128a8ca799122577f08`.

## GPU {#gpu}

`planned`

### 硬件与依赖

- GPU 固件、SMMU stream、Android 参考实现

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO
- 2026-11-14: board.toml 变更不触及 GPU 配置；记录本次 board.toml 提交。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- GPU 提交/映射/fence 正确，Metal 客户端渲染已知图像

### 当前范围

- 预期长期开放；rothko 也未实现

### 下一步

- 盘点 GPU 固件与 SMMU stream（勿混入 Qualcomm GMU 术语）

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- Connsys 型号、总线、固件/校准文件

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO

### 完成条件

- 扫描、关联、地址配置、收发流量通过

### 当前范围

- 预期长期开放

### 下一步

- 盘点 Wi-Fi 芯片与固件

### 证据

按下一步操作收集证据。

## cellular {#cellular}

`planned`

### 硬件与依赖

- 范围决策：建议先记录 not-applicable

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO

### 完成条件

- 记录排除决策或完成调制解调器实现

### 当前范围

- 建议初期排除基带

### 下一步

- 记录 not-applicable 决策

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- 音频 DSP/codec、路由

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO

### 完成条件

- 声明的路由完成播放/捕获

### 当前范围

- 预期后期

### 下一步

- 盘点音频 DSP/codec

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- FDVFS 平台块 fdvfs@0x0c068200（mediatek,fdvfs）、VCore/DDR 请求链格式与 rothko 同；充电 IC/电量计已盘点

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO
- 2026-11-14: board.toml 变更不触及电源配置；按键/看门狗已在真机初步验证（见 input/firmware 区域）。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- 电源控制与电量读数与观察一致

### 当前范围

- 电量计/充电驱动尚未接入 XNU；睡眠/唤醒转换未实现（rothko 同样为开放项）

### 下一步

- 对照 rothko MtkCpuFreq 写 rodin 固定启动频率请求；确认 PMIC 电源键/按键路由

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`planned`

### 硬件与依赖

- donor IPSW、kernelcache、trust cache、Data seed

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO
- 2026-11-14: 新增 scripts/prepare-dtb.py（dtc 编译 dts/rodin-stock.dts → tree/dtb/rodin.dtb 与 device/dtb/rodin.dtb），workflow 的 bootimg 步骤显式传 --dtb；payload 步骤补 UNIXNU\_UNIQUE\_CHIP\_ID 环境变量。
- 2026-11-14: workflow 增加 boot.img/payload.img 产物上传（含预链接内核，属机主专用：下载后删除该 run）；packaging 区域记录该约束。
- 2026-11-14: schema 2 ADT 生成器从 dts/rodin.dts 产生 ADT（本地验证 12,824 字节）：修复 memory 段为 12 GiB 单段（0x40000000+0x300000000，与 payload.dram\_size 一致）、删除非法占位 touch-spi=&lt;TODO&gt;、GIC 记录值改 0x0c400000；root\_match\_volume\_uuid 留空跳过（尚无 userdata 卷 UUID）。

### 完成条件

- 内核+prelink 成功，payload 完整，boot 镜像符合格式与大小限制

### 当前范围

- payload/adt 多项 TODO

### 下一步

- 编写 make-turbo4-adt.py（参考 make-rothko-adt.py）

### 证据

按下一步操作收集证据。

## 诊断 {#diagnostics}

`planned`

### 硬件与依赖

- pmsg/ramoops、UEFI 日志导出；设备已有独立 pstore\(133 MiB\) 与 oops\(16 MiB\) 分区

### 配置

- TODO

### 操作步骤

- TODO

### 开发经验

- TODO

### 完成条件

- 每个里程碑有可复现命令、匹配版本与可访问结果

### 当前范围

- 持久化日志通道尚未建立；UEFI 日志导出未集成到固件

### 下一步

- 在固件集成时加入日志导出（QR/log ring），payload 启用 pmsg/ramoops 参数

### 证据

按下一步操作收集证据。

</div>
