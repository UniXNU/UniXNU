# ShengPreflight

先按[适配流程](/zh/porting/platform)准备板级输入、修改源码、接入构建并逐步验证。

板级 UEFI 预检。构建前校验固件卷、内存图和启动输入。

| 仓库 | 维护者 | 范围 |
| --- | --- | --- |
| [ShengPreflight](https://github.com/UniXNU/ShengPreflight) | [UniXNU](https://github.com/UniXNU) | 板级 UEFI 预检。构建前校验固件卷、内存图和启动输入。 |

## 状态

检查项对应参考板型的固件卷和内存布局。

## 构建

设备在 `[firmware] preflight` 选择预检脚本，`./unixnu build firmware` 在构建 FD 前调用它们。使用目标设备的预检实现和固件输入。
