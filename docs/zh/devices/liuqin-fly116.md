# Xiaomi Pad 6 Pro（liuqin）：存储链路打通、根卷挂载未完成（Fly116）

[Fly116/UniXNU-liuqin](https://github.com/Fly116/UniXNU-liuqin)

小米平板 6 Pro（liuqin / SM8475）上的 UniXNU 移植记录。**UFS 存储链路、iOS 根镜像与块设备发布已实机打通，根卷挂载尚未完成；当前无法启动 iOS 用户界面。**

目标组件：iPad7,1 iPadOS 17.7.11（21H461）。

| 部分 | 状态 |
| --- | --- |
| 配置 | `implemented`（board.toml + liuqinPkg） |
| 固件与启动 | `implemented`（Mu-Silicium UEFI + BootShim，全 Linux 构建） |
| 内存与 DMA | `implemented`（自建连续页分配 + `kmem_alloc_contig`） |
| 显示 | `implemented`（仅 framebuffer 文本控制台） |
| 存储与根卷 | `partial`：UFS 链路、GPT/SHNGROOT 解析、块设备发布已通；`IOMedia` 未生成，根卷未挂载 |
| 镜像组装 | `implemented`（userdata 94 GiB + `unixnu` 11.79 GiB，镜像 9,382,658,048 B） |
| 用户态 | `planned` |
| GPU / 图形界面 | `planned`；Adreno 无 Metal 驱动，真桌面可行性低 |
| 网络、音频、电源 | `planned` |

## 已实机验证的关键结论

- 非苹果平台无人初始化 `IOMapper`；wired（不可分页）描述符的 `prepare()` 永不返回 —— 改为自建 DMA 缓冲。
- 早期 `kmem_alloc_contig` 不可靠、`mach_absolute_time()` 不前进 —— 连续页提前到 STARTUP 阶段预分配。
- **`IOSleep()` 在本平台永不返回**，所有基于 deadline 的等待都会挂死；等待逻辑必须改为忙等 + 让出 CPU。
- IOStorageFamily 的 prelink 绝对符号漏了 board 的 slide（`-0x1000000`），导致块设备构造函数跳入零填充区执行 `UDF #0`。
- `IOService::registerService()` 要求服务在 service plane 中有通往 registry root 的链路；挂在设备树节点上的服务会被静默丢弃，本移植改为挂到 platform expert。

## 当前卡点

窗口已成功 `registerService()`（诊断见 `REGPUBLISH ok`），但没有任何 `IOBlockStorageDriver` 认领该设备，
因此不生成 `IOMedia`，媒体等待超时并报 `UFS ROOT FAILURE: SystemOS window media not found`。

完整记录（含已排除的假设与下一步）见仓库 `docs/bringup-2026-11-19-session.md`。