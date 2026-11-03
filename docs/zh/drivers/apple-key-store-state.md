# AppleKeyStoreState

先按[适配流程](/zh/porting/platform)准备板级输入、修改源码、接入构建并逐步验证。

为所选用户态 ABI 提供 AppleKeyStore 状态查询和状态接口。

[源码仓库](https://github.com/UniXNU/AppleKeyStoreState).

该组件处理 AppleKeyStore selector 和所选 OS 配置使用的状态回调，运行时服务与符号记录在组件目录中。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build kernel -D /path/to/device
```

[组件目录](/zh/reference/components)
