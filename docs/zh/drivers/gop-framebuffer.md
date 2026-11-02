# GopFramebuffer

先按[适配流程](/zh/porting/display)准备板级输入、修改源码、接入构建并逐步验证。

使用固件 GOP 交接的 framebuffer 呈现。

[源码仓库](https://github.com/UniXNU/GopFramebuffer).

实现通过 PE_current_console 读取固件 framebuffer，并集成所选 MobileFramebuffer ABI。板级接口提供显示策略和 GPU scanout 集成。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build kernel -D ../UniXNU-sheng
```

[组件目录](/zh/reference/components)

帧诊断记录 GPU 与显示的明确关联，以及完成后的原始像素。使用方法见 [GPU 帧诊断](/zh/porting/gpu-diagnostics)。

帧诊断从已准备好的直接显示槽位读取物理地址。验证阶段尚未映射时记录零地址，提交切换时补充映射地址。诊断观察代码不准备描述符，也不查询其物理段。
