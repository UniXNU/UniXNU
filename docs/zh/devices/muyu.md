# 小米平板 7 Pro（muyu）

小米平板 7 Pro（muyu） 是搭载 SM8635 的设备。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-muyu](https://github.com/yehua123-oos/UniXNU-muyu) | [yehua123-oos](https://github.com/yehua123-oos) | iPadOS 17.7.11 可启动；Adreno 735 GMU 已运行 |

## 状态

iPadOS 17.7.11（21H461）根镜像已装在 `userdata`，系统能进桌面，显示由 CPU 合成（约 1.4 fps）。UEFI 用 `fastboot boot` 启动，负载是 `vendor_boot` 的 ramdisk；物理按键和 Novatek 触摸控制器都以原生 IOService 运行。

GPU：Adreno 735（`qcom,adreno-gpu-gen7-11-0`）的 GMU 已在真机上冷启动并完成全部 HFI 启动（2026-10-30 读数 `cold=0 ph=7 proto=0`）。命令提交、CP 和 Metal 前端尚未实现；GX 电源域的上电卡在一个本 port 还没有驱动的 RPMh voter 上。

## GPU 记录

仓库里保存了完整取证：`docs/GPU-CLIFFS-MMIO.md`（cliffs 寄存器表）、`docs/GPU-GMU-MAP.md`（GMU 平台描述）、`docs/GPU-PROBE-RUNBOOK.md`（探针模式、期望值与判定树）。GMU 固件 chip id 是从 CM3 镜像里直接取出来的（`0x070b0000`），不是 catalog 的回退公式。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。

## 来源

- [板级配置](https://github.com/yehua123-oos/UniXNU-muyu/blob/main/board.toml)
