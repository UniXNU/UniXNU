# UniXNU 分区 (实验性)

`scripts/dual_sys/partition.py` 通过 ADB 识别设备和分区布局，先缩小 F2FS，再从 `userdata` 尾部创建 `unixnu` 分区。新分区容量以 GiB 指定。

保留 userdata 的起始位置、类型、GUID 和属性。新块设备为 `/dev/block/by-name/unixnu`；格式化、系统安装和启动配置需另行完成。

## 支持的布局

| 要求 | 接受的状态 |
| --- | --- |
| 主机 | Python 3.10 或更新版本、Android platform-tools，无需安装 Python 包 |
| Recovery | 支持设备的 TWRP，ADB 具有 root 权限，能够解密 `/data` |
| 内核 | 实现用于在线缩容的 `F2FS_IOC_RESIZE_FS`，需要验证该设备的 recovery 内核 |
| 文件系统 | F2FS，块大小为 4096 字节，每个 segment 为 512 块，每个 section 只有一个 segment，启用 checkpoint |
| 加密映射 | 直接使用 userdata，或仅由 userdata 支撑、覆盖整个分区的一层 device-mapper 映射 |
| 分区表 | 主、备 GPT 一致，逻辑扇区为 512 或 4096 字节，使用常规的 128 字节分区项 |
| 分区位置 | `userdata` 是最后一个已占用分区，存在空闲 GPT 分区项，尚未创建 `unixnu` |
| Recovery 命令 | `sh`、`dd`、`blockdev`、`sha256sum`、`cmp`、`readlink`、`sync`、`umount` |

遇到 Ext4、多设备或 zoned F2FS、多 segment section、尾部加密元数据、多层映射或中间分区时停止。

## 准备 recovery（分区备份可选）

1. 进入兼容的 TWRP。已安装时可执行：

   ```sh
   adb reboot recovery
   adb devices -l
   ```

2. 检查设备和 GPT。连接多台设备时，每条主机脚本命令添加 `--serial SERIAL`。

   ```sh
   python3 scripts/dual_sys/partition.py inspect
   ```

3. 可选：保存原始启动/recovery 镜像，将离线的 `userdata` 和 `metadata` 成对备份到另一块物理磁盘。TWRP 文件级备份可能缺少加密元数据。跳过分区备份时，直接进入第 4 步。

   关闭 MTP，卸载 Data、绑定挂载和 Metadata。确认分区及其解密设备均未挂载：

   ```sh
   adb -s SERIAL shell cat /proc/mounts
   adb -s SERIAL shell readlink -f /dev/block/by-name/userdata
   adb -s SERIAL shell readlink -f /dev/block/by-name/metadata
   ```

   确认离线后，在主机 POSIX shell 中复制。替换备份路径和 `SERIAL`：

   ```sh
   mkdir -p /external-disk/phone-backup
   adb -s SERIAL exec-out 'dd if=/dev/block/by-name/metadata bs=1048576 2>/dev/null' \
     > /external-disk/phone-backup/metadata.img
   adb -s SERIAL exec-out 'dd if=/dev/block/by-name/userdata bs=1048576 2>/dev/null' \
     > /external-disk/phone-backup/userdata.img
   adb -s SERIAL shell blockdev --getsize64 /dev/block/by-name/metadata
   adb -s SERIAL shell blockdev --getsize64 /dev/block/by-name/userdata
   wc -c /external-disk/phone-backup/metadata.img /external-disk/phone-backup/userdata.img
   shasum -a 256 /external-disk/phone-backup/metadata.img /external-disk/phone-backup/userdata.img
   ```

   确认复制成功，文件大小与对应设备一致。Windows 使用支持二进制传输的备份工具，避免 PowerShell 文本管道。保留这些备份。

4. 重启 TWRP，解密 Data 并以读写方式挂载 `/data`。保持 MTP 关闭，退出占用 `/data` 的程序：

   ```sh
   adb -s SERIAL reboot recovery
   adb -s SERIAL wait-for-device
   # 在 TWRP 中解密并挂载 Data，然后检查。
   adb -s SERIAL shell cat /proc/mounts
   ```

5. 跳过相关分区的备份是可接受的。请注意在缩容前备份重要数据。

## 编译 recovery 辅助程序

架构须匹配 `inspect` 的输出。AArch64 手机可在 Linux 上交叉编译静态辅助程序：

```sh
mkdir -p out/dual_sys
aarch64-linux-gnu-gcc -static -O2 -Wall -Wextra -Werror \
  scripts/dual_sys/f2fs-shrink.c -o out/dual_sys/f2fs-shrink
file out/dual_sys/f2fs-shrink
```

确认输出为 AArch64 静态 ELF，也支持静态 musl 构建。主机脚本检查架构后上传到 recovery 的 `/tmp`。

## 预览分区方案

示例：为 UniXNU 预留 32 GiB。

```sh
python3 scripts/dual_sys/partition.py plan \
  --size-gib 32 --helper out/dual_sys/f2fs-shrink \
  --output out/dual_sys/preview
```

`--size-gib` 为正数，以整数 MiB 为步长，如 `32`、`32.5`。容量等于请求值，边界按 1 MiB 对齐，尾部不足 1 MiB 的空间留空。核对输出布局，并使用新输出目录。

`plan` 检查 GPT、F2FS、可用空间和设备映射，仅写入主机文件及 recovery 的 `/tmp`。

