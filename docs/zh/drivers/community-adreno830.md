# Adreno830

面向一加 13T（PKX110，SM8750）的 Adreno 830（Gen8）内核 GPU 驱动，从 Adreno740 `5c8c145` 起步。它拉起 GMU、CP 和 SMMU，并提供 AdrenoMetal、metal2vulkan 和 Turnip 使用的加速器接口。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [Adreno830](https://github.com/Shad0w23333/Adreno830) | [Shad0w23333](https://github.com/Shad0w23333) | 面向一加 13T（PKX110，SM8750）的 Adreno 830 内核 GPU 驱动。板级输入在设备仓库 [Shad0w23333/UniXNU-Pagani_SM8750](https://github.com/Shad0w23333/UniXNU-Pagani_SM8750)。 |

## 状态

一加 13T，iPadOS 17.7.11（21H461），2026-10-30 至 2026-11-01：驱动在真机上通过 Metal 跑桌面，系统应用、小组件和控制中心都能渲染。主机测试 45 项通过、1 项跳过。详见 [docs/PROGRESS.md](https://github.com/Shad0w23333/Adreno830/blob/main/docs/PROGRESS.md)。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录驱动及其状态，不接管维护。
