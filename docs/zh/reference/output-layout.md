# 输出布局

全部构建输出位于 `out/`。驱动只在设备仓库写入 `unixnu.lock`。

## 目录

```
out/
  state.json
  feeds/
  ipsw/<build>/
  <board>/
    .config
    tree/
    logs/
    kernel/
      kernel.macho
    package/
      Build/Out/
    payload/
      payload.img
      payload.json
    boot/
      boot.img
      boot.json
    userdata/
      userdata-root.img
      userdata-root.json
```

## state.json

```json
{
  "device": "/path/to/device/repository"
}
```

没有 `-D` 和 `UNIXNU_DEVICE` 时，驱动从这里读取设备仓库。

## feeds

每个 git 仓库和 ref 一个克隆：

```
out/feeds/<repo>-<hash>/
```

哈希覆盖 URL 和 ref。源码声明 `path` 时使用浅克隆、blobless 和 sparse checkout。

## ipsw

```
out/ipsw/<build>/
  <member file>
  <member file>.json
```

sidecar 记录组件、成员路径、大小、SHA-256 和来源。缓存成员的大小和哈希匹配固定值时复用。

## tree

```
tree/
  drivers/
  kits/
  patches/
  refer/
  scripts/
  package/
  build/
  .cache/
```

模块目录是符号链接，`scripts/` 是副本。设备 package 出现在 `kits/<board.kit>`。`.cache/firmware` 是指向设备仓库 `.cache/firmware` 的符号链接。

## logs

| 文件 | 步骤 |
| --- | --- |
| `kernel.log` | XNU 构建 |
| `kernel-bootstrap.log` | 为编译记录执行的首次 XNU 构建 |
| `archive-NN-<name>.log` | `[kernel] archives` 中第 `NN` 个静态库脚本 |
| `prelink.log` | 预链接 |
| `package.log` | EDK II package 构建 |
| `firmware-preflight.log` | 板级预检 |
| `firmware.log` | EDK II 固件构建 |
| `basetools.log` | EDK II BaseTools 构建 |
| `payload.log` | 负载卷 |
| `payload-adt.log` | ADT 生成 |
| `payload-patch.log` | panic 屏幕补丁 |
| `payload-skip-setup.log` | Setup 跳过 |
| `userdata.log` | userdata 镜像 |

## boot.json

| 字段 | 含义 |
| --- | --- |
| `kernel_sha256` | kernel 字段哈希 |
| `ramdisk_bytes` | ramdisk 大小 |
| `header_version` | Android 启动镜像 header 版本 |
| `kernel_address` | 内核加载地址 |
| `tags_address` | tags 加载地址 |
| `image_sha256` | 启动镜像哈希 |
| `image_bytes` | 启动镜像大小 |
| `fd_sha256` | 固件卷哈希 |
| `dtb_sha256` | 设备树哈希 |
| `shim_bytes` | BootShim 大小 |
| `hardware_tested` | 验证状态 |

## payload.json

| 字段 | 含义 |
| --- | --- |
| `kernel_sha256` | 输入内核 |
| `payload_kernel_sha256` | 负载中的内核 |
| `adt_sha256` | ADT sidecar |
| `kernel_args` | 命令行 |
| `trust_cache_sha256` | trust cache 包 |
| `data_ramdisk_sha256` | Data 种子 |
| `skip_setup` | 是否跳过 Setup |
| `panic_screen` | 是否打入 panic 屏幕 |
| `payload_sha256` | 负载镜像哈希 |
| `payload_bytes` | 负载镜像大小 |
| `hardware_tested` | 验证状态 |

## userdata-root.json

| 字段 | 含义 |
| --- | --- |
| `image_bytes` | 镜像大小 |
| `image_sha256` | 镜像哈希 |
| `manifest_sha256` | manifest 哈希 |
| `windows` | 每个窗口的名称、偏移、大小和哈希 |
| `userdata_bytes` | 分区容量 |
| `flash_command` | fastboot 命令 |
| `source` | 本地或远程 IPSW |
| `hardware_tested` | 验证状态 |

## 清理

`unixnu clean` 删除板级输出下的 `tree`、`logs`、`kernel`、`package`、`boot` 和 `edk2-conf`，保留已拉取源码和解压的 IPSW 成员。

## 下一步

- [构建](/zh/building)
- [命令行](/zh/reference/cli)
- [故障排查](/zh/reference/troubleshooting)
