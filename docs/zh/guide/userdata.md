# userdata 镜像

userdata 镜像为 XNU 提供根文件系统。它保存目标 IPSW 中未修改的 `OS` 和 `Cryptex1,SystemOS` 磁盘镜像，并在前面加一个 manifest。

准备选定的 IPSW 及设备 GPT 数据。Linux 上安装提供 `lzfse` 的 [Linux 工具链](/zh/guide/requirements#linux)。扩大 Data 种子（第 4 步）需要 macOS 的 `hdiutil` 和 `diskutil`。先在[构建流程](/zh/building)中选定设备并保存本地输入。

## 1. 核对分区 {#分区}

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

## 2. 预检并构建镜像 {#构建}

```sh
./unixnu build userdata --ipsw /path/to/restore.ipsw --dry-run
./unixnu build userdata --ipsw /path/to/restore.ipsw
```

步骤按 `[userdata] windows` 提取 IPSW 组件，在 macOS 上用 `hdiutil`、在 Linux 上用 `scripts/unixnu/udif.py` 读取每个磁盘镜像，写出原始镜像到 `out/<device>/<os_profile>/<config>/userdata/userdata-root.img`。

报告 `userdata-root.json` 记录窗口偏移、大小、哈希、分区容量和刷写命令。

先检查 dry-run 的分区容量和窗口布局，确认输入正确后再运行第二条命令。完成后应得到镜像及报告。

## 3. 设置根卷 UUID {#根卷选择}

内核按 UUID 挂载根卷：

```toml
[payload.adt]
root_match_volume_uuid = "REQUIRED_ROOT_VOLUME_UUID"
```

从所选 OS 镜像取得 APFS 根卷 UUID。在 macOS 连接镜像后用 `diskutil apfs list` 检查，确认根卷所属镜像容器并复制其 Volume UUID。修改后重建 payload 和启动镜像。

ADT 生成器写入 `/chosen/root-matching`，包含 `IOProviderClass = IOMedia` 和该 UUID。原生块驱动发布 userdata 分区，分区方案发布卷，XNU 选择 UUID 匹配的 IOMedia。

## 4. 准备 Data 卷 {#data-卷}

可写 Data 卷来自负载中的 Data ramdisk 种子：

```sh
./unixnu build payload --data-ramdisk data.img
```

sheng 的持久存储布局可使用 macOS 工具调整 seed 大小：

```sh
python3 scripts/seed-data-grow.py --gib 8 /path/to/data.dbr /path/to/data-grow.dbr
```

按目标 Data 分配范围选择大小，预留根卷窗口、存储元数据和日志区域。
工具通过 `hdiutil` 连接原始镜像，使用 `diskutil` 调整 APFS，生成新的 packed seed。
接受范围为 3 至 1024 GiB。

`--auto` 还读取脚本树中的 `build/userdata-root/userdata-root.json`（或 `.img`），
并通过 fastboot 查询 userdata 容量。使用前在该位置提供同一目标的报告。
`--userdata-bytes BYTES` 替代容量查询，`--reserve-mib` 指定日志保留区，默认 1024 MiB。

卷 UUID 保留，seed 大小变化会改变持久化身份并初始化新的 Data store。
随镜像记录所选大小和根卷报告。其他设备先适配并验证 [UFS 指南](/zh/porting/ufs)中的存储分配。

`--skip-setup` 在种子副本中把 Setup 标记为完成。负载报告记录种子哈希和结果镜像哈希。偏好改动见[跳过 Setup](/zh/guide/skip-setup)。

## 5. 刷写并启动 {#刷写}

刷写 `userdata` 会覆盖该分区。执行前确认目标设备、分区布局和报告中的镜像路径，并保存需要保留的分区数据。

```sh
fastboot devices
fastboot flash userdata out/<device>/<os_profile>/<config>/userdata/userdata-root.img
```

刷写成功后，按[启动镜像](/zh/guide/boot#启动)启动匹配的 boot image，记录根卷挂载结果。

驱动把命令写入报告。设备仓库可以提供封装脚本，在刷写前检查镜像和分区。

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

## 下一步

- [userdata 布局](/zh/concepts/userdata)
- [启动镜像](/zh/guide/boot)
- [设备配置](/zh/reference/configuration)
