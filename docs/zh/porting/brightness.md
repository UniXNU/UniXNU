# 亮度接口

本页列出系统对背光服务的要求，该服务在
[显示适配](/zh/porting/display)的亮度步骤中构建。数值取自 sheng 的 `AppleARMBacklight.cpp`。

## 服务身份

`AppleARMPlatform` 已定义 `AppleARMBacklight`，所以板级类使用自己的类名，`getMetaClass`
返回 `AppleARMBacklight` 的 metaclass。CoreBrightness 据此把该服务当作内建显示屏的背光，
沙盒也按该类应用配置。

## 发布的属性

| 属性 | 读取方 | 内容 |
| --- | --- | --- |
| `backlight-control` | CoreBrightness | `true` |
| `IODisplayParameters.brightness` | iPadOS 17 | 以等级表示的 `min`、`max`、`value` |
| `IODisplayParameters.BrightnessMilliNits` | iPadOS 27 | 以毫尼特表示的 `min`、`max`、`value` |
| `backlight-marketing-table` | iPadOS 27 | 滑块等间距位置对应的有符号 16.16 尼特。缺少时无法创建显示对象 |
| `LmaxProduct` | iPadOS 27 | 4 字节的 16.16 尼特。为 0 时滑块所有位置都对应最大值 |
| `LmidProduct`、`LminProduct` | iPadOS 27 | 以尼特表示的数值 |
| `backlight-calibration-parameters` | iPadOS 27 | `lMinProduct`、`lMidProduct`、`lMaxProduct`、`lMinPanel`、`lMidPanel`、`lMaxPanel`，均为 16.16 尼特 |

## 接受的请求

| 属性 | 作用 |
| --- | --- |
| `brightness-nits` | 有符号 16.16 尼特。小于等于 0 时关闭 LED，其他值按比例换算为不低于 1 的等级 |
| `brightness`、`FadePeriod` | 等级和以 16.16 秒表示的渐变时间，最长 5 秒，每 16 ms 一步 |

其他属性返回成功，不产生效果。请求通过定时器交给工作循环，调用方不会等待传输。

## iPadOS 27 上的虚拟平台

设置了 ADT 属性 `vmm-present` 的板子会让 MobileGestalt 回答 `IsVirtualDevice`。
CoreBrightness 随后选择一个丢弃所有亮度请求的控制方式。`scripts/appsync/BacklightMode.m`
让 `backboardd` 使用真机的模式，它通过
[AppSync 适配层](/zh/concepts/security)加载。

## 启动参数

| 参数 | 作用 |
| --- | --- |
| `backlight=1` | 启动服务 |
| `backlight-control=0` | 不发布 `backlight-control`，也不返回上述 metaclass |
| `log-display=1` | 在启动日志中加入 `L` 行 |

## 验证

1. 系统日志出现 `[UniXNU backlight] physical brightness control selected`。
2. `L` 行显示 `st=4`，`xerr` 保持为 0。
3. 拖动滑块时 `req` 增加，`lvl` 和面板亮度随之变化。
4. 熄屏时背光关闭，唤醒后恢复。

把结果记录到显示范围，再继续[输入](/zh/porting/input)。
