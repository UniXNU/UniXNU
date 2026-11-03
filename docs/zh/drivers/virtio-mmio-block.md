# VirtioMmioBlock

先按[适配流程](/zh/porting/platform)准备板级输入、修改源码、接入构建并逐步验证。

使用 split queue 的 VirtIO 1.2 MMIO 块传输。

[源码仓库](https://github.com/UniXNU/VirtioMmioBlock).

组件需要匹配的 MMIO 设备、中断路由和所选存储 ABI。owner-root 路径还提供 verified block 策略 archive。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build kernel -D /path/to/device
```

[组件目录](/zh/reference/components)
