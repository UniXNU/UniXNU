# 故障排查

## 构建

| 现象 | 检查 | 处理 |
| --- | --- | --- |
| `no device repository` | `-D` 或 `UNIXNU_DEVICE` | 传入设备仓库 |
| `has no board.toml` | 设备仓库布局 | 创建 `board.toml` |
| `is an EXAMPLE device repository` | `[board] example` | 复制示例并设置真实名称 |
| `no configuration` | `out/<board>/.config` | 运行 `unixnu defconfig NAME` |
| `no Mu-Silicium checkout` | `--uefi` 路径 | 传入含 `Resources/Scripts/mkbootimg.py` 的仓库 |
| `is not a Mu-Silicium checkout` | 路径 | 指向仓库根目录 |
| `no edk2 tree` | `--edk2` 或已拉取 edk2 | 运行 `unixnu fetch` 或传入 Mu_Basecore |
| 内核步骤缺少静态库 | `[kernel] archives` 和 `logs/archive-NN-*.log` | 修正脚本条目或提供静态库 |
| `no builder makes it` | 指定的 `*_ARCHIVE` 路径 | 在 `[kernel] archives` 中加入脚本，或把静态库放入构建树 |
| `kernelcache not found` | `--kernelcache` 或 IPSW | 拉取 IPSW 或传入文件 |
| `does not match the kernelcache` | `[kernel.prelink] kernelcache_sha256` | 使用固定镜像 |
| 固件卷大小不匹配 | `[uefi_fd] size` | 重新构建固件或修正配置 |
| 负载超过 `size_mib` | `[payload] size_mib` | 提高大小或移除文件 |
| `not one of the trust caches this board accepts` | `[payload] trust_cache_sha256` | 使用接受的包，或用 `--owner-trust-cache` 传入 owner 签名的包 |
| `unsupported kernel argument` | 参数字符 | 使用字母、数字、`_`、`.`、`-` |
| `command line is ... bytes` | 参数数量 | 缩短到 1000 字节 |

## IPSW

| 现象 | 检查 | 处理 |
| --- | --- | --- |
| `this IPSW is ...` | 产品、版本、build | 使用板级描述的镜像 |
| `no Erase build identity` | device class、chip ID、board ID | 修正身份值 |
| `does not support range requests` | 远程 URL | 使用支持 range 的服务器或本地文件 |
| `differs from the pinned sha256` | `[ipsw.sha256]` | 使用固定成员或更新固定值 |
| `expected exactly one arm64 slice` | kernelcache | 使用 ARM64 kernelcache |

## 启动

| 现象 | 检查 | 处理 |
| --- | --- | --- |
| `fastboot` 看不到设备 | 驱动、线缆、bootloader 模式 | 安装 USB 驱动并重启到 bootloader |
| 镜像启动后复位 | 启动镜像 header、基址和大小 | 检查 Mu-Silicium 配置和 BootShim 参数 |
| 固件停住 | Silicium 随机停顿 | 再次启动同一镜像 |
| 无显示 | GOP 驱动 | 使用 `console = "text"` 或串口 |
| 无菜单 | 配置路径 | 把 `unixnu.toml` 放到 `\EFI\UniXNU\unixnu.toml` |
| 无启动项 | 负载卷 | 检查 FAT 卷标、菜单项路径和卷驱动 |
| 驱动失败 | 菜单中的第一条失败原因 | 修正驱动路径或依赖 |
| `no loader protocol installed` | 固件卷中的 DarwinBoot | 把 DarwinBoot 加入 FDS 或负载 |
| `loader revision 1 cannot accept kexts` | 加载器 revision | 使用 revision 2 或移除 kext |
| `boot refused: ...; firmware retained` | DarwinBoot 日志 | 检查内核、ADT、trust cache 和占位符 |
| 内核入口 panic | 页表、内核窗口、启动参数 | 用 QEMU fixture 和启动进度日志 |
| panic 给出 provider | 设备树节点或驱动静态库 | 加入节点或启用驱动 |
| 无根设备 | userdata 镜像、UUID、容量 | 刷写镜像，检查 UUID 和窗口偏移 |
| Data store 窗口被拒绝 | 种子大小、`sheng-log-reserve`、根镜像 | 增长种子使其适配 userdata，或调整 `sheng-log-reserve` |
| 用户态显示断言 | 显示 provider 和启动参数 | 检查显示驱动和 focus 参数 |

## 日志

| 来源 | 位置 |
| --- | --- |
| 构建 | `out/<board>/logs/` |
| 启动管理器 | 串口 `UNIXNU:` 行 |
| 加载器 | 串口 `DARWINBOOT:` 行 |
| 内核 | 串口 |
| QEMU | `--log` 文件和 `.clean.log` |

## 检查报告

```sh
jq . out/<board>/boot/boot.json
jq . out/<board>/payload/payload.json
jq . out/<board>/userdata/userdata-root.json
```

报告记录输入哈希，与提供的文件比较。

## 模块来源

```sh
./unixnu status
```

输出列出每个模块和来源。本地模块会被标记并报告为未固定。

## 下一步

- [构建](/zh/building)
- [启动镜像](/zh/guide/boot)
- [调试与日志](/zh/guide/debugging)
- [bring-up 顺序](/zh/porting/bring-up)
