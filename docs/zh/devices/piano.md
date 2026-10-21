# 小米平板 8 Pro（piano）

piano 是搭载 SM8750 的小米平板 8 Pro。下面的移植是独立的社区项目，UniXNU 组织不维护它。固件部分来自 [Project-SunUEFI](https://github.com/slwyts/Project-SunUEFI)。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-piano](https://github.com/code002-2/UniXNU-piano) | [code002-2](https://github.com/code002-2) | 内核在 CI 编译并预链接 |

## 状态

设备树生成器和板级描述已被 `unixnu` 驱动接受。XNU 内核在 CI 编译并预链接：51,806,208 字节，ARM64 `MH_EXECUTE`，带 namespaced source corecrypto、`ArmDTPlatform` 和 `ArmCpu`。尚未在平板上运行。下一步是负载、启动镜像，以及把 UniXNU 和 DarwinBoot 集成进 SunUEFI 的 `pianoPkg` 固件。

## 构建

```sh
gh workflow run build-piano-kernel
```

从运行结果下载 `piano-kernel`，读取 `kernel.macho` 及其 SHA-256。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
