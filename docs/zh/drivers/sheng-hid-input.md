# ShengHidInput

先按[适配流程](/zh/porting/input)准备板级输入、修改源码、接入构建并逐步验证。

触控、按键与 IOHIDFamily 的集成。

[源码仓库](https://github.com/UniXNU/ShengHidInput).

实现使用板级触控状态和 IOHIDFamily 2031.120.4 ABI。archive 构建器读取已确认的预链接 candidate 和 ABI 记录，需要板级触控策略与所选 OS ABI。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build kernel -D /path/to/device
```

[组件目录](/zh/reference/components)

arm64e 的公开源码构建方法及当前链接、运行时限制见[公开源码驱动构建](/zh/porting/migration#source-drivers)。历史 iOS 17 真机结果不代表该路径已通过验证。
