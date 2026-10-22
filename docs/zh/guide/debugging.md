# 调试与日志

bring-up 需要四类证据：串口输出、屏幕诊断页、panic 屏幕和构建报告。把它们一起收集。

## 日志来源

| 来源 | 通道 | 用途 |
| --- | --- | --- |
| UEFI 串口 | UART | 固件、UniXNU、DarwinBoot |
| 内核串口 | 由 `serial=` 选择的 UART | XNU 控制台和 panic 输出 |
| 诊断页 | framebuffer | 控制台停止后的实时状态 |
| 脉冲条 | framebuffer 底部 | 诊断页占用面板时的心跳 |
| panic 屏幕 | framebuffer | panic 文本和寄存器 |
| QEMU 日志 | 文件 | UniXNU 和加载器测试 |
| 构建报告 | JSON | 输入哈希和阶段结果 |

## 串口

把参数加入负载：

```toml
[payload]
kernel_args = ["-v", "serial=3", "debug=0x14e"]
```

UniXNU 启动管理器写到第一个 `EFI_SERIAL_IO_PROTOCOL`，行以 `UNIXNU:` 开头。DarwinBoot 的行以 `DARWINBOOT:` 开头。

抓取串口：

```sh
tio -b 115200 -d 8 -p none -s 1 /dev/tty.usbserial-0001 -L out/serial.log
```

其他工具：

```sh
picocom -b 115200 /dev/tty.usbserial-0001
screen -L /dev/tty.usbserial-0001 115200
minicom -D /dev/tty.usbserial-0001 -b 115200
```

设备页面记录 UART 引脚和波特率。支持 USB device 模式的板子可以暴露 CDC ACM 串口。

常用的早期输出：

```
UNIXNU: UniXNU 0.1.0 starting as firmware boot option
UNIXNU: config: loaded \EFI\UniXNU\unixnu.toml
UNIXNU: driver ...: started
UNIXNU: menu: shown 2 entries, default 0
DARWINBOOT: loader v2 installed EL1
DARWINBOOT: ARM64 va=... pa=... args=... entry=... owned=...
DARWINBOOT: inputs validated; exiting boot services
```

## 屏幕诊断页

诊断页是绘制到 XNU framebuffer 映射上的全屏文本覆盖层。启用方式：

```
boot-progress=1
```

级别 1 启动监视器。30 秒没有阶段或存储活动，或达到 120 秒观察上限时，页面冻结并保留屏幕，便于拍照。

```
boot-progress=2
```

级别 2 连续运行。超过时限只报告，系统继续运行。

页面使用 48 行、120 列。面板至少 2160x1400 时缩放为 3。

| 行区域 | 内容 |
| --- | --- |
| 标题 | 构建标签、live 或 stop 状态、原因 |
| 1 | 时间、空闲、IRQ 计数、监视器计数、root 状态、进程数、空闲页 |
| 2 | 存储请求、已验证块、失败、完整性计数 |
| 3 到 30 | 阶段历史、进程状态、存储细节、最后 PC 和寄存器 |
| 31 到 47 | 缓存存储输出、UFS 计时、内存、进程采样、UI trace、触控行 |
| 47 | 独立脉冲条 |

给镜像加标签，拍照后可以确认构建：

```
sheng-build-tag=ks-001
```

标题栏会以 `[ks-001]` 开头。

用户态接管显示并停止扫描输出后，可以收回面板：

```
boot-diag-resume=10
```

10 秒没有 scanout 后页面重绘。新的有效 scanout 会再次让出面板。

页面字段：

| 字段 | 含义 |
| --- | --- |
| `time` | 监视器启动后的秒数 |
| `idle` | 距上次阶段或 I/O 进展的秒数 |
| `IRQ` | 监视器统计的中断入口数 |
| `monitor` | 监视器线程迭代数 |
| `lost` | 丢弃的记录更新数 |
| `root` | owner root 接受状态 |
| `procs` | 进程数 |
| `free` | 空闲 4 KiB 页 |
| `requests` | 存储请求 |
| `verified4K` | 已验证 4 KiB 块 |
| `failures` | 存储失败 |
| `integrity` | 存储完整性失败 |
| `last PC` | 最后中断入口 PC |
| `TCR`、`TTBR`、`SCTLR` | 翻译控制和页表基址寄存器 |

