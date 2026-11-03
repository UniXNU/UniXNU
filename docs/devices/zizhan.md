# Xiaomi MIX Fold 2 \(zizhan, SM8475\): UniXNU bring-up derived from Pong

[qiumochen/UniXNU-zizhan](https://github.com/qiumochen/UniXNU-zizhan)

<div v-pre>

Xiaomi MIX Fold 2：iPadOS 18.7.10 主屏、内屏触摸、Adreno 730 渲染（120 Hz 面板，滑动约 54 fps）与电池读数；基于 UniXNU-pong

Source record: [porting.toml](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/porting.toml), `fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd`.

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
| [Network](#network) | `host-verified` |
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
- 新增隔离的 zizhan\_ipados18\_wifi\_defconfig 与 zizhan-wifi-sm8475.json；默认 GPU 配置继续关闭 Wi-Fi。实机 WLAN PHY 和供电参数不同于 Pong，已用本机 live DT 逐项核验新 profile。

### Completion criteria

- dts/zizhan.dts 能编译，内核与启动镜像能构建，手机能进入 iPadOS 主屏

### Current limits

- 外屏（DSI-2，1080x2520）、Wi-Fi、音频没有接入，配置里关闭。

### Next action

- 用发布的版本打包启动镜像并上机跑一轮，记录设备结果。

### Evidence

- `source`: [记录了实机硬件参数、全分区备份和原厂 UEFI 内存表对照。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-28-device-prep.md)
- `source`: [记录了 zizhan 与 Pong 的硬件地址差异。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-01-battery.md)
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

- `source`: [UEFI、DarwinBoot24 交接和 XNU 早期启动的上机记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-29-xnu-bringup.md)

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

- `source`: [8 核启动（k4），E/P 调度对比和 tsample 线程采样记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [X2 优先调度的测量和结果。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-01-120hz-and-cadence.md)

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

- `source`: [k1 打印受管内存 9728 MiB。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-29-xnu-bringup.md)

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

- `source`: [根文件系统方案、挂根死锁的根因分析和 0006 修复前后的对比。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-30-root-and-autoloop.md)

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
- 旧内核截图日志每行被截断，只保留左侧约 39/135 个采样列；新分段格式已在 g248、g249 上机验证，但采样截图不能代替像素级面板检查。

### Next action

- 接入面板背光的 DCS 命令。

### Evidence

- `source`: [内屏显示 iPadOS 主屏（u3）。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/evidence/2026-10-30-u3-ipados-homescreen.jpg)
- `source`: [120 Hz 切换和帧率测量。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-01-120hz-and-cadence.md)
- `source`: [DPU 翻页零拷贝三缓冲的实现和测量。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-01-zero-copy-and-return-paths.md)
- `device`: [每轮 6 张截图均完整解出 135/135 列、120/120 行；主屏及天气画面横跨整幅图，旧右侧黑区确为缺失数据补黑。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>cycle.sh g248、g249；tools/zizhan/mac/shot.py</code>. Revision: `c9c8fd274c279a8571b525a1e1dbdf8eddf84d9d`.

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

- `source`: [用触摸打开了「设置」。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/evidence/2026-10-30-t4-settings-by-touch.jpg)
- `source`: [触摸驱动的轮次记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [ui\_compat18.c 新增 zizhan display-link 速率 WIP；未构建、未上机，触摸与动画体验需要独立回归，未改变输入区域验证等级。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)

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
- GPU 客户端因内存 ledger 被杀（SBRendererService 渲染电池页时）会在用户映射还在时释放 BO 页，内核 pmap\_assert\_free panic；PongAdrenoClient 的 dropViews 现在 unmap 并释放映射，NativeAdrenoMemory::release 在页还给 VM 前对每页 pmap\_disconnect（NativeAdrenoDisconnectPages）。
- ASTC 布局修复后，g248 和已安装 watermark 桥接库的 g249 在 DeviceSupportsASTC=1 时自动打开天气 App；各 6 张分段截图均记录完整 135/135 列，主屏与天气画面横跨整屏。g251 时钟和 g252 设置也记录到完整宽度的 App 画面。
- g253、g254 的 GPU 时间线分别完整完成 592/592 和 403/403 笔提交；deadline 看到的 submitted/retired 差 1 是 backboardd 在复位前 26 ms 正常提交的在途工作，不是持续 fence 停滞。
- Photos 的零尺寸断言来自 Tungsten 以 0x0 调用 PXCreateContext；Photos 专用运行时钩子把零轴收敛为 1，g262、g263 和最终内核 g264 均成功进入 Photos，ASTC 开关两组都没有再崩溃。

### Completion criteria

- 主屏和应用由 GPU 渲染，长时间滑动没有 GPU 丢失

### Current limits

- 壁纸扩展不能用 GPU；metal2vulkan 每次提交仍有约 10–20 ms 的 CPU 开销。
- ASTC 修复已自动验证主屏、天气、时钟、设置和 Photos 整幅采样截图；多任务、触摸动画和 Photos 的相册/搜索/编辑路径仍待人工确认，默认仍关闭 ASTC。早先确认过的整机 GPU 丢失仍有 stuck-copy 和 poison 检测。
- Photos 启动与相册首页已自动验证，但首次提示后的网格、搜索、编辑和图片浏览仍需人工操作；IOSurfaceSharedEvent 监听仍缺失。

### Next action

- 支持 IOSurfaceSharedEvent 监听，让壁纸扩展和依赖监听的服务重新使用 GPU 事件。
- 同镜像验证 fairplayd，再测试 display-link WIP，随后按调研顺序处理 nopreamble、BO 缓存、壁纸和截图清晰度。

### Evidence

- `source`: [GPU bring-up、GPU 丢失的诊断和拒绝壁纸扩展的对照实验。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [逐帧 GPU 提交时间线。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-31-frame-timeline.md)
- `host`: [最终 Metal 桥接库和插件构建成功；源码里的 ASTC 格式编号与 iPhoneOS SDK 核对。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-astc-layout.md)
  Command: <code>metal-refresh.sh astc-final 的 bridge / plugin 构建</code>. Revision: `e3be89264924267a610e472e559c9d4d8a66b803`.
- `device`: [ASTC=1，天气 App 在连续 3 张旧格式截图的左侧区域有画面，自动返回 Android；右侧数据缺失。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-astc-layout.md)
  Command: <code>round.sh g247 pong_touch_synth=3 tsa=1118 touch_lat=1 pong_shot=60 pong_shot_ms=1000 pong_astc=1</code>. Revision: `e3be89264924267a610e472e559c9d4d8a66b803`.
- `device`: [watermark 桥接库安装后 ASTC=1，天气启动，主屏与天气 6 张截图完整，自动返回 Android；GPU fence 停滞仍在。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>metal-refresh.sh watermark；cycle.sh g249</code>. Revision: `c9c8fd274c279a8571b525a1e1dbdf8eddf84d9d`.
- `device`: [时钟、设置成功启动且整幅截图完整；照片启动后反复以 PXPixelSizeAreaIsZero 断言退出。每轮均自动返回 Android。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-shot-and-watermark.md)
  Command: <code>cycle.sh g250–g252</code>. Revision: `caa3a06b6b809be46146fc890995b16d51c8a99c`.
- `device`: [两轮时间线无丢失，提交全部完成，零拷贝 fence 无超时；deadline fence 是复位前 26 ms 的正常在途提交。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-fence-diagnostics.md)
  Command: <code>cycle.sh g253、g254；pong_gtrace_delay、pong_gtrace、pong_gtrace_ib</code>. Revision: `a0eb276866aee06a31189f182335760d5a39d4a9`.
- `source`: [记录 ASTC 后续工作、fairplayd 当前镜像状态和 display-link WIP 的未验证边界。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `device`: [钩子把 Tungsten 的 0x0 收敛为 1x1；Photos 不再触发零尺寸断言或退出，最终 ASTC=1 轮次保持运行并自动返回 Android。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-photos-context.md)
  Command: <code>cycle.sh g262–g264；pong_astc=0/1；Photos PXCreateContext 兼容钩子</code>. Revision: `1ebf568205630bc5fa25737ae95392d2908f0e8a`.

## Network {#network}

`host-verified`

Components: `PongPlatform24`.

### Hardware and dependencies

- QCA6490（PCI 17cb:1103）；本机只读导出的固件与 Linux v7.0.14 ath11k 源码，不入仓库

### Configuration

- 默认 GPU 配置仍为 CONFIG\_XNU\_PONG\_WIFI=n、pong\_wifi=0；试验配置 zizhan\_ipados18\_wifi\_defconfig 为 CONFIG\_XNU\_PONG\_WIFI=y，镜像需 WIFI=1 写入 pong\_wifi=1

### Procedure

- 从实机 Android live DT 核对 PCIe0、WLAN GPIO、SID；在隔离试验配置中构建并打包 Wi-Fi 镜像。
- USB 恢复后临时 fastboot boot，按 PCIe、供电、MHI、固件、MSI、扫描顺序定位首个失败阶段。

### Development findings

- 实机 DT 确认 PCIe0、GPIO 80/94/95/96/204、SID 0x1c00/0x1c01；Android 链路为 Gen2 x1。
- 旧 Pong profile 与 zizhan live DT 的 PHY 表有 6 条差异，多出一条本机没有的 WLAN 供电请求；g265/g266 均未启动。
- zizhan profile 经完整 live DT 核验；g267 镜像虽已打包，监视在设备未出现时撤下，未有设备结果。
- 高位 QMI board ID 分支已保留 chip ID 决定的 bdwlan/bdwlang 前缀；三配置重新构建成功，g268 镜像含自动返回参数，实际 QMI ID 仍待设备日志。
- g268 自动轮次的 USB 工具已修正启动失败误报并限制 adb/fastboot 阻塞；CI、GPU、Wi-Fi 三配置再构建通过，仍无设备启动证据。
- g268 镜像内 PWF2 与本机 213 个原始固件文件逐项一致；包内没有高位 board ID 文件，实际 QMI ID 待设备日志。

### Completion criteria

- 扫描到网络并完成关联

### Current limits

- 尚无 Wi-Fi 试验配置的设备启动日志、实际 QMI board ID、扫描或关联证据；USB 当前不可见。默认镜像继续关闭 Wi-Fi。
- 若实际 QMI board ID 超过 0xff，本机导出的固件包没有对应高位命名文件；需先看实际请求名，不能猜测替代。

### Next action

- 恢复 USB 枚举，执行 g268 试验镜像的临时启动和自动返回轮次，取回日志后处理首个失败阶段。

### Evidence

- `source`: [记录了 Wi-Fi 芯片型号。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-28-device-prep.md)
- `host`: [旧 profile 的三配置构建通过，但试验镜像已因板级输入不符撤下，g265/g266 均未启动。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh：zizhan_ipados18_wifi_defconfig、pong_ipados18_ci_defconfig、zizhan_ipados18_gpu_defconfig</code>. Revision: `79ae5b1d7b92f621ac549aec80e73e30e404d649`.
- `host`: [zizhan profile 完整核验；三配置成功，g267 命令行含唯一 Wi-Fi 开关和自动返回；设备尚未启动。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>PONG_WIFI_DTB=&lt;local live DT&gt; ci_kernel.sh：zizhan_ipados18_wifi_defconfig；另构建 pong_ipados18_ci_defconfig、zizhan_ipados18_gpu_defconfig；ci_boot_ufs.sh boot-g267</code>. Revision: `ae24f8a89f41fe2864d997ea3b8005fb1824ae89`.
- `host`: [QMI 扩展 board ID 命名修正后，三配置成功；g268 镜像命令行和自动返回参数检查通过，尚无设备结果。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh：Wi-Fi、CI、GPU 三配置；ci_boot_ufs.sh boot-g268</code>. Revision: `2eab51d14ecc79b3e9b34a4adf65a2b0a81322d8`.
- `host`: [三配置再次成功；adb 可见、未授权、阻塞和 fastboot boot 成败模拟通过；g268 仍未启动设备。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>ci_kernel.sh：CI、GPU、Wi-Fi 三配置；USB 工具模拟</code>. Revision: `890ec93c136a23bbc0e857d0879c3119bf945b83`.
- `host`: [213/213 文件一致；内核和最终镜像均含完整包；无高位 board ID 文件，实际 QMI ID 未知。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>解析 PWF2 目录并逐项 SHA-256 比对本机导出，核对 g268 镜像内嵌固件包</code>. Revision: `0949ebe471d258965f2ef2ae21b44cd1eda13576`.

## Audio {#audio}

`planned`

Components: `PongPlatform24`.

### Hardware and dependencies

- 2 个 CS35L41 功放（地址 0x40、0x42）；公开 zizhan Android DT 给出 SE15 I²C（0x880000）、SDA/SCL（GPIO56/57）和 IRQ（GPIO88/118），共用 GPIO1 复位；启用前须与本机 live DT 核对。Pong 音频代码使用 TFA9873，总线/引脚/地址均不同。

### Configuration

- boot-arg pong\_audio=0；没有 tfa98xx.cnt 时构建一张空功放表

### Procedure

- 保持 pong\_audio=0；先核对本机 live DT 和 I²C 前置条件，再以隔离配置做只读身份探针，最后实现 CS35L41 初始化与 ADSP 播放路由。

### Development findings

- 功放型号与 Pong 不同，Pong 的 TFA9873 路径不能直接用。
- 公开 zizhan Android DT 的两颗 CS35L41 位于 SE15 I²C 0x880000，SDA/SCL 为 GPIO56/57，地址 0x40/0x42，共用 GPIO1 复位；PongAudio.cpp 使用 SE13 0xa94000、GPIO48/49、TFA 地址 0x34/0x35。
- GeniI2c 底层有多字节收发入口，但现有功放包装和寄存器写入是 TFA9873 专用，不能仅改地址。

### Completion criteria

- 扬声器能出声

### Current limits

- 没有 CS35L41 驱动；公开提取 DT 尚未与本机 live DT 再核对，未有音频设备启动或声音证据。

### Next action

- 先核对本机 live DT 的 SE15 时钟、引脚、复位与 IRQ；隔离配置只读 CS35L41 身份，再核对调音/固件与 ADSP 路由，逐段上机验证。

### Evidence

- `source`: [记录了音频不启动的原因和空功放表。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-01-battery.md)
- `source`: [公开提取的 zizhan Android DT 给出 SE15、GPIO56/57、CS35L41 地址和复位/IRQ；本机尚待 live DT 复核。](https://github.com/sm8450-mainline/fdt/blob/3e347601d9e91dd2f1f48e51499823225f7bc0bc/zizhan.dts)
- `source`: [逐项对照 PongAudio.cpp，列出隔离探针的前置条件和未验证边界。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-audio-board-audit.md)

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
- 电池服务类名改为 AppleSmartBattery：PerfPowerServices 的 PLBatteryAgent（hasAppleSmartBattery）和 powerd 的电池健康计算都按这个类名找电池；另外发布 Serial、BatteryData 和 MaximumCapacityPercent。「设置 › 电池 › 电池健康」读到的最大容量为 78 %（3483/4500 mAh）。
- 设置里电池健康的转圈由 batteryDataUnavailable 决定：管理状态来自 thermalmonitord 的 com.apple.thermalmonitor.ageAwareMitigationState（本移植上从不发布），服务状态来自 powerd 电源字典里的 Battery Service State（缺失）。
- USB 拔插时充电状态和电流方向（+300 mA / −520 mA）随之切换（v7）。
- 电池认证：设置先问 MobileGestalt 的 D6/BMDrlb8V3WSiqL8gL+w，为真时要读电池下 AppleAuthCPRelay 的 isTrustedForUI；这块电池没有 Apple 认证芯片，ui\_compat18.c 在 UI 进程里答 false（不适用），不伪造“正品”。

### Completion criteria

- 状态栏和「设置 › 电池」显示正确的电量，插拔充电器有变化；「设置 › 电池」能打开，不卡住

### Current limits

- 「电池健康」一直转圈（管理状态和服务状态缺失）；电池用量图表需要长时间使用才有数据；没有休眠和唤醒。

### Next action

- 让 thermalmonitord 发布 ageAwareMitigationState、让 powerd 写出 Battery Service State，不在设置里伪造“正常”。

### Evidence

- `source`: [ADSP 启动阶段 1–13 全部通过，电池读数与 Android 一致。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-01-battery.md)

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
- ADT 的 /chosen 必须有 unique-chip-id 和 chip-id：没有它们内核不发布 IOPlatformUUID，gethostuuid\(\) 永久阻塞（timed → locationd → contextstored → PowerUIAgent → 「设置 › 电池」卡死）；build-ipados18-bootimg-local.py 传软件种子（不是 Apple 硬件标识）。
- fairplayd.A2 在本移植上启动即退出，launchd 握着 KeepAlive 端口，排队的请求永远没有回复；build-ipados18.py 的 EXCLUDED18 把它移出服务缓存。
- DarwinBoot24 命令行上限 1020 字节：等于默认值的 pong\_ui\_software=0、pong\_software\_ui=0、pong\_ram\_banks=1 不再写入（约 −54 字节）。
- ADT /product 的 udid-version 决定 MobileGestalt 怎么算 UniqueDeviceID：1 要 SerialNumber、ECID、WifiAddress、BluetoothAddress，Wi-Fi 关着时 WifiAddress 的回答让调用者等几秒（设置主线程卡在 -\[ISDefaults init\]，首屏 6.4 s）；有 /chosen 种子时改用 iPhone17,1 自己的 2（ChipID-ECID），首屏 1.2 s。
- 11-02 为调查 Weather 卡住，从 g213 修改前镜像恢复当前 OS 的 fairplayd.A2 job/plist；g245 交接记录为 2560 帧、moving 2453 / 72.0 fps、fairplayd failed lookup 零行，但仍 respawn，功能恢复未验证。EXCLUDED18 仍排除它，全量重建会再移除。

### Completion criteria

- 从本仓库的提交构建出能上机的启动镜像

### Current limits

- Apple 镜像、固件和 ABI 二进制都要在本机准备。
- job-restore.sh 泛化版仅做静态检查，尚未在 Mac / 设备运行；当前已安装镜像与全量重建的 fairplayd 策略不同。

### Next action

- 用这个版本打包启动镜像并上机跑一轮，记录设备结果。
- 同镜像做 fairplayd 有/无对照并核对 Weather / 电池页，决定是否修改 EXCLUDED18；Mac 补做双配置内核及 plugin / UI 构建。

### Evidence

- `source`: [构建链说明。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-29-xnu-bringup.md)
- `host`: [Mac Studio（Apple silicon，Xcode 26.6.0）从全新的构建目录完整编译出 DEVELOPMENT\_ARM64\_PONG 内核，18321080 字节；zizhan 的 boot-arg 字符串（pong\_fts、pong\_panel\_hz、pong\_dpu\_flip 等）与上机使用的内核一致。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/evidence/host-build-zizhan_ipados18_gpu.txt)
  Command: <code>ZIZHAN_SRC=&lt;work dir&gt; ci_prep.sh &amp;&amp; DEFCONFIG=zizhan_ipados18_gpu_defconfig JOBS=10 ci_kernel.sh</code>. Revision: `1ec1190f4e3467a36a7a7402bc766dfdf688adf1`.
- `source`: [区分当前镜像回填和源码 EXCLUDED18，记录 g245 现象及下一项验证，未增加 device-verified 证据。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-02-gpu-astc-and-fairplayd.md)
- `source`: [Wi-Fi 本机输入路径、三配置构建和试验镜像打包记录；无设备结果。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)

## Diagnostics {#diagnostics}

`implemented`

Components: `PongPlatform24`.

### Hardware and dependencies

- ramoops（0x85200000）、logfs 分区、USB（adb 和 fastboot）

### Configuration

- pong\_autoreset=&lt;秒&gt;（默认 300），pong\_autoreset\_sb
- pong\_klog\_4k：内核把 ramoops 区复制到 UFS 上的固定文件
- pong\_gtrace、pong\_gtrace\_delay、pong\_gtrace\_ib、touch\_lat：可定时启动的逐帧时间线

### Procedure

- cycle.sh：fastboot boot 镜像，等看门狗复位回 fastboot，再启动 RamoopsDump 把 ramoops 写进 logfs 并回到 Android，最后经 adb 取回日志。
- panic、长按电源键 3 秒和到点复位都会热复位到 fastboot，DRAM 里的日志保留。

### Development findings

- 整个流程不需要人按键。漏带 pong\_autoreset 的轮次（g152 系列）曾被误判为总线冻结。
- 连续多轮后手机发热，DRAM 里的 ramoops 几乎每行都有位翻转；pong\_klog\_4k 写到 UFS 的副本没有这个问题。
- 带 pong\_url=&lt;秒&gt; 的轮里，SpringBoard 打开 prefs:root=&lt;pong\_pane&gt;（H = 电池健康），settings\_compat18.c 在设置启动后 6/12/20/30 s 打印界面（标签、表格、cell 的 specifier id、转圈、SwiftUI 无障碍元素，非 ASCII 转义为 \\xHH），tools/zizhan/mac/settings-ui.py 解码；无人值守就能判断一个设置页的状态。
- 手势采样器 gs\_all=2（patches/xnu-ipados18/0005）也记录等待中的线程，tools/zizhan/mac/gsym.py 符号化整条栈；用它沿同步 XPC 一路查到 timed 卡在 gethostuuid\(\)。
- pong\_gtrace\_delay 可把提交时间线移到 SpringBoard 后的指定秒数；deadline fence 年龄用于区分持续停滞与自动复位瞬间的在途提交。
- USB 枚举探测有 6 秒上限；fastboot boot 传输有 180 秒上限并保留失败状态，避免把未启动的轮次记为已启动。
- g268 USB 等待任务由用户图形域 launchd 托管，进程父级为 launchd，日志有定期心跳；手机尚未枚举。
- logfs 导出/拉取失败时轮次现在清除本机旧副本并停止，避免把同名历史镜像作为本轮取证。

### Completion criteria

- 每一轮都能自动回到 Android 并取回完整日志

### Current limits

- 日志位翻转与温度有关；cycle.sh 在每轮之前等电池降到 35 °C。
- 11-02 display-link 诊断随 ui\_compat18.c WIP 保存，touch\_lat=1 打印调用方；未构建、未上机。
- g268 等待 USB 恢复，尚无这版自动轮次工具的设备返回证据。

### Next action

- 把 klog 作为默认日志来源。

### Evidence

- `source`: [免按键闭环的设计和轮次记录。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-10-30-root-and-autoloop.md)
- `source`: [四条复位回路的修复。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-01-zero-copy-and-return-paths.md)
- `source`: [公开交接收录 Mac clone 工作流、诊断默认值和验证边界，旧主机同步流程退役。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/CLAUDE.md)
- `source`: [USB 无枚举导致 g265 未启动；fastboot 探测加 6 秒上限，when-back 支持指定试验镜像；主机模拟通过，设备回路尚待恢复。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
- `host`: [失败启动不再被记录为 booted；三配置构建成功。手机未枚举，设备轮次待运行。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>adb-visible.sh 与 fastboot-boot.sh 模拟；CI、GPU、Wi-Fi 三配置构建</code>. Revision: `890ec93c136a23bbc0e857d0879c3119bf945b83`.
- `host`: [等待进程由 launchd 托管并记录心跳；手机仍未枚举，无设备日志或截图。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>launchctl submit g268 when-back；launchctl list 与日志检查</code>. Revision: `5eaa262d46cdb2c3d7a56de28805d57cea548185`.
- `host`: [导出失败、拉取部分文件和空文件都删除旧副本并失败；成功保留新副本；三配置构建通过，设备尚未验证。](https://github.com/qiumochen/UniXNU-zizhan/blob/fe4bff38928dce4b4c2e03a9bf0f4f3dca2cc7fd/docs/progress/2026-11-03-wifi-bringup.md)
  Command: <code>pull-logfs.sh 失败注入四种情况；ci_kernel.sh CI/GPU/Wi-Fi 三配置</code>. Revision: `0a03bab9a4876f1490e453559a24244ffca76958`.

</div>
