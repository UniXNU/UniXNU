# 启动镜像

启动镜像从内存运行。流程启动镜像，并保持已安装的 boot 分区不变。

## 前提

- bootloader 已解锁并支持 `fastboot`。
- 设备的 UEFI 移植与板级配置匹配。
- 已构建带负载的启动镜像，或用空 ramdisk 做启动管理器冒烟测试。
- 板级 UART 可用时准备串口。

## 启动

```sh
fastboot devices
fastboot boot out/<board>/boot/boot.img
```

`fastboot boot` 传输镜像并启动一次。设备原有的 boot 分区和已安装系统保持不变。

启动镜像包含：

| 部分 | 内容 |
| --- | --- |
| kernel | BootShim 和 UEFI 固件卷的 gzip 数据 |
| ramdisk | UniXNU 负载 FAT 卷 |
| 追加数据 | 设备树 |

Android bootloader 加载镜像，校验 BootShim 的 ARM64 header，然后跳转到 shim。BootShim 启动固件卷。

## 启动管理器

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

## Darwin 启动

类型为 `xnu` 的菜单项由 DarwinBoot 读取以下文件：

| 文件 | 必需 | 内容 |
| --- | --- | --- |
| `kernel.macho` | 是 | 预链接 XNU 内核 |
| `kernel.macho.adt` | 是 | Apple 格式设备树 sidecar |
| `kernel.macho.trustcache` | 否 | trust cache 包 |
| 菜单项 `initrd` | 否 | Data ramdisk 种子 |

DarwinBoot 把内核段复制到连续物理窗口，构造 `boot_args`，把 ADT 和 trust cache 地址写入 `/chosen/memory-map` 占位符，然后退出 boot services。

默认窗口为 256 MiB。ADT 属性 `/chosen/darwinboot-memory-size` 可以请求更大的窗口。

## 首次启动

首次启动需要 userdata 镜像。镜像提供 OS 与 SystemOS 卷，以及内核匹配的根卷 UUID。

```sh
fastboot flash userdata out/<board>/userdata/userdata-root.img
fastboot reboot bootloader
fastboot boot out/<board>/boot/boot.img
```

userdata 镜像较大。用 `unixnu build userdata` 构建，并按设备仓库报告中的命令刷写。

Data 种子提供可写 Data 卷。`--skip-setup` 在种子副本中把 Setup 标记为完成，跳过 Hello 页面。步骤和偏好改动见[跳过 Setup](/zh/guide/skip-setup)。

## 日志

板级 UART 可用时，UEFI 固件写到 `EFI_SERIAL_IO_PROTOCOL`，UniXNU 的行以 `UNIXNU:` 开头。

内核在命令行选择串口时写日志，例如 `serial=3`。启动进度层把检查点写到 framebuffer 和串口。

| 来源 | 位置 |
| --- | --- |
| 构建驱动 | `out/<board>/logs/*.log` |
| 启动管理器 | 串口，`UNIXNU:` 行 |
| DarwinBoot | 串口，`DARWINBOOT:` 行 |
| XNU | 串口内核输出 |

## 恢复

镜像从内存运行。复位设备即可回到原有 bootloader 和已安装系统。

```sh
fastboot reboot bootloader
```

固件在菜单前停住时，复位设备并再次启动同一镜像。固件停住后设备仍在 bootloader，第二次 `fastboot boot` 使用同一镜像。

## macOS

启动流程由 IPSW 驱动。macOS 恢复镜像按相同成员布局提供 `KernelCache`、`DeviceTree`、`OS`、`Cryptex1,SystemOS`、`StaticTrustCache` 和 `Cryptex1,SystemTrustCache`。

启动 macOS：

1. 把板级文件的 `[ipsw]` 指向 macOS IPSW，并填入该镜像的产品、版本、build、device class、chip ID 和 board ID。
2. 在 `[ipsw.sha256]` 中固定成员哈希。
3. 把 `[userdata] windows` 设为 `OS` 和 `Cryptex1,SystemOS`。
4. 构建内核、负载、启动镜像和 userdata 镜像。
5. 刷写 userdata 镜像并启动启动镜像。

设备树和平台驱动提供硬件描述，用户态来自 macOS 磁盘镜像。

## 下一步

- [调试与日志](/zh/guide/debugging)
- [userdata 镜像](/zh/guide/userdata)
- [启动参数](/zh/xnu/boot-arguments)
- [故障排查](/zh/reference/troubleshooting)
