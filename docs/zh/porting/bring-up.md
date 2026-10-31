# bring-up 顺序

bring-up 按阶段推进。每个阶段都有可见结果和日志行，一次隔离一个问题。

重复构建时，在 [unixnu.local.toml](/zh/reference/configuration#local-build-inputs) 保存路径。修改启动参数后，按[参数应用流程](/zh/xnu/boot-arguments#apply-arguments)重新构建负载和启动镜像。画面停在加载器交接阶段时，按[绿条诊断](/zh/guide/debugging#green-bar)检查。

启用外设前完成对应[适配流程](/zh/porting/drivers)，按[构建指南](/zh/building)生成镜像，再依次检查以下阶段。失败后先保存镜像和最后日志，再修改输入。

## 阶段 1：UEFI

目标：固件进入 UEFI shell、启动菜单或 UniXNU。

检查：

- 固件卷大小匹配 `[uefi_fd] size`。
- 启动镜像 header 满足 bootloader 要求。
- `fastboot boot boot.img` 启动固件，不复位。
- framebuffer 有输出，或串口有 UEFI 输出。
- 块设备和负载卷可见。Mu-Silicium initrd 负载需要在 FD 中包含 `UniXNURamDiskDxe`、DiskIoDxe 和 FAT，详见[固件集成](/zh/porting/uefi-firmware#required-integration)。

```sh
fastboot boot out/<device>/<os_profile>/<config>/boot/boot.img
```

固件停止响应时，复位进入设备 bootloader，用 `fastboot devices` 确认连接，重试前保存最后的固件输出。

## 阶段 2：UniXNU

目标：菜单出现，配置解析成功。

检查：

- 串口行以 `UNIXNU:` 开头。
- 日志报告 entry、driver、patch、ACPI、slice 和 kit 数量。
- 菜单列出预期项。
- 驱动失败显示数量和第一条失败原因。

最小测试：空 ramdisk。UniXNU 使用内置配置并列出可移动加载器。

```sh
./unixnu bootimg --uefi /path/to/Mu-Silicium --dtb board.dtb --ramdisk none
```

继续前，按[二维码抓取步骤](/zh/porting/log-capture#qr-logs)从 **Tools → Advanced Logger**
导出当前固件日志。先按[集成步骤](/zh/porting/log-capture#firmware-setup)准备平台日志模块和插件。

## 阶段 3：负载

目标：UniXNU 读取 `unixnu.toml` 和负载文件。

检查：

- 日志报告配置路径。
- `xnu` 菜单项存在。
- 负载报告哈希与卷中文件一致。
- ADT sidecar 位于内核旁边。

负载错误在 DarwinBoot 启动前可见。

## 阶段 4：DarwinBoot

目标：DarwinBoot 校验内核、ADT 和 trust cache，退出 boot services。

检查：

- 串口行以 `DARWINBOOT:` 开头。
- 打印虚拟基址、物理基址、参数地址、入口地址。
- 打印 framebuffer 基址、宽、高和深度。
- 异常级别为 EL1。
- bootstrap 页表路径到达内核入口。

拒绝时打印 `DARWINBOOT: boot refused: <status>; firmware retained`，固件继续运行并回到菜单。

## 阶段 5：内核入口

目标：XNU 启动并到达平台专家。

检查：

- 内核打印版本和启动参数。
- bootstrap 页表映射内核窗口。
- 平台专家匹配 ADT 根节点。
- `/cpus`、`/arm-io`、`/defaults`、`/options` 和 NVRAM proxy 存在。

内核在视频控制台出现前停止时，会改为显示颜色条。见[颜色条](/zh/guide/debugging#颜色条)。

缺少平台 provider 时 panic 会给出 provider 名称。加入驱动或修正 ADT。

## 阶段 6：存储与根卷

目标：块驱动发布 userdata 分区，卷出现，XNU 挂载根卷。

检查：

- 存储驱动打印链路速度和命令队列。
- 分区方案发布 `OS` 和 `SystemOS`。
- 根卷 UUID 匹配 `root_match_volume_uuid`。
- 内核挂载根卷并启动 `launchd`。

根卷匹配失败时内核没有根设备。检查 UUID、窗口偏移和分区容量。

存储可用后，按[持久化日志步骤](/zh/porting/log-capture#persistent-logs)接入写入器和 Linux 或 recovery 读取器，先手动取回一次日志，再启用定时重启和自动循环。

## 阶段 7：用户态

目标：`launchd` 运行，首个用户进程到达可见状态。

检查：

- `launchd` 从根卷启动。
- Data 卷挂载。
- 显示服务或控制台有输出。
- 启动进度层记录最后检查点。

使用 `boot-progress=2` 和诊断启动参数查看最后完成的检查点。

## 先在 QEMU 验证

按 [QEMU 测试](/zh/reference/qemu)准备 ESP 并运行菜单/payload fixture。
XNU 入口 fixture 需要一起放入 ARM64 内核、ADT sidecar 和 DarwinBoot。
运行前检查选定启动项及预期检查点。

```sh
JOBS=8 bash package/Scripts/smoke.sh
```

安装 QEMU 前置工具后从主仓库运行。该命令检查 UEFI package 场景，将日志和截图写入
`package/Build/Smoke/`。内核工作按 [QEMU 指南](/zh/reference/qemu)的 XNU 入口步骤操作。
外设结果在目标设备上记录。

## 失败隔离

| 现象 | 首先检查 |
| --- | --- |
| 固件无输出 | 启动镜像 header、固件基址和大小、bootloader 日志 |
| 固件有输出，无菜单 | GOP 驱动、UniXNU 路径、`unixnu.toml` |
| 菜单存在，无负载项 | 负载卷标、FAT 驱动、菜单项路径 |
| 有负载项，无 DarwinBoot 日志 | 加载器协议、固件卷中的 DarwinBoot |
| DarwinBoot 拒绝 | 内核 Mach-O、ADT、trust cache、占位符 |
| 内核入口无日志 | 启动参数、串口选择、framebuffer 地址 |
| panic 给出 provider | ADT 节点、驱动静态库、内核开关 |
| 无根卷 | userdata 镜像、UUID、分区容量 |

## 下一步

- [故障排查](/zh/reference/troubleshooting)
- [QEMU 测试](/zh/reference/qemu)
- [启动参数](/zh/xnu/boot-arguments)
- [调试与日志](/zh/guide/debugging)
