# bring-up 顺序

bring-up 按阶段推进。每个阶段都有可见结果和日志行，一次隔离一个问题。

## 阶段 1：UEFI

目标：固件进入 UEFI shell、启动菜单或 UniXNU。

检查：

- 固件卷大小匹配 `[uefi_fd] size`。
- 启动镜像 header 满足 bootloader 要求。
- `fastboot boot boot.img` 启动固件，不复位。
- framebuffer 有输出，或串口有 UEFI 输出。
- 块设备和负载卷可见。

```sh
fastboot boot out/<board>/boot/boot.img
```

固件停住后设备仍在 bootloader，再次启动同一镜像。

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

## 阶段 7：用户态

目标：`launchd` 运行，首个用户进程到达可见状态。

检查：

- `launchd` 从根卷启动。
- Data 卷挂载。
- 显示服务或控制台有输出。
- 启动进度层记录最后检查点。

使用 `boot-progress=2` 和诊断启动参数查看最后完成的检查点。

## 先在 QEMU 验证

QEMU fixture 在没有设备时测试 UniXNU、DarwinBoot 和内核入口：

```sh
python3 scripts/qemu-entry/make-dt.py --armvirt --armcpu --smp 2 \
  --owned-memory-size 0x20000000 --output build/qemu.dtb

python3 package/Scripts/stage-esp.py -o out/esp \
  package/UniXNUPkg/Test/Qemu/esp \
  --put out/<board>/package/Build/Out/UniXNU.efi=EFI/BOOT/BOOTAA64.EFI

python3 package/Scripts/qemu-run.py out/esp \
  --log out/qemu.log --screenshot out/qemu.png \
  --expect "UNIXNU: menu: shown" --expect "DARWINBOOT:"
```

QEMU 运行器启动 AArch64 `virt` 机器和 AAVMF，抓取串口日志，并可以向模拟键盘发送按键。

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
