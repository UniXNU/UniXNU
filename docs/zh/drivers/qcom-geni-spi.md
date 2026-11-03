# QcomGeniSpi

先按[适配流程](/zh/porting/input)准备板级输入、修改源码、接入构建并逐步验证。

高通 GENI 串行引擎 SPI 控制器操作。

[源码仓库](https://github.com/UniXNU/QcomGeniSpi).

调用者提供寄存器访问和平台回调。参考触控栈将其与 ShengNovatekTouch 组合使用，复用时核对控制器资源和回调要求。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build kernel -D /path/to/device
```

[组件目录](/zh/reference/components)
