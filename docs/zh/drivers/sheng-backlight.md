# ShengBacklight

ShengBacklight 把 sheng 面板的两颗 KTZ8866 背光控制器接入 CoreBrightness。

[源码](https://github.com/UniXNU/UniXNU-sheng/blob/main/package/AppleARMBacklight.cpp)。

## 状态

设备：小米平板 6S Pro（sheng）。

| 系统 | 状态 | 功能 |
| --- | --- | --- |
| iPadOS 17 | 可用 | 手动调节亮度，熄屏关闭背光 |
| iPadOS 27.0.1（24A446） | 可用 | 手动调节亮度 |
| iPadOS 27.0.1（24A446） | 未验证 | 熄屏关闭背光 |

## 硬件

两颗控制器的 I2C 地址都是 0x11：一颗在 QUP wrap 1 串行引擎 1（`0xa84000`，SPI 354），另一颗在 I2C hub 引擎 2（`0x988000`，SPI 466）。两者接收相同的 11 位亮度等级，范围 0 到 2047，写入 `BL_BRT_LSB`（0x04，第 2:0 位）和 `BL_BRT_MSB`（0x05）。

引擎沿用引导程序留下的固件、时钟和 SCL 时序。传输由 [GENI I2C 核心](/zh/porting/display)按中断推进，每步期限 25 ms。新等级会替换尚未写入的等级。

## 服务

`AppleARMPlatform` 已定义 `AppleARMBacklight`，所以类名是 `ShengBacklight`，`getMetaClass` 返回 `AppleARMBacklight` 的 metaclass。CoreBrightness 据此把该服务当作内建显示屏的背光，沙盒也按该类应用配置。`NativeSandboxGrantProcess` 允许 `backboardd` 设置配置拒绝的属性。

发布的属性：

| 属性 | 读取方 | 内容 |
| --- | --- | --- |
| `backlight-control` | CoreBrightness | `true` |
| `IODisplayParameters.brightness` | iPadOS 17 | 以等级表示的 `min`、`max`、`value` |
| `IODisplayParameters.BrightnessMilliNits` | `BrightnessControl`，iPadOS 27 | 以毫尼特表示的 `min`、`max`、`value` |
| `backlight-marketing-table` | CoreBrightness，iPadOS 27 | 滑块等间距位置对应的有符号 16.16 尼特。缺少时无法创建显示对象 |
| `LmaxProduct` | `BrightnessControl`，iPadOS 27 | 4 字节的 16.16 尼特。为 0 时滑块表缩放为无穷大，所有位置都对应最大值 |
| `LmidProduct`、`LminProduct` | `BrightnessControl`，iPadOS 27 | 以尼特表示的数值 |
| `backlight-calibration-parameters` | CoreBrightness，iPadOS 27 | `lMinProduct`、`lMidProduct`、`lMaxProduct`、`lMinPanel`、`lMidPanel`、`lMaxPanel`，均为 16.16 尼特 |

接受的请求：

| 属性 | 作用 |
| --- | --- |
| `brightness-nits` | 有符号 16.16 尼特。小于等于 0 时关闭 LED，其他值按比例换算为不低于 1 的等级 |
| `brightness`、`FadePeriod` | 等级和以 16.16 秒表示的渐变时间，最长 5 秒，每 16 ms 一步 |

其他属性（如 `brightness-nits-cap`）返回成功，不产生效果。请求通过定时器交给工作循环，`backboardd` 不会等待传输。

范围是 2、140 和 500 尼特。面板亮度尚未实测，这些值只决定滑块刻度，不代表绝对亮度。

## iPadOS 27 的亮度控制

板级为 AMFI 设置了 ADT 属性 `vmm-present`，MobileGestalt 因此回答 `IsVirtualDevice`。CoreBrightness 随后选择 `VMBLControl`，它会丢弃所有亮度请求。许多其他框架也读取这个值，所以它保持为真。

`scripts/appsync/BacklightMode.m` 只改变 `backboardd`：`-[BrightnessSystemInternal initBLControl:]` 收到真机使用的模式 1，而不是 3。它通过 AppSync 适配层加载，该适配层用签名副本替换 `/usr/libexec/backboardd`。

## 配置

| 启动参数 | 作用 |
| --- | --- |
| `backlight=1` | 启动驱动 |
| `backlight-control=0` | 不发布 `backlight-control`，也不返回上述 metaclass |
| `log-display=1` | 在启动日志中加入 `L` 行 |

## 验证

1. 系统日志出现 `[UniXNU backlight] physical brightness control selected` 和 `Set Default 1 BLControl`。
2. `L` 行显示 `st=4`，`xerr` 保持为 0。
3. 拖动滑块时 `req` 增加，`lvl` 和面板亮度随之变化。
4. 熄屏时背光关闭，唤醒后恢复。
