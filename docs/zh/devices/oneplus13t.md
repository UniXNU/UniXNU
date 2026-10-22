# 一加 13T（oneplus13t）

oneplus13t 是搭载 SM8750 的一加 13T（PKX110、OP60F5L1）。下面的移植是独立的社区项目，UniXNU 组织不维护它。仓库从 `UniXNU-oneplus13t` 更名为 `UniXNU-Pagani_SM8750`，提交历史保留。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-Pagani_SM8750](https://github.com/IssacL04/UniXNU-Pagani_SM8750) | [IssacL04](https://github.com/IssacL04) | 已到 XNU S1 到 S6，根设备查找 panic，无根和用户态 |

## 状态

| 部分 | 状态 |
| --- | --- |
| UEFI Shell 和菜单 | 真机工作，侧键交互仍待确认 |
| GitHub Actions 中的 XNU 构建 | 通过，第 9 个镜像到达 S1 到 S6 |
| 负载和启动镜像 | 内嵌负载交接，启动镜像解包后比对通过 |
| DarwinBoot 交接 | 真机出现绿色交接条 |
| XNU 入口 | 已到 S1 到 S6，控制台、`zalloc` 和 BSD 根设备查找已执行 |
| 根和用户态 | 不可用，根设备查找在 60 秒后 panic |
| kernelcache 预链接、userdata、iOS 用户态 | 未配置 |

panic 页记录 `poll=0x3c`、`timer=0x1a3` 和超时路径。单核定时器中断和观察线程已运行。长期稳定性和多核调度尚未验证。

## 双系统存储

2026-10-22，设备专用的 F2FS 缩容流程在 256 GB 机型上创建了 64 GiB 的 `unixnu` 分区。采集到的主、备 GPT 一致，CRC 有效。该结果只覆盖分区创建，不能证明 XNU 已挂载根文件系统，也不代表参数化脚本已经在其他设备上验证。

| 项目 | 采集值 |
| --- | --- |
| Recovery 内核 | `6.6.118-android15-8-o-g4d611c32bedc-enc3l-4k` |
| 磁盘 / 逻辑扇区 | `/dev/block/sda` / 4096 字节 |
| 剩余 userdata | 分区 15，LBA 4020972 到 44928767 |
| UniXNU 分区 | 分区 16，LBA 44928768 到 61705983 |
| F2FS 缩容请求 / 预期结果 | 40907264 / 40907535 个 4096 字节块 |

按[双系统分区指南](/zh/porting/dual-system-partition)从连接的设备计算布局，不要把这些 LBA 复制到另一台手机。检查当前分区表：

```sh
python3 scripts/dual_sys/partition.py inspect
```

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
