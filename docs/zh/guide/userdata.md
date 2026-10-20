# userdata 镜像

userdata 镜像为 XNU 提供根文件系统。它保存目标 IPSW 中未修改的 `OS` 和 `Cryptex1,SystemOS` 磁盘镜像，并在前面加一个 manifest。

## 构建

```sh
./unixnu build userdata --ipsw /path/to/restore.ipsw
```

步骤按 `[userdata] windows` 提取 IPSW 组件，用 `hdiutil` 读取每个磁盘镜像，写出原始镜像到 `out/<board>/userdata/userdata-root.img`。

报告 `userdata-root.json` 记录窗口偏移、大小、哈希、分区容量和刷写命令。

只检查不写文件：

```sh
./unixnu build userdata --dry-run
```

## 分区

`board.toml` 描述 GPT 条目：

```toml
[userdata]
first_lba = 0x2f3840
last_lba = 0x3d0abfa
lba_bytes = 4096
windows = [
  { name = "OS", component = "OS" },
  { name = "SystemOS", component = "Cryptex1,SystemOS" },
]
```

`first_lba` 和 `last_lba` 来自设备上名为 `userdata` 的 GPT 条目，`lba_bytes` 是分区逻辑块大小。

镜像大小为各窗口按 1 MiB 对齐后的总和，加上 1 MiB 头部区域。步骤拒绝超过分区容量的镜像。

## 布局

```
0x000000  SHNGROOT manifest，4096 字节，零填充到 1 MiB
0x100000  OS 窗口，完整磁盘镜像
....      SystemOS 窗口，完整磁盘镜像
```

manifest 为小端：

| 偏移 | 字段 |
| --- | --- |
| 0 | `SHNGROOT` |
| 8 | 版本，32 位，值 1 |
| 12 | 窗口数，32 位 |
| 16 | 镜像大小，64 位 |
| 24 | 窗口条目，每条 128 字节 |
| 4064 | 字节 0 到 4063 的 SHA-256 |

每个窗口条目包含 32 字节名称、64 位偏移、64 位大小、32 位块大小、32 位标志、32 字节 SHA-256 和 40 字节保留。

## 刷写

```sh
fastboot flash userdata out/<board>/userdata/userdata-root.img
```

驱动把命令写入报告。设备仓库可以提供封装脚本，在刷写前检查镜像和分区。

## 根卷选择

内核按 UUID 挂载根卷：

```toml
[payload.adt]
root_match_volume_uuid = "00000000-0000-0000-0000-000000000000"
```

ADT 生成器写入 `/chosen/root-matching`，包含 `IOProviderClass = IOMedia` 和该 UUID。原生块驱动发布 userdata 分区，分区方案发布卷，XNU 选择 UUID 匹配的 IOMedia。

## Data 卷

可写 Data 卷来自负载中的 Data ramdisk 种子：

```sh
./unixnu build payload --data-ramdisk data.img
```

种子可以增长到平板的存储大小，不需要挂载卷：

```sh
python3 scripts/seed-data-grow.py --auto data.dbr data-grow.dbr
```

`--auto` 读取 `fastboot getvar partition-size:userdata`，减去根镜像、4 MiB guard、日志保留区和 store header 与 bitmap，向下取整到整 GiB，并保留 1 GiB 余量。它需要 userdata 构建生成的 `build/userdata-root/userdata-root.json` 和处于 fastboot 的平板，除非给出 `--userdata-bytes`。`--gib N` 直接指定大小，`--userdata-bytes BYTES` 跳过 fastboot 查询，`--reserve-mib` 覆盖默认 1024 MiB 日志保留区。范围为 3 到 1024 GiB。

增长后的输出只保留非零页，大小接近输入。卷 UUID 不变。种子身份包含大小，所以改变大小会重新开始 Data 卷。store 窗口不适合真实 userdata 分区时，内核拒绝该种子。

内核接受最大 1 TiB 的 Data 磁盘。typed block provider 只保存种子的非零页，持久 store 用 forced unit access 把变化的页写回 userdata 分区末尾。

`--skip-setup` 在种子副本中把 Setup 标记为完成。负载报告记录种子哈希和结果镜像哈希。偏好改动见[跳过 Setup](/zh/guide/skip-setup)。

## 下一步

- [userdata 布局](/zh/concepts/userdata)
- [启动镜像](/zh/guide/boot)
- [设备配置](/zh/reference/configuration)
