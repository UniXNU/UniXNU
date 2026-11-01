# 启动镜像

先按[构建指南](/zh/building)完成启动镜像组装。以下流程从 RAM 启动镜像，依次检查菜单、加载器和内核。

使用 `./unixnu build firmware --uefi ../uefi-<device>` 构建固件。Mu-Silicium initrd 负载需要在固件中加入 `UniXNURamDiskDxe`、DiskIoDxe 和 FAT 支持，并在 `./unixnu bootimg` 前构建负载。[固件集成指南](/zh/porting/uefi-firmware#required-integration)列出了必需的 DSC/FDF 条目和菜单检查步骤。

重复构建时，在 [unixnu.local.toml](/zh/reference/configuration#local-build-inputs) 保存路径。修改启动参数后，按[参数应用流程](/zh/xnu/boot-arguments#apply-arguments)重新构建负载和启动镜像。画面停在加载器交接阶段时，按[绿条诊断](/zh/guide/debugging#green-bar)检查。

## 1. 核对输入 {#前提}

- bootloader 已解锁并支持 `fastboot`。
- 设备的 UEFI 移植与板级配置匹配。
- 已构建带负载的启动镜像，或用空 ramdisk 做启动管理器冒烟测试。
- 板级 UART 可用时准备串口。

## 2. 准备根卷 {#首次启动}

使用 userdata 根卷布局的设备，首次启动根卷前需要安装该镜像。镜像提供 OS 与 SystemOS 卷，以及内核匹配的根卷 UUID。

安装或替换根镜像时执行下方刷写命令。设备已有匹配的根镜像时，继续步骤 3。

刷写 `userdata` 会覆盖该分区。执行前确认目标设备、分区布局和报告中的镜像路径，并保存需要保留的分区数据。

```sh
fastboot devices
fastboot flash userdata out/<device>/<os_profile>/<config>/userdata/userdata-root.img
fastboot reboot bootloader
```

userdata 镜像较大。用 `unixnu build userdata` 构建，并按设备仓库报告中的命令刷写。

Data 种子提供可写 Data 卷。`--skip-setup` 在种子副本中把 Setup 标记为完成，跳过 Hello 页面。步骤和偏好改动见[跳过 Setup](/zh/guide/skip-setup)。

## 3. 启动镜像 {#启动}

```sh
fastboot devices
fastboot boot out/<device>/<os_profile>/<config>/boot/boot.img
```

`fastboot boot` 传输镜像并启动一次。运行后的 payload 遵循已配置的存储和安装策略。

启动镜像包含：

| 部分 | 内容 |
| --- | --- |
| kernel | BootShim 和 UEFI 固件卷的 gzip 数据 |
| ramdisk | UniXNU 负载 FAT 卷 |
| 追加数据 | 设备树 |

Android bootloader 加载镜像，校验 BootShim 的 ARM64 header，然后跳转到 shim。BootShim 启动固件卷。

## 4. 确认启动菜单 {#启动管理器}

UniXNU 把版本和配置摘要写到串口并绘制菜单。默认配置包含超时、默认项和倒计时。

| 操作 | 按键 |
| --- | --- |
| 移动高亮 | 上、下 |
| 启动选中项 | Enter |
| 停止倒计时 | 任意键 |
| 确认菜单项 | Enter |
| 取消确认 | 没有选项时任意键，或在 Cancel 上按 Enter |
| 选择确认选项 | 上、下，然后 Enter |

带 `confirm` 的菜单项在启动前显示问题。倒计时跳过需要确认的菜单项。给出 `confirm_titles` 时，Cancel 默认选中，选中的 `confirm_args` 追加到菜单项参数。见[启动配置](/zh/reference/boot-configuration)。

菜单项来自 `\EFI\UniXNU\unixnu.toml`。菜单项可以启动 EFI 程序、带 EFI stub 的 Linux、执行动作，或通过加载器协议启动 Darwin 内核。

UniXNU 找不到配置时，会扫描每个卷的 `\EFI\BOOT\BOOTAA64.EFI`，把这些菜单项加到内置动作之前。

## 5. 确认加载器交接 {#darwin-启动}

类型为 `xnu` 的菜单项由 DarwinBoot 读取以下文件：

| 文件 | 必需 | 内容 |
| --- | --- | --- |
| `kernel.macho` | 是 | 预链接 XNU 内核 |
| `kernel.macho.adt` | 是 | Apple 格式设备树 sidecar |
| `kernel.macho.trustcache` | 否 | trust cache 包 |
| 菜单项 `initrd` | 否 | Data ramdisk 种子 |

DarwinBoot 把内核段复制到连续物理窗口，构造 `boot_args`，把 ADT 和 trust cache 地址写入 `/chosen/memory-map` 占位符，然后退出 boot services。

默认窗口为 256 MiB。ADT 属性 `/chosen/darwinboot-memory-size` 可以请求更大的窗口。

## 6. 保存日志 {#日志}

板级 UART 可用时，UEFI 固件写到 `EFI_SERIAL_IO_PROTOCOL`，UniXNU 的行以 `UNIXNU:` 开头。

内核在命令行选择串口时写日志，例如 `serial=3`。启动进度层把检查点写到 framebuffer 和串口。

| 来源 | 位置 |
| --- | --- |
| 构建驱动 | `out/<device>/<os_profile>/<config>/logs/*.log` |
| 启动管理器 | 串口，`UNIXNU:` 行 |
| DarwinBoot | 串口，`DARWINBOOT:` 行 |
| XNU | 串口内核输出 |

## 把 payload 放进 vendor_boot {#vendor-boot-负载}

超过几 MB 的 payload 放不进 `boot`。GKI 设备的 `boot` 本身没有 ramdisk
（`ramdisk_size` 为 0），厂商 ABL 也会拒绝带 ramdisk 的 boot 镜像，因此 payload
属于 `vendor_boot` 的 `vendor_ramdisk` 字段，`./unixnu bootimg` 用 `--ramdisk none`
运行。

三个上限决定镜像能否被接受：

- **窗口**。原厂 `vendor_boot` header 把 ramdisk 放在 `0x01000000`、设备树放在
  `0x01f00000`，只剩 15 MiB。payload 超过这个大小前要用 `--ramdisk-addr` 重新定位，
  否则会覆盖设备树。
- **分区**。重建后的镜像必须放得进分区。末尾 64 字节的 AVB footer 会被重新指向
  vbmeta blob，因此不需要删掉 footer。
- **文件系统**。固件按 FAT 挂载 ramdisk。`mformat -F` 可能生成固件读不了的卷；
  `mformat -T 8192 -h 64 -s 32` 生成的 FAT16 卷可以挂载。

菜单会以 `payload: initrd <起>-<止> [<id>] fs <n>` 报告结果。`fs 0` 表示块设备存在但
没有可读文件系统；完全没有 payload 行则表示 ramdisk 没到达加载器。

## 只有屏幕可用时 {#屏幕诊断}

没有串口的板子只能在帧缓冲上报告进度，加载器和内核各有自己的信号：

- DarwinBoot 在跳转内核前把帧缓冲顶部十六分之一刷成绿色。出现绿带表示内核之前的
  所有阶段都已通过。
- 可选的入口探针在绿带下方按阶段各画一条：蓝色是内核入口（MMU 关闭），品红色是
  即将开启 MMU 之前；配合 `entry_probe_reset_delay` 会在 MMU 开启后若干秒通过 PSCI
  复位，把"CPU 走到了这一步"变成一次重启。
- `payload.panic_screen = true` 会打补丁，让 panic 把格式串画到内核自己的帧缓冲映射上。
  它与第四阶段探针共用 `_start` 之后的零填充，二者不能同时启用。
- `entry_probe_reset_after` 用来二分 `_arm_init`：在指定调用之后复位，说明内核已从该
  调用返回。

加载器失败前画出的诊断会在菜单重绘时被立即覆盖。只能靠拍照留证时，应在失败路径上
让屏幕停留数秒。

## 恢复

使用设备硬件复位方式返回 bootloader。fastboot 响应后，以下命令可重启 bootloader：

```sh
fastboot reboot bootloader
```

固件在菜单前停止响应时，保存最后输出，复位进入 bootloader 并用 `fastboot devices` 确认连接。再次尝试前按[启动验证](/zh/porting/bring-up)检查固件输入。

## macOS

macOS 移植需要匹配其 XNU 版本、kernelcache、预链接 roots、私有驱动 ABI、trust cache 和根卷布局的 OS profile。
按[内核准备](/zh/guide/build-kernel)与[预链接](/zh/concepts/prelink)确认这些输入。
仓库提供的 `ipados-17.7.11-21H461` profile 描述名称所示的 iPadOS 构建。

将完成的 OS profile 设为 `board.os_profile`，检查 `status --json`，再重复构建和启动验证流程。
macOS 结果须关联该 profile 与目标设备。

## 下一步

- [调试与日志](/zh/guide/debugging)
- [userdata 镜像](/zh/guide/userdata)
- [启动参数](/zh/xnu/boot-arguments)
- [故障排查](/zh/reference/troubleshooting)
