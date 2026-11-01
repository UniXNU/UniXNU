# Xiaomi MIX Fold 2 \(zizhan, SM8475\): UniXNU bring-up derived from Pong

[qiumochen/UniXNU-zizhan](https://github.com/qiumochen/UniXNU-zizhan)

<div v-pre>

Xiaomi MIX Fold 2：iPadOS 18.7.10 主屏、内屏触摸、Adreno 730 渲染（120 Hz 面板，滑动约 54 fps）与电池读数；基于 UniXNU-pong

Source record: [porting.toml](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/porting.toml), `c434bb62fb0bc4722570724fb77853f6033252a3`.

This page is generated from the device record.

| Area | Status |
| --- | --- |
| [Configuration](#configuration) | `host-verified` |
| [Firmware and boot](#firmware) | `implemented` |
| [CPU and interrupts](#cpu) | `implemented` |
| [Memory and DMA](#memory) | `implemented` |
| [Storage and root](#storage) | `implemented` |
| [Display](#display) | `implemented` |
| [Input](#input) | `implemented` |
| [GPU](#gpu) | `implemented` |
| [Network](#network) | `planned` |
| [Audio](#audio) | `planned` |
| [Power](#power) | `implemented` |
| [Image assembly](#packaging) | `host-verified` |
| [Diagnostics](#diagnostics) | `implemented` |

## Configuration {#configuration}

`host-verified`

Components: `PongPlatform24`.

### Hardware and dependencies

- zizhan（22061218C）实机 /sys/firmware/fdt，MIUI V14.0.15.0.TLRCNXM（Android 13，内核 5.10.136）
- UniXNU-pong 的 SM8475 公共层与 PongPlatform24（Nothing Phone \(2\)，同为 SM8475）
- iPad7,11 的 iPadOS 18.7.10 22H374 restore

### Configuration

- board.toml：name = zizhan，device\_tree = dts/zizhan.dts，kernel.defconfig = zizhan\_ipados18\_gpu\_defconfig
- configs/zizhan\_ipados18\_gpu\_defconfig：CONFIG\_XNU\_PONG\_ADRENO\_PLATFORM=y、CONFIG\_XNU\_PONG\_POWER=y、CONFIG\_XNU\_PONG\_WIFI=n、CONFIG\_XNU\_PONG\_BACKLIGHT=n
- patches/xnu-ipados18/series：0001–0006、0008–0014，按序号应用

### Procedure

- tools/gen\_reserved.py 按 pong.dts 的布局从实机 DT 生成 dts/zizhan.dts：model、compatible、DRAM 区间和 reserved-memory 换成 zizhan 的值。
- 固件段指向 uefi-zizhan 的 Platforms/Xiaomi/zizhanPkg/zizhan.dsc。
- 其余沿用 Pong 的四层选择（ARM64、SM8475、22H374、板级）。

### Development findings

- zizhan 与 Pong 的 DRAM 第二段不同（0xf4600000+0xba00000，Pong 为 0xf1400000+0xec00000），ADSP carveout 为 0x9fd00000+0x3100000（Pong 为 0x85700000+0x2800000）；其余 SMEM、IPCC、AOSS、cmd-db 地址相同。
- 构建脚本不读取 board 名，改名 zizhan 不影响 Pong 脚本。

### Completion criteria

- dts/zizhan.dts 能编译，内核与启动镜像能构建，手机能进入 iPadOS 主屏

### Current limits

- 外屏（DSI-2，1080x2520）、Wi-Fi、音频没有接入，配置里关闭。

### Next action

- 用发布的版本打包启动镜像并上机跑一轮，记录设备结果。

### Evidence

- `source`: [记录了实机硬件参数、全分区备份和原厂 UEFI 内存表对照。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-28-device-prep.md)
- `source`: [记录了 zizhan 与 Pong 的硬件地址差异。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-11-01-battery.md)
- `host`: [托管 runner 上解析四层配置、编译 dts/zizhan.dts、应用全部 13 个 XNU 补丁并链接出 CI 内核，产物 pong-macos-products 已上传。](https://github.com/qiumochen/UniXNU-zizhan/actions/runs/41304992346)
  Command: <code>GitHub Actions zizhan macOS build（macos-15-intel，Xcode 16.4，pong_ipados18_ci_defconfig）</code>. Revision: `28d9f4fe869293e7a384b18b800ceb8dd56c1244`.

## Firmware and boot {#firmware}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- uefi-zizhan（uefi-pong 加 Platforms/Xiaomi/zizhanPkg）
- 原厂 uefi\_b 的 uefiplat.cfg 内存表

### Configuration

- MemoryMap：PIL Reserved 大小 0x1DC00000，删去 Demura 和 QTEE
- SimpleFbDxe：framebuffer 0xb8000000，2160x1916（bootloader 留下的 cont\_splash\_region）
- 启动方式：fastboot boot，不写任何分区

### Procedure

- build\_fw.sh 用 EDK II 构建 zizhanPkg 的 FD；build\_bootimg.py 把 BootShim、FD 和实机 DTB 拼成 boot v4 镜像。
- DarwinBoot24 读取 UniXNU 菜单配置，交接 XNU 前武装看门狗（pong\_autoreset）。
- 命令行不能超过 1023 个字符，ci\_boot\_ufs.sh 在打包时检查。

### Development findings

- 内屏显示 Silicium logo 和 UniXNU 菜单，颜色和方向正确；DarwinBoot24 能交接给 XNU。
- DarwinBoot24 拒绝启动时，把原因追加到 logfs:\\BOOTFAIL.TXT，然后重试，最后回到 fastboot。

### Completion criteria

- fastboot boot 后进入 UniXNU 菜单并启动 XNU；任何失败都能自动回到 fastboot

### Current limits

- 高通 DXE 二进制沿用 uefi-pong 的 Binaries/pong；没有 zizhan 自己的 DisplayDxe，外屏不点亮。

### Next action

- 改用原厂 FV 里的 Panel\_L18\_38\_0c\_0a\_sec\_dsc\_cmd.xml 尝试点亮外屏。

### Evidence

- `source`: [UEFI、DarwinBoot24 交接和 XNU 早期启动的上机记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-29-xnu-bringup.md)

## CPU and interrupts {#cpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- SM8475：4 个 Cortex-A510、3 个 Cortex-A710、1 个 Cortex-X2；GICv3；19.2 MHz 定时器；PSCI

### Configuration

- ADT cluster-type（PONG\_ADT\_CLUSTERS=1），内核用 \_\_ARM\_AMP\_\_ 构建两个 cluster
- boot-arg pong\_fast\_pri（默认 47）和 pong\_fast\_cpu（默认 7）
- ml-timeout-lock-panic-scale=40、interrupt-masked-debug-mode=1

### Procedure

- 0008 把 E/P 两个 cluster 交给 AMP 调度器；0014 让 UI 优先级线程先用空闲的 X2；0003 限制 qsort 递归深度，避免启动栈溢出。

### Development findings

- 8 个 CPU 全部启动。AMP 内核如果 ADT 里没有 cluster-type，会在早期卡住（g97）。
- 这个 SoC 在 Gunyah 下普通的停顿也会超过 DEVELOPMENT 内核的 500 µs 中断屏蔽阈值，所以超时按 sheng 的做法放大 40 倍，中断屏蔽检查只记录不 panic。
- SpringBoard 主线程在 app 打开卡顿时 0.73 个核跑在 A710、只有 0.09 跑在 X2（g170），0014 因此让 UI 线程先用 X2。

### Completion criteria

- 8 核启动，滑动时 UI 线程优先落到 X2

### Current limits

- 没有温控；连续多轮后手机发热，ramoops 出现大量位翻转。

### Next action

- 接入 SM8475 的温度传感器和 CPU 调频限制。

### Evidence

- `source`: [8 核启动（k4），E/P 调度对比和 tsample 线程采样记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [X2 优先调度的测量和结果。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-11-01-120hz-and-cadence.md)

## Memory and DMA {#memory}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 实机 DT 的 memory 和 reserved-memory 节点

### Configuration

- dts/zizhan.dts 的 memory@80000000 和 reserved-memory

### Procedure

- DarwinBoot24 只把实际拥有的 RAM 区间交给 XNU。

### Development findings

- XNU 打印 Pong RAM: 4 owned banks, 9728 MiB；物理内存 12 GiB，空洞不会分配给 VM。

### Completion criteria

- XNU 启动并打印受管内存

### Current limits

- 受管容量 9728 MiB，没有用上全部物理内存。

### Next action

- 核对 0x9\_0000\_0000 以上的区间能否交给 XNU。

### Evidence

- `source`: [k1 打印受管内存 9728 MiB。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-29-xnu-bringup.md)

## Storage and root {#storage}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- UFS 3.1；Android userdata 分区（f2fs）
- 22H374 的 OS、SystemOS、Data 镜像（在 Mac 上用 IPSW 制作）

### Configuration

- boot-arg pong\_shngroot\_4k=&lt;4K 块号&gt;：根镜像在 userdata 里的起始块
- pong\_ufs\_async=0（默认），pong\_ufs\_defer 默认开

### Procedure

- install\_pinned.py 用 pinalloc 在 Android /data 里分配一个物理连续的 19.4 GiB 文件 /data/hackios/root.img，写入 OS、SystemOS、Data 三个窗口，打印起始块号。
- RootLayout 按这个块号把三个窗口作为独立的 IOMedia 发布。
- 0006：publishResource 发现 IOResources 还在配置中时，立即投递 matched 通知。

### Development findings

- 没有修 0006 之前，大约每 4 次启动有 3 次失败（Failed to mount root device）。原因是 APFS 容器探测在 IOBSD 发布之前运行，持有 APFS 的锁去等 IOBSD，与 IOResources 配置形成死锁环（g28 用 0005 的等待线程转储抓到）。修复后 g36–g39 4/4 正常挂根。
- OS、SystemOS 和可写 Data 三个卷都能挂载，原厂 22H374 launchd 能启动。

### Completion criteria

- 每次启动都能挂根；Data 卷的写入在下次启动后仍在

### Current limits

- 根镜像在 Android 的 f2fs 文件里，Android 里不能移动或碎片整理这个文件（用一个 40 GiB 的占位文件保持连续）。

### Next action

- 给 AppleImage4 提供软件 IOAESAccelerator，消除它在 /defaults 上的永久等待。

### Evidence

- `source`: [根文件系统方案、挂根死锁的根因分析和 0006 修复前后的对比。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-30-root-and-autoloop.md)

## Display {#display}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 内屏 DSI-1，2160x1916，命令模式，DSC，60/120 Hz
- bootloader 留下的 cont\_splash\_region（0xb8000000 + 0x2b00000）

### Configuration

- ADT display-scale 和 artwork-scale-factor = 2（1080x958 点）
- pong\_panel\_hz（默认 120）
- pong\_dpu\_flip=1、pong\_dpu\_bufs=2、pong\_zc=2、fb\_swapwait=1（内核默认值）

### Procedure

- DSI 命令 FIFO 发出 DT 里 timing@1 的 timing-switch 命令，把面板切到 120 Hz。
- DPU 直接翻页到 CoreAnimation 自己的画布，三缓冲，不再用 GPU 拷贝。

### Development findings

- display-scale 为 3 时 1916/3 不是整数，SpringBoard 的状态栏 Auto Layout 无限递归崩溃；改成 2 后主屏正常（u3）。
- INTF\_1 帧计数从 60.5/s 变为 120.2/s，翻页 latch 上限从 16.6 ms 降到 8.3 ms，合成滑动的帧率从 44.6 升到 54–55 fps。
- 去掉每帧 2.5 ms 的扫描输出拷贝后，每帧都被显示，没有撕裂计数。

### Completion criteria

- 内屏显示 iPadOS 主屏，120 Hz 下滑动帧率稳定

### Current limits

- 外屏没有驱动；背光沿用 bootloader 的状态，系统里不能调节亮度。

### Next action

- 接入面板背光的 DCS 命令，让亮度设置生效。

### Evidence

- `source`: [内屏显示 iPadOS 主屏（u3）。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/evidence/2026-10-30-u3-ipados-homescreen.jpg)
- `source`: [120 Hz 切换和帧率测量。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-11-01-120hz-and-cadence.md)
- `source`: [DPU 翻页零拷贝三缓冲的实现和测量。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-11-01-zero-copy-and-return-paths.md)

## Input {#input}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- 内屏触摸 ST FTS（spi0.0 fts-pri），固件 st\_fts\_l18.ubin
- PMIC 电源键

### Configuration

- boot-arg pong\_touch=1，touch\_flip 默认 2（y 镜像）
- 电源键长按 pong\_button\_reset 毫秒（默认 3000）后热复位到 fastboot

### Procedure

- 0002 加入 bsd/dev/pong\_fts.c：SE4 只能给 GSI 用，所以 SPI 用 GPIO 模拟。
- 触摸事件走 Pong 原有的 HID 路径交给 backboardd。

### Development findings

- 用触摸在主屏上打开了「设置」（t4）。
- 长按电源键 3 秒能把手机从运行中的 iOS 送回 fastboot。

### Completion criteria

- 触摸能点开应用、滑动页面

### Current limits

- 外屏触摸（spi2.0 fts-sec）没有驱动；音量键没有核对。

### Next action

- 核对音量键的 PMIC 外设地址。

### Evidence

- `source`: [用触摸打开了「设置」。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/evidence/2026-10-30-t4-settings-by-touch.jpg)
- `source`: [触摸驱动的轮次记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-30-root-and-autoloop.md)

## GPU {#gpu}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- Adreno730v3；手机自带固件 a730\_sqe.fw、gmu\_gen70000.bin、a730\_zap.\*（不进仓库）
- Turnip 和 metal2vulkan

### Configuration

- PONG\_ADRENO\_FIRMWARE 指向固件目录
- pong\_gpu\_level（GMU 起始档位，默认 9 = 710 MHz）
- 内核默认拒绝 MercuryPosterEx 使用 GPU（pong\_gpu\_deny=- 恢复）

### Procedure

- Adreno bring-up 等 rootvnode 出现后再开始；Metal provider 在挂根之后才发布。
- 扫描输出按 surface 缓存映射和导入。

### Development findings

- GPU 渲染的主屏和动画已由用户照片确认。
- 壁纸扩展 MercuryPosterEx 会和 backboardd 抢 GPU，基线 13 轮里有 5 轮整机 GPU 丢失；拒绝它之后 6/6 没有丢失，滑动帧率平均 54.5 fps。
- 固定 900 MHz 不比 DCVS 快，GPU 频率不是瓶颈。

### Completion criteria

- 主屏和应用由 GPU 渲染，长时间滑动没有 GPU 丢失

### Current limits

- 壁纸扩展不能用 GPU；metal2vulkan 每次提交仍有约 10–20 ms 的 CPU 开销。

### Next action

- 支持 IOSurfaceSharedEvent 监听，让壁纸扩展重新使用 GPU。

### Evidence

- `source`: [GPU bring-up、GPU 丢失的诊断和拒绝壁纸扩展的对照实验。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [逐帧 GPU 提交时间线。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-31-frame-timeline.md)

## Network {#network}

`planned`

Components: `PongPlatform24`.

### Hardware and dependencies

- QCA6490（与 Nothing Phone \(2\) 相同），zizhan 自己的 board data

### Configuration

- CONFIG\_XNU\_PONG\_WIFI=n，boot-arg pong\_wifi=0

### Procedure

- 暂不启动 Pong 的 Wi-Fi 栈。

### Development findings

- zizhan 的 PCIe、GPIO 和 board data 还没有与 Pong 核对。

### Completion criteria

- 扫描到网络并完成关联

### Current limits

- 没有接入。

### Next action

- 从实机 DT 核对 PCIe0 和 WLAN 使能 GPIO，再打开 CONFIG\_XNU\_PONG\_WIFI。

### Evidence

- `source`: [记录了 Wi-Fi 芯片型号。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-28-device-prep.md)

## Audio {#audio}

`planned`

Components: `PongPlatform24`.

### Hardware and dependencies

- 2 个 CS35L41 功放（I2C 2-0040、2-0042）；Pong 用的是 TFA9873

### Configuration

- boot-arg pong\_audio=0；没有 tfa98xx.cnt 时构建一张空功放表

### Procedure

- 暂不启动音频。

### Development findings

- 功放型号与 Pong 不同，Pong 的 TFA9873 路径不能直接用。

### Completion criteria

- 扬声器能出声

### Current limits

- 没有 CS35L41 驱动。

### Next action

- 参照 Linux cs35l41 驱动写 I2C 初始化序列。

### Evidence

- `source`: [记录了音频不启动的原因和空功放表。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-11-01-battery.md)

## Power {#power}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- ADSP 固件：/vendor/firmware\_mnt/image/adsp.mdt 和 b00..b25，用 mdt2mbn.py 合并为 adsp.mbn（不进仓库）
- UniXNU-sheng 的 ShengBattmgr 协议

### Configuration

- CONFIG\_XNU\_PONG\_POWER=y
- boot-arg pong\_adsp=2 启动 DSP 和电池，1 只做映射和调查，0 关闭

### Procedure

- PongAdsp 用 zizhan 的 carveout 加载并认证启动 ADSP，经 PMIC GLINK 读取电池。
- ShengBattmgr 改用小米的属性编号（12 之后后移一位），温度单位已经是 0.01 °C。
- 不编 Wi-Fi 时由 PongRpmh.cpp 提供共享的 RPMh 投票。

### Development findings

- g206 的读数与 Android sysfs 一致：电量 100 %、4444 mV、充电 426 mA、34.40 °C、满充 3507 mAh、设计 4500 mAh、循环 907 次。

### Completion criteria

- 状态栏和「设置 › 电池」显示正确的电量，插拔充电器有变化

### Current limits

- 状态栏和设置里的显示还没有人工确认；没有休眠和唤醒。

### Next action

- 人工确认状态栏电池图标和插拔充电器的变化。

### Evidence

- `source`: [ADSP 启动阶段 1–13 全部通过，电池读数与 Android 一致。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-11-01-battery.md)

## Image assembly {#packaging}

`host-verified`

Components: `PongPlatform24`.

### Hardware and dependencies

- xnu-11417.140.69（Darwin 24.6.0）和 22H374 restore 的原始组件

### Configuration

- patches/xnu-ipados18/series
- PROFILE=zizhan\_ipados18\_gpu

### Procedure

- ci\_prep.sh 准备依赖，ci\_kernel.sh 构建内核，ci\_boot\_ufs.sh 预链接并打包成启动镜像。
- build-xnu-ipados18.sh 用 patch --forward 依次应用补丁，避免把看起来已应用的块反向撤销。

### Development findings

- 干净的 xnu-11417.140.69 按 series 依次应用全部补丁后，与实际构建用的工作树逐文件一致。
- 新版 Xcode 的 clang 多了三个警告，在 -Werror 下需要关掉；Pong 脚本原来只允许 Intel 主机，现在也允许 arm64 主机。

### Completion criteria

- 从本仓库的提交构建出能上机的启动镜像

### Current limits

- Apple 镜像、固件和 ABI 二进制都要在本机准备。

### Next action

- 用这个版本打包启动镜像并上机跑一轮，记录设备结果。

### Evidence

- `source`: [构建链说明。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-29-xnu-bringup.md)
- `host`: [Mac Studio（Apple silicon，Xcode 26.6.0）从全新的构建目录完整编译出 DEVELOPMENT\_ARM64\_PONG 内核，18321080 字节；zizhan 的 boot-arg 字符串（pong\_fts、pong\_panel\_hz、pong\_dpu\_flip 等）与上机使用的内核一致。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/evidence/host-build-zizhan_ipados18_gpu.txt)
  Command: <code>ZIZHAN_SRC=&lt;work dir&gt; ci_prep.sh &amp;&amp; DEFCONFIG=zizhan_ipados18_gpu_defconfig JOBS=10 ci_kernel.sh</code>. Revision: `1ec1190f4e3467a36a7a7402bc766dfdf688adf1`.

## Diagnostics {#diagnostics}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- ramoops（0x85200000）、logfs 分区、USB（adb 和 fastboot）

### Configuration

- pong\_autoreset=&lt;秒&gt;（默认 300），pong\_autoreset\_sb
- pong\_klog\_4k：内核把 ramoops 区复制到 UFS 上的固定文件
- pong\_gtrace、touch\_lat：逐帧时间线

### Procedure

- cycle.sh：fastboot boot 镜像，等看门狗复位回 fastboot，再启动 RamoopsDump 把 ramoops 写进 logfs 并回到 Android，最后经 adb 取回日志。
- panic、长按电源键 3 秒和到点复位都会热复位到 fastboot，DRAM 里的日志保留。

### Development findings

- 整个流程不需要人按键。漏带 pong\_autoreset 的轮次（g152 系列）曾被误判为总线冻结。
- 连续多轮后手机发热，DRAM 里的 ramoops 几乎每行都有位翻转；pong\_klog\_4k 写到 UFS 的副本没有这个问题。

### Completion criteria

- 每一轮都能自动回到 Android 并取回完整日志

### Current limits

- 日志位翻转与温度有关；cycle.sh 在每轮之前等电池降到 35 °C。

### Next action

- 把 klog 作为默认日志来源。

### Evidence

- `source`: [免按键闭环的设计和轮次记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [四条复位回路的修复。](https://github.com/qiumochen/UniXNU-zizhan/blob/c434bb62fb0bc4722570724fb77853f6033252a3/docs/progress/2026-11-01-zero-copy-and-return-paths.md)

</div>
