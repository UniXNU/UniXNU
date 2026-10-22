# MobileGestalt 身份

MobileGestalt 从 Apple 设备树（ADT）读取设备信息。负载在构建时写入 ADT，修改身份不需要改动已签名的内核和用户态镜像。

## 属性

| 属性 | 节点 | 示例 | 作用 |
| --- | --- | --- | --- |
| `model` | 根节点 | `iPad7,1` | `hw.product` 和 `hw.machine`，按前缀确定设备类别 |
| `target-type` | 根节点 | `J120` | `hw.target`，硬件型号字符串 |
| `product-name` | `/product` | `iPad Pro (12.9-inch) (2nd generation)` | 平台专家报告的产品名 |
| `product-description` | `/product` | `iPad Pro (12.9-inch) (2nd generation)` | 产品描述 |
| `artwork-device-idiom` | `/product` | `pad` | 界面系列，iPhone 使用 `phone` |
| `artwork-device-subtype` | `/product` | `2732` | 素材几何 |
| `artwork-scale-factor` | `/product` | `2` | 素材缩放 |
| `artwork-display-gamut` | `/product` | `P3` | 显示色域 |
| `compatible-device-fallback` | `/product` | `iPad6,7` | 回退设备 |
| `thin-bezel` | `/product` | `1` | 边框类型 |
| `button-names` | `/buttons` | `hold`、`voldown`、`volup` | 可用按钮，没有主屏幕按钮时省略 `menu` |
| `home-button-type` | `/buttons` | `2` | 无机械主屏幕按钮，使用滑动手势 |
| `certificate-production-status` | `/chosen` | `0` | 激活安全状态 |
| `effective-production-status-ap` | `/chosen` | `0` | 激活安全状态 |
| `certificate-security-mode` | `/chosen` | `1` | 激活安全模式 |
| `effective-security-mode-sep` | `/chosen` | `1` | 激活安全模式 |
| `display-scale` | `/chosen` | `2` | MobileGestalt 读取的缩放 |

`DeviceClass` 把 `hw.product` 按前缀与 `iPhone`、`iPod`、`iPad`、`AppleTV`、`Watch` 等系列比较。前缀不匹配时回退为 `iPod`。根节点 `model` 提供 `hw.product`，需要和 `/product` 的值一起设置。

## 全面屏手势

使用没有主屏幕按钮的身份：

- 根节点 `model` 和 `target-type` 取自无主屏幕按钮的设备
- `/buttons` 不包含 `menu`
- `home-button-type = 2`

SpringBoard 通过 `BSPlatform homeButtonType` 读取该值。值为 2 时，锁屏使用上滑手势。sheng 上从锁屏上滑可以到达密码界面，密码界面把设备识别为 iPad。

## iPadOS 与 iOS

ADT 身份和用户态镜像属于同一设备系列。iPadOS 根使用 pad 身份，iOS 根使用 phone 身份。

| 目标 | `model` | `target-type` | `product-name` | `artwork-device-idiom` |
| --- | --- | --- | --- | --- |
| iPadOS | `iPad7,1` | `J120` | `iPad Pro (12.9-inch) (2nd generation)` | `pad` |
| iOS | `iPhone10,3` | `D22` | `iPhone X` | `phone` |

恢复镜像见[构建环境](/zh/guide/requirements#target-ipsw)。

在 UniXNU 板级文件中，`[payload.adt] ipad_identity = true` 把 `--ipad-identity` 传给板级 ADT 工具，由工具写入 iPad 身份。目标为 iPhone 时，在 ADT 工具中写入 phone 值，或增加一个选择身份的板级选项。

身份向用户态描述硬件。已安装的系统仍来自 IPSW，iPadOS 根保持 iPadOS，iOS 根保持 iOS。

根节点 `compatible` 保留板子自己的字符串。Apple 板名可能匹配原始平台 kext，进入移植尚未实现的路径。

## 应用

1. 修改板级 ADT 工具，或设置 `ipad_identity`。
2. 重新构建负载。
3. 清除缓存的答案。
4. 启动后检查设备名、锁屏提示、上滑手势和键盘布局。

Python ADT 工具可以直接写入节点：

```python
node('buttons', [
    ('compatible', b'buttons\0'),
    ('device_type', b'buttons\0'),
    ('button-names', b'hold\0voldown\0volup\0'),
    ('home-button-type', struct.pack('<I', 2)),
])
node('product', [
    ('product-name', b'iPad Pro (12.9-inch) (2nd generation)\0'),
    ('product-description', b'iPad Pro (12.9-inch) (2nd generation)\0'),
    ('artwork-device-idiom', b'pad\0'),
    ('artwork-device-subtype', struct.pack('<I', 2732)),
    ('artwork-scale-factor', struct.pack('<I', 2)),
    ('artwork-display-gamut', b'P3\0'),
    ('compatible-device-fallback', b'iPad6,7\0'),
    ('thin-bezel', struct.pack('<I', 1)),
])
```

## 缓存

MobileGestalt 把答案写到 `/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.mobilegestaltcache/Library/Caches/com.apple.MobileGestalt.plist`。缓存按 build 和平台 UUID 索引，修改身份后可能保留旧的设备类别和主屏幕按钮答案。修改身份后删除该文件，或重建 Data 卷。偏好文件 `/var/mobile/Library/Preferences/com.apple.MobileGestalt.plist` 和 `com.apple.mobilegestalt.plist` 属于同一域。

## 下一步

- [设备树](/zh/porting/device-tree)
- [启动负载](/zh/concepts/payload)
- [跳过 Setup](/zh/guide/skip-setup)
