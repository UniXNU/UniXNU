# realme GT5 240W（rmx3823）— miniyv 移植

realme GT5 240W（rmx3823）是 SM8550（kalama）机型。下面的移植是一个独立的社区项目，
fork 自 [Janit8r/uefi-rmx3823](https://github.com/Janit8r/uefi-rmx3823)。
UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [simple-RMX3823-UniXNU](https://github.com/miniyv/simple-RMX3823-UniXNU) | [miniyv](https://github.com/miniyv) | UEFI 引导阶段移植 |

## 当前状态

通过 `fastboot boot`（临时启动，**不写入任何分区**），UEFI 完整引导链已经贯通：

ABL → BootShim → SEC → 固件卷解压 → DXE（全部驱动派发）→ BDS →
UniXNU 菜单（苹果 logo、音量键可选）→ 诊断停机。

2026-11-10 硬件实测通过：1240x2772 帧缓冲控制台、菜单图形、按键输入。
XNU 内核在本移植上尚未启动。

相对上游的主要修复：

- **gunzip 输出损坏规避**。ABL 会对其解压输出缓冲区的固定位置（固件偏移
  0x349A6–0x47661）覆写约 1.2 KB 数据。上游布局中该位置恰好位于 LZMA
  压缩固件卷中段，导致所有预构建镜像的固件卷解压均告失败。本固件插入
  0x41000 字节填充段，使压缩卷从损坏窗口之后开始。
- **移除 RamManagerDxe**。它依赖原厂链条中由 ABL 提供的高通 RamPartition
  协议；`fastboot boot` 链条中无人安装该协议，驱动会断言。
- **BDS 不再关机**。找不到引导项时，平台现在打印 GOP 与引导项诊断信息并
  停机，而不是盖屏后直接关机。

## 路线图

- 接通 UniXNU 载荷（菜单当前报 `image not found`）。
- UFS 存储支持，以便注册引导项。
- 通过 DarwinBoot 启动 XNU。
- GPU 加速（Adreno 740）。
- 外设：触摸、USB、传感器、音频，系统流畅可用。
  蜂窝基带不在本移植的目标范围内。

## 维护

维护者拥有该仓库及其发布决定。UniXNU 文档仅列出该移植及其状态，
不接管维护。
