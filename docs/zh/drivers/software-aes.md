# SoftwareAES

先按[适配流程](/zh/porting/platform)准备板级输入、修改源码、接入构建并逐步验证。

通过 XNU AES 辅助函数和 IOAESAccelerator ABI 提供软件 AES-CBC。

[源码仓库](https://github.com/UniXNU/SoftwareAES).

SoftwareAES 使用所选 XNU 和 IOCryptoAcceleratorFamily 接口。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build kernel -D /path/to/device
```

[组件目录](/zh/reference/components)
