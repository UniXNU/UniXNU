# MobileGestalt 身份

MobileGestalt 从 Apple 设备树（ADT）读取设备信息。负载在构建时写入 ADT，修改身份不需要改动已签名的内核和用户态镜像。

## 操作步骤 {#procedure}

1. 按 [iPadOS 与 iOS](#ipados-与-ios)确认用户态系列，选择匹配的 model、target 和 product 值。
2. 按[应用](#应用)修改带类型的 ADT 属性，同时核对[属性表](#属性)和[手势要求](#全面屏手势)。
3. 运行 `./unixnu payload` 和 `./unixnu bootimg`，再启动新镜像。
4. 检查设备报告的身份和界面行为。结果仍为先前值时，按[缓存说明](#缓存)检查，记录受影响的缓存及镜像。

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

SpringBoard 通过 `BSPlatform homeButtonType` 读取该值。值为 2 时，锁屏使用上滑手势。

## iPadOS 与 iOS

ADT 身份和用户态镜像属于同一设备系列。iPadOS 根使用 pad 身份，iOS 根使用 phone 身份。

| 目标 | `model` | `target-type` | `product-name` | `artwork-device-idiom` |
| --- | --- | --- | --- | --- |
| iPadOS | `iPad7,1` | `J120` | `iPad Pro (12.9-inch) (2nd generation)` | `pad` |
| iOS | `iPhone10,3` | `D22` | `iPhone X` | `phone` |

恢复镜像见[构建环境](/zh/guide/requirements#目标-ipsw)。

格式 1 的 UniXNU 板级文件中，`[payload.adt] ipad_identity = true` 把 `--ipad-identity` 传给板级 ADT 工具，由工具写入 iPad 身份。目标为 iPhone 时，在 ADT 工具中写入 phone 值，或增加一个选择身份的板级选项。

身份向用户态描述硬件。已安装的系统仍来自 IPSW，iPadOS 根保持 iPadOS，iOS 根保持 iOS。

根节点 `compatible` 保留板子自己的字符串。Apple 板名可能匹配原始平台 kext，进入移植尚未实现的路径。

## 应用

1. 格式 2 按[设备树属性类型](/zh/porting/device-tree)在设备或 OS profile 中设置
   `[adt.product]` 与 `[adt.buttons]`。格式 1 使用所选板级 ADT 工具及其 `ipad_identity` 选项。
2. 从主仓库执行 `./unixnu payload` 和 `./unixnu bootimg`。
3. 按下文路径清理 Data 卷中的缓存答案。
4. 启动新镜像，检查设备名称、锁屏提示、上滑手势和键盘布局。

格式 1 的 Python ADT 工具可直接写入节点：

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
