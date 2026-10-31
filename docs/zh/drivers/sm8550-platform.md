# Sm8550Platform

先按[适配流程](/zh/porting/gpu)准备板级输入、修改源码、接入构建并逐步验证。

SM8550 GPU 平台操作：GMU、GPU SMMU，以及 GPU 及其电源轨读取的 RPMh 命令数据库。

[源码仓库](https://github.com/UniXNU/UniXNU-sm8550-common).

这是板级代码而非驱动：由 SoC 仓库提供，板级在启用 Adreno 740 加速器时选中它。GMU 部分启动图形管理单元并持有其电源轨；SMMU 部分给 GPU 自己的 stage 1 翻译域；命令数据库部分按名称回答 RPMh 资源查询。

## 要求

| 要求 | 含义 |
| --- | --- |
| SoC SM8550 | 寄存器映射和 RPMh 资源名属于该板 |
| GPU 固件 | GMU 和 GPU 微码来自板级提供的固件文件 |
| `ArmSmmu4K` | SMMU 部分通过 SMMU kit 编程 stage 1 上下文 |
| `AdrenoFirmware` | 把镜像交给 GMU 的固件加载器 |

在板级配置中选择它：

```toml
[components]
include = ["Sm8550Platform", "Adreno740", "AdrenoMetal", "AdrenoFirmware", "ArmSmmu4K"]
```

该组件作为板级包的一部分编入内核（`build_stage = "embedded"`），不产生单独的归档或 bundle。

## 源码

| 文件 | 内容 |
| --- | --- |
| `ShengGmu.c` | GMU 启动、停止、内存窗口、中断和 keepalive 投票 |
| `ShengGpuSmmu.c` | GPU 的 SMMU 上下文、其 stage 1 页表和故障处理 |
| `ShengGmuCommandDb.c` | RPMh 命令数据库：按名称、档位与投票查询资源 |

## 验证

该 kit 通过使用它的驱动验证：在到达 GPU 的板级上为 [Adreno 740](/zh/drivers/adreno740) 和 [Adreno Metal](/zh/drivers/adreno-metal)。把 GMU 启动结果、SMMU 上下文和资源投票记录到板级 `porting.toml` 的 GPU 区域。

## 集成

```sh
./unixnu build kernel -D ../UniXNU-sheng
```

[组件目录](/zh/reference/components)