## 脉冲条

脉冲条位于面板底部，高 32 像素，2 倍缩放，绿色文字，由独立高优先级监视线程每秒更新。

```
P<turn> I<irq> M<monitor>/<seconds> B<bind>:<result> d<depth> @<base> lock<busy>/<render> PC<pc>
```

| 字段 | 含义 |
| --- | --- |
| `P` | 脉冲轮次 |
| `I` | 中断入口数 |
| `M` | 监视器计数和距上次推进的秒数 |
| `B` | framebuffer 绑定次数、结果和深度 |
| `@` | framebuffer 基址 |
| `lock` | 记录器和渲染器忙碌标志 |
| `PC` | 最后中断入口 PC |

诊断页占用面板时脉冲条持续存在。OS 接管显示后它关闭。`boot-diag-resume` 会重新打开诊断页和脉冲条。

## panic 屏幕

负载可以把 panic 屏幕打进内核副本：

```toml
[payload]
panic_screen = true
```

负载步骤运行：

```sh
python3 scripts/patch-xnu-entry-probe.py <kernel> --panic-screen --no-reset
```

panic 屏幕把格式化后的 panic 消息和寄存器写到 framebuffer，并保持显示。`--no-reset` 停止自动复位，屏幕保留到拍照完成。

### 颜色条

早期启动会在 framebuffer 上画三条 1/16 屏幕高度的色条。正常方向下从上到下：

| 色条 | 绘制者 | 含义 |
| --- | --- | --- |
| 绿色 | DarwinBoot `DarwinEnter` | 已退出 boot services，控制权到达内核入口 |
| 蓝色 | 入口探针阶段 1 | 内核入口代码已执行，MMU 仍关闭 |
| 品红 | 入口探针阶段 2 | 内核到达打开 MMU 之前的位置 |

入口探针把每条画在绿色条下方。阶段 3 没有色条：它在 MMU 打开后等待 `--reset-delay` 秒再复位。过了这段时间设备重启，说明 MMU 已打开。

### 入口探针复位

内核还不能绘图之前，重启是唯一的信号。`entry_probe_reset_delay` 保留入口探针的复位：打过补丁的内核在 MMU 打开后等待这么多秒，然后用 PSCI SYSTEM_RESET 复位。过了这段时间设备自己重启，说明 CPU 已经通过 MMU 打开这一步。

```toml
[payload]
entry_probe_reset_delay = 6
entry_probe_reset_after = "_arm_vm_init"   # 可选：改为在这个调用之后复位
entry_probe_reset_in = "_arm_init"         # 发出调用的函数（默认值）
entry_probe_reset_occurrence = 1           # 第几次调用（默认 1）
entry_probe_reset_before = false           # 在调用点复位，不执行调用，也不等待
```

设置 `entry_probe_reset_after` 后，复位移到该调用之后，一次运行只回答一个问题：内核有没有走过这个调用。这些键对应板级 `patch-xnu-entry-probe.py` 的 `--reset-delay`、`--reset-after`、`--in`、`--occurrence` 和 `--reset-before`，可以和 `panic_screen` 同时使用。不设置 `entry_probe_reset_delay` 时，负载仍传 `--no-reset`。

第一条 panic 消息也会复制到 `boot_progress_panic_text`。secondary core 上的 panic 只停住该 core，实时横幅在屏幕重绘后仍保留文本。

设备树 panic 区域需要：

```
CONFIG_XNU_DT_PANIC_REGION=y
```

内核读取 `/chosen` 的 `embedded-panic-log-size` 和区域的 `reg` 属性，映射前先校验。

## 用户态故障证据

故障探针在异常投递前记录 EL0 breakpoint 和 abort 状态：

| 字段 | 含义 |
| --- | --- |
| `pid`、`name` | 进程 |
| `PC`、`LR`、`SP`、`FP` | 故障时寄存器 |
| `ESR`、`FAR` | 异常综合征和故障地址 |
| `slide` | shared region slide |
| `x0` 到 `x28` | 通用寄存器 |
| frames | 最多 12 个返回地址 |

捕获在 trap 路径中完成，不分配内存。匹配的进程退出时，记录随信号打印。未捕获异常的原因会从退出进程的可写 malloc 区域中搜索并打印到崩溃行。

