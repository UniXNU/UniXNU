# userdata 布局

userdata 分区承载 Darwin 根文件系统。UniXNU 保留原始磁盘镜像不变，并添加 manifest 把每个镜像映射到分区窗口。

## manifest

```
struct shngroot_header {
  char     magic[8];        /* "SHNGROOT" */
  uint32_t version;         /* 1 */
  uint32_t count;           /* 窗口数 */
  uint64_t image_bytes;     /* 镜像总大小 */
  struct {
    char     name[32];
    uint64_t offset;
    uint64_t size;
    uint32_t block_size;    /* 512 */
    uint32_t flags;         /* bit 0: 只读 */
    uint8_t  sha256[32];
    uint8_t  reserved[40];
  } window[count];
  uint8_t  reserved[32];
  uint8_t  manifest_sha256[32];
};
```

头部占 4096 字节，零填充到 1 MiB。第一个窗口从 0x100000 开始，每个窗口按 1 MiB 对齐。

## 窗口

| 窗口 | IPSW 组件 | 内容 |
| --- | --- | --- |
| `OS` | `OS` | 系统卷 |
| `SystemOS` | `Cryptex1,SystemOS` | cryptex 系统卷 |

镜像按字节从 IPSW 磁盘镜像复制。userdata 步骤读取每个磁盘镜像的原始磁盘：macOS 上用 `hdiutil` 只读挂载并读取原始设备，Linux 上由 `scripts/unixnu/udif.py` 解码 UDIF 块。OS 镜像是含 LZFSE 块的 UDIF 镜像；SystemOS cryptex 是原始镜像，按原样复制。

## 容量

```
(last_lba - first_lba + 1) * lba_bytes
```

步骤拒绝超过容量的镜像。报告记录容量和镜像大小。

## 根卷匹配

XNU 通过 `/chosen/root-matching` 选择根卷：

```xml
<dict>
  <key>IOProviderClass</key><string>IOMedia</string>
  <key>IOPropertyMatch</key>
  <dict>
    <key>UUID</key><string>00000000-0000-0000-0000-000000000000</string>
  </dict>
</dict>
```

UUID 是 OS 窗口的卷 UUID。原生块驱动发布 userdata 分区，分区方案发布卷，XNU 匹配 UUID。

## Data 卷

可写 Data 卷独立于 userdata 镜像，来自负载中的 Data ramdisk 种子。种子是负载步骤的输入，负载报告记录其哈希。

内核接受最大 1 TiB 的 Data 磁盘。超过 2 GiB 时，typed block provider 只保存种子的非零页，内存占用随内容而不是磁盘大小增长。种子身份对大小和非零页及其索引做哈希。

持久 store 从 userdata 分区末尾的窗口提供磁盘。写入使用 forced unit access，命令完成时页已写入介质。store 与根镜像和日志保留区保持距离。`sheng-log-reserve=<MiB>` 设置该保留区，默认 1024 MiB。`sheng-data-persist=1` 只验证窗口，`sheng-data-persist=2` 打开写窗口。

`scripts/seed-data-grow.py` 把打包种子的 APFS 容器增长到指定大小或平板的 userdata 分区。输出只保留非零页，卷 UUID 不变。改变大小会重新开始 Data 卷。store 窗口不适合真实分区时，内核拒绝该种子。

`--skip-setup` 写出把 Setup 标记为完成的种子副本，副本按种子哈希缓存。

## 报告

`userdata-root.json` 记录：

| 字段 | 含义 |
| --- | --- |
| `image_bytes` | 镜像总大小 |
| `image_sha256` | 镜像哈希 |
| `manifest_sha256` | manifest 哈希 |
| `windows` | 每个窗口的名称、偏移、大小和哈希 |
| `userdata_bytes` | 分区容量 |
| `flash_command` | `fastboot flash userdata <image>` |
| `source` | 本地或远程 IPSW |
| `hardware_tested` | 验证状态 |

## 下一步

- [userdata 镜像](/zh/guide/userdata)
- [设备配置](/zh/reference/configuration)
- [启动链](/zh/concepts/boot-chain)
