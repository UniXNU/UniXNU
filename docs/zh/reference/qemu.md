# QEMU 测试

QEMU 在没有设备时测试 UniXNU、注入路径、DarwinBoot 和内核入口。

## 前提

| 工具 | 用途 |
| --- | --- |
| `qemu-system-aarch64` | AArch64 虚拟机 |
| AAVMF 或 EDK2 AArch64 固件 | UEFI 环境 |
| `dtc` | 设备树编译 |
| `mtools` 或 `pyfatfs` | 块切片测试的 FAT 镜像 |

运行器在常见 Homebrew 和发行版路径查找固件，也可以用 `--firmware` 指定。

## 准备 ESP

```sh
python3 package/Scripts/stage-esp.py -o out/esp \
  package/UniXNUPkg/Test/Qemu/esp \
  --put out/<board>/package/Build/Out/UniXNU.efi=EFI/BOOT/BOOTAA64.EFI \
  --put out/<board>/package/Build/Out/HelloPayload.efi=EFI/UniXNU/Payloads/HelloPayload.efi \
  --put out/<board>/package/Build/Out/SampleDriver.efi=EFI/UniXNU/Kits/SampleDriver.kit/SampleDriver.efi
```

`stage-esp.py` 复制树，把 `.dts` 编译为 `.dtb`，`.dtso` 编译为 `.dtbo`，并把每个 `--put` 文件放到目标位置。

## 运行

```sh
python3 package/Scripts/qemu-run.py out/esp \
  --log out/qemu.log --screenshot out/menu.png \
  --expect 'UNIXNU: menu: shown' \
  --expect 'UNIXNU-HELLO: RESULT PASS'
```

| 选项 | 含义 |
| --- | --- |
| `--firmware FILE` | AAVMF code 镜像 |
| `--log FILE` | 串口日志 |
| `--screenshot FILE` | 菜单出现时的 PNG |
| `--keys LIST` | 菜单后发送的 QEMU 键码 |
| `--expect REGEX` | 必须匹配串口日志 |
| `--reject REGEX` | 必须不匹配 |
| `--no-gop` | 无显示设备，只用文本控制台 |
| `--display-size WxH` | 使用该尺寸的 virtio GPU 显示器代替 ramfb，例如竖屏用 `1080x2400`。固件要求宽度至少 640 像素 |
| `--disk FILE` | 额外只读 raw 磁盘 |
| `--timeout SECONDS` | 运行超时 |
| `--cpus N` | 虚拟 CPU 数量 |
| `--finish-on-expect` | 所有期望匹配后两秒停止 |
| `--menu-marker TEXT` | 触发截图和按键的日志标记 |

运行器通过 QEMU `vvfat` 只读暴露 ESP，抓取串口日志，并通过 QMP 截图和发送按键。

## 冒烟测试

```sh
JOBS=8 bash package/Scripts/smoke.sh
```

脚本构建 package 并运行六个场景：

| 场景 | 检查 |
| --- | --- |
| 默认项 | 设备树补丁、overlay、kit 驱动、initrd、菜单项变量 |
| 键盘 | 下和 Enter 选择第二项 |
| 降级 | 无 GOP、无配置、内置菜单项、文本控制台 |
| 块切片 | FAT 分区头部的配置，尾部发布为块设备 |
| kext 暂存 | revision 2 交接、revision 1 拒绝、非法包、重复 |
| 布局 | 1080x2400 显示器使用竖屏，800x1000 显示器保持横屏 |

日志和截图位于 `package/Build/Smoke/`。

## XNU 入口 fixture

QEMU 入口生成器为内核构建 Apple 格式设备树：

```sh
python3 scripts/qemu-entry/make-dt.py \
  --armvirt --armcpu --smp 2 \
  --owned-memory-size 0x20000000 \
  --output build/qemu-test.adt
```

| 选项 | 含义 |
| --- | --- |
| `--armvirt` | 描述 QEMU virt 设备 |
| `--armcpu` | 加入 GICv3 distributor 和 redistributor |
| `--smp N` | CPU 数量和 PSCI |
| `--owned-memory-size` | DarwinBoot 连续窗口 |
| `--data-ramdisk` | scratch Data 占位符 |
| `--trust-cache` | trust cache 占位符 |
| `--nvram-proxy` | 易失 CHRP NVRAM proxy |
| `--root-match-volume-uuid` | 根卷匹配 |
| `--osenvironment` | `main`、`recoveryos` 或 `ramdisk` |
| `--qemu-vmm-present` | 在 `/defaults` 中报告 VMM |
| `--crypto-hash-method` | Image4 哈希方法 |

生成器描述 QEMU，只使用 QEMU 数值。

## HVF

Apple Silicon macOS 上 QEMU 可以使用 HVF：

```sh
python3 scripts/qemu-entry/make-dt.py --armvirt --armcpu --qemu-vmm-present \
  --qemu-accel hvf --output build/qemu-hvf.adt
```

生成器读取主机计数器频率作为 CPU timebase。bound fixture 用于在内核停点观察实际 `TCR_EL1`、`SCTLR_EL1` 和 `TTBR`。

## 停点

```sh
python3 scripts/qemu-entry/gdb-stop.py --help
```

辅助脚本在符号处停住 QEMU，记录寄存器、内存和最后检查点，输出 JSON 报告。

## 下一步

- [bring-up 顺序](/zh/porting/bring-up)
- [4 KiB 页表](/zh/xnu/four-k-page-tables)
- [故障排查](/zh/reference/troubleshooting)