| 文件 | 用途 |
| --- | --- |
| `plan.json` | 设备身份、原始文件系统状态和计算后的分区范围 |
| `gpt-primary.before`、`gpt-backup.before` | 原始 GPT 区域，主表区域包含保护 MBR |
| `gpt-primary.after`、`gpt-backup.after` | 计划写入的 GPT 区域 |
| `plan.env` | 传给 recovery 脚本的设备路径、容量和预期结果 |
| `twrp.sh`、`f2fs-shrink` | Recovery 执行脚本与已编译辅助程序 |
| `SHA256SUMS` | 检查上传是否完整、生成文件是否发生变化 |

保留完整方案目录；如已备份 userdata/metadata，可一并保存。GPT 备份不能恢复丢失的文件内容。

## 执行分割

`apply` 重新生成方案，使用相同容量和新输出目录。

```sh
python3 scripts/dual_sys/partition.py apply \
  --size-gib 32 --helper out/dual_sys/f2fs-shrink \
  --output out/dual_sys/applied
```

核对设备和布局，完整输入显示的确认短语。执行期间保持供电，不操作 TWRP。

执行顺序：

1. 复核上传文件、设备、内核和 GPT。
2. 通过内核缩小 F2FS。
3. 检查两份超级块均落在新 userdata 范围内。
4. 卸载 `/data`，拒绝残留挂载。
5. 写入并读回备份 GPT，再处理主 GPT；主机复核两份表。

`metadata` 保持原样，`/data` 保持卸载，需手动重启 recovery 刷新分区表。GPT 按 [UEFI 规范](https://uefi.org/specs/UEFI/2.9_A/05_GUID_Partition_Table_Format.html)先写备份表，再写主表。

主机调用 `twrp.sh` 并使用生成的 `plan.env`。手动检查时，替换为输出中的 recovery 目录：

```sh
adb -s SERIAL shell 'sh /tmp/unixnu-dual-REPLACE_WITH_PRINTED_ID/twrp.sh check'
```

方案仅适用于当前设备和 recovery 会话。执行时使用主机 `apply` 生成新方案。

## 重启 recovery 后验证

GPT 读回成功后，重启 recovery 刷新分区大小和加密映射。解密并挂载 Data，再验证：

```sh
adb -s SERIAL reboot recovery
adb -s SERIAL wait-for-device
# 在 TWRP 中解密并挂载 Data。
python3 scripts/dual_sys/partition.py verify --plan out/dual_sys/applied/plan.json
```

`verify` 检查 GPT、内核分区范围和 F2FS 大小。确认文件可读后，再测试 Android 启动：

```sh
adb -s SERIAL reboot system
```

`unixnu` 尚未格式化，可能残留旧 userdata 字节。写入镜像前，确认设备配置和刷写命令指向 `unixnu`；默认构建命令仍可能指向 Android 的 `userdata`。镜像构建和 UFS 驱动需另行配置。

## F2FS 容量计算

设原始块数为 `B`，新分区可容纳的 4096 字节块数为 `L`，section 大小为 `S = 512`，请求值为 `floor((L - B % S) / S) * S`。[内核](https://github.com/torvalds/linux/blob/v6.6/fs/f2fs/gc.c)按整个 section 缩减并保留原始余数，只对 `L` 取整可能越界。辅助程序会检查最终大小。

## 处理中断

脚本不自动重试或回滚。不要删除 recovery 会话锁来重新执行 `apply`。重启前保存阶段标记和内核日志：

```sh
adb -s SERIAL pull /tmp/unixnu-dual-REPLACE_WITH_PRINTED_ID/stage ./recovery-stage.txt
adb -s SERIAL shell dmesg > recovery-dmesg.txt
```

| 最后完成的操作 | 后续处理 |
| --- | --- |
| 预览或前置检查 | 存储未改变，解决报告的问题后重新生成方案 |
| F2FS 缩容失败 | 保留原 GPT，检查文件系统和内核错误后再决定是否继续 |
| F2FS 已验证，卸载失败 | GPT 仍为原始状态，检查占用文件和绑定挂载，不强制或懒卸载 |
| 已开始写入备份 GPT | 两份 GPT 可能不一致，保持 recovery 运行，重启前检查两份原始数据 |
| 两份 GPT 均读回成功 | 重启 recovery 并执行 `verify` |

Data 无法读取时不要格式化。恢复 GPT 不能撤销 F2FS 数据迁移；完整恢复 userdata 需要原分区容量和匹配的 metadata 备份。先由设备维护者判断现场状态。

## 离线测试

Linux、WSL 和 macOS 均可执行，需要 C 编译器，无需连接手机：

```sh
python3 scripts/dual_sys/test_dual_sys.py
cc -O2 -Wall -Wextra -Werror scripts/dual_sys/f2fs-shrink.c -o /tmp/f2fs-shrink-test
/tmp/f2fs-shrink-test self-test
sh -n scripts/dual_sys/twrp.sh
```

macOS 上的 `cc` 仅编译共用的对齐自检，不依赖 Linux 头文件，也不包含设备操作。Recovery 使用上节的 Linux/Android ELF 构建。

覆盖 GPT、F2FS 对齐、ADB 选择及模拟失败顺序。Recovery 内核行为、数据完整性和 Android 启动仍需真机测试。