## UI 栈追踪

UI trace 采样指定进程，打印 PC、LR、FP 和栈切片：

```
boot-ui-focus=launchd
boot-ui-focus2=SpringBoard
boot-ui-focus3=backboardd
boot-ui-focus4=Setup
boot-ui-chrono=1
```

地址使用 64 进制字母表编码，以适配行宽。把抄录的行交给解码器：

```sh
python3 scripts/decode-boot-ui-trace.py trace.txt
```

解码器为每个线程组输出一个 JSON 对象，包含 `pc`、`lr`、帧和错误码。

trace 每 8 秒轮换一页。间隔几秒拍三到四张照片，覆盖全部页面。

## 拍照

诊断页按拍照场景设计。建议流程：

1. 把 `sheng-build-tag` 设为简短的镜像标签。
2. 冻结页面用 `boot-progress=1`，实时页面用 `boot-progress=2`。
3. 用户态会清屏时设置 `boot-diag-resume`。
4. 把设备放在支架上，相机与面板平行。
5. 关闭闪光灯，从侧面打光，避免反射。
6. 对标题栏锁定焦点和曝光。
7. 让面板填满画面，包含四个角。
8. 先拍标题栏，再拍整页。
9. UI trace 页面间隔 8 秒拍三到四张。
10. 拍底部脉冲条。
11. 记录启动镜像 SHA-256 和拍摄时间。

| 检查项 | 原因 |
| --- | --- |
| 标题栏可读 | 构建标签和状态标识镜像 |
| 文字区域无眩光 | 第 3 到 30 行承载阶段历史 |
| 四角可见 | 确认完整面板和缩放 |
| 脉冲条可见 | 显示拍摄时的心跳 |
| 至少两张 | 变化的计数器说明屏幕在实时更新 |

相机照片是面板显示内容的证据。保留原始文件。只抄录需要的行，并把照片与抄录一起保存。

## QEMU 抓取

```sh
python3 package/Scripts/qemu-run.py out/esp \
  --log out/qemu.log --screenshot out/qemu.png \
  --expect 'UNIXNU: menu: shown'
```

运行器把去掉 ANSI 的日志写到 `out/qemu.clean.log`。`--screenshot` 在菜单出现时截屏。`--keys` 在菜单后发送 QEMU 键码。

停止辅助脚本在指定符号处记录寄存器和内存：

```sh
python3 scripts/qemu-entry/gdb-stop.py --help
```

## 调试参数

| 参数 | 用途 |
| --- | --- |
| `-v` | 详细内核输出 |
| `serial=3` | 串口控制台 |
| `debug=0x14e` | 调试输出掩码 |
| `kextlog=0xfff` | kext 日志 |
| `boot-progress=1` | 诊断页，30 秒停滞后冻结 |
| `boot-progress=2` | 诊断页连续运行 |
| `sheng-build-tag=<tag>` | 标题栏镜像标签 |
| `boot-diag-resume=<seconds>` | OS 停止 scanout 后收回面板 |
| `sheng-platform-stage=<n>` | 在平台专家阶段停住 |
| `sheng-touch=<n>` | 触控探针阶段 |
| `offline-legacy-phase=<n>` | 显示探针阶段 |
| `-no_slto_panic` | 关闭 SLTO panic |
| `cs_debug=<mask>` | 代码签名输出 |

## 证据包

收集：

| 项目 | 来源 |
| --- | --- |
| 串口日志 | UART 抓取文件 |
| 诊断照片 | 标题栏、整页、trace 页、脉冲条 |
| panic 照片 | panic 屏幕 |
| 启动报告 | `out/<board>/boot/boot.json` |
| 负载报告 | `out/<board>/payload/payload.json` |
| 构建日志 | `out/<board>/logs/` |

每张照片都记录启动镜像哈希：

```sh
shasum -a 256 out/<board>/boot/boot.img
jq . out/<board>/boot/boot.json
```

## 下一步

- [启动参数](/zh/xnu/boot-arguments)
- [故障排查](/zh/reference/troubleshooting)
- [QEMU 测试](/zh/reference/qemu)
- [sheng 设备页](/zh/devices/sheng)
