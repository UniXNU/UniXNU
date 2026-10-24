# 设备树匹配

驱动通过 IOKit personality 绑定到 provider。personality 是匹配键字典。

## 操作步骤 {#procedure}

1. 在源码中找到驱动的 [provider 类](#provider-类)和 personality，记录 `IOClass`、`IOProviderClass` 及匹配键。
2. 将 personality 与生成的[设备树节点](#设备树节点)比较，按[示例](#匹配示例)核对名称、compatible 和属性类型。
3. 修改所属 personality 或 DTS/profile 属性，结合[属性读取代码](#读取属性)确认寄存器宽度与引用编码符合预期。
4. 修改 personality 后重建内核；修改 ADT 后重建 payload 和启动镜像。检查 [probe 顺序](#probe-顺序)及驱动启动日志，确认绑定到预期 provider。

## personality 键

| 键 | 含义 |
| --- | --- |
| `IOClass` | 驱动类 |
| `IOProviderClass` | Provider 类 |
| `IONameMatch` | Provider 名称或 `compatible` 值 |
| `IOPropertyMatch` | Provider 属性精确匹配字典 |
| `IOProbeScore` | 分数越高越先 probe |
| `IOMatchCategory` | 匹配类别，允许第二个驱动匹配同一 provider |
| `IOResourceMatch` | probe 前必须发布的资源 |
| `IOProviderMergeProperties` | 加到 provider 的属性 |

没有 `IONameMatch` 或 `IOPropertyMatch` 的 personality 匹配该类的所有 provider，`IOProbeScore` 决定候选顺序。

## Provider 类

| Provider | 发布方 | 用途 |
| --- | --- | --- |
| `IOPlatformExpertDevice` | 平台专家 | 平台身份、product、buttons |
| `IOPlatformDevice` | `ArmDTPlatform` 为每个 `arm-io` 子节点发布 | SoC 设备 |
| `IOResources` | IOKit | AES、RAM 块等全局资源 |
| `IOMedia` | 分区和文件系统栈 | 根卷匹配 |
| `IOBlockStorageDevice` | 存储驱动 | 块设备客户端 |

`ArmDTPlatform` 把 nub 附加到平台专家上。nub 保留设备树父节点，`reg` 和 `ranges` 通过 `arm-io` 解析。

## 匹配示例

### 按 compatible 匹配平台设备

```c
"   ,{"
"     'IOClass'         = NativeUfs;"
"     'IOProviderClass' = IOPlatformDevice;"
"     'IONameMatch'     = 'qcom,sm8550-ufshc';"
"     'IOProbeScore'    = 1000:32;"
"   }"
```

`IONameMatch` 与 provider 名称和 `compatible` 字符串列表比较。

### 全局资源

```c
"   ,{"
"     'IOClass'         = NativeAES;"
"     'IOProviderClass' = IOResources;"
"     'IOResourceMatch' = IOBSD;"
"     'IOProbeScore'    = 1000:32;"
"   }"
```

`IOResourceMatch = IOBSD` 等到 BSD 子系统发布资源。

### 按 UUID 匹配根卷

```xml
<key>IOProviderClass</key><string>IOMedia</string>
<key>IOPropertyMatch</key>
<dict>
  <key>UUID</key><string>00000000-0000-0000-0000-000000000000</string>
</dict>
```

该字典存放在 `/chosen/root-matching`。

## 设备树节点

格式 2 按[设备树指南](/zh/porting/device-tree)编辑硬件 DTS，SoC DTSI 声明控制器资源。
使用 SM8550 UFS host 的板级源码启用已有节点：

```text
&ufs {
    status = "okay";
};
```

包含的 SoC 节点声明 `reg = <0 0x1d84000 0 0x3000>` 和 `unixnu,adt-name = "ufshc"`。
父节点使用两个地址 cell、两个大小 cell 与恒等 `ranges`。
转换器将范围导出到 `/arm-io/ufshc`，编码为相对 `arm-io` 基址的小端 u64 偏移及 u64 大小。
按 [UFS 适配](/zh/porting/ufs)在消费端驱动配置时钟、电源和 DMA。

## 读取属性

```cpp
OSData *data = OSDynamicCast(OSData, provider->getProperty("reg"));
if (data == nullptr || data->getLength() != 2 * sizeof(uint64_t)) {
  return false;
}
uint64_t range[2];
memcpy(range, data->getBytesNoCopy(), sizeof(range));
uint64_t physicalAddress = range[0];
uint64_t length = range[1];
```

此例在小端 ARM64 上读取一个格式 2 ADT 范围。驱动使用多个范围时，应验证并读取每个地址/大小对。

字符串属性：

```cpp
OSData *compatible = OSDynamicCast(OSData, provider->getProperty("compatible"));
if (compatible == nullptr || compatible->getLength() == 0) {
  return false;
}
const char *value = (const char *)compatible->getBytesNoCopy();
```

字符串列表是连续的 NUL 结尾字符串。

## overlay 与补丁

kit 可以应用设备树 overlay：

```toml
[[overlay]]
file = "board.dtbo"
```

配置可以修改属性：

```toml
[[dt_patch]]
op = "set"
node = "/arm-io/intc"
prop = "status"
value = "disabled"
```

补丁应用于 EFI 和 Linux 菜单项。Darwin 路径读取 `.adt` sidecar。

## probe 顺序

1. 平台专家发布 provider。
2. IOKit 收集 `IOProviderClass` 匹配的 personality。
3. `IONameMatch` 或 `IOPropertyMatch` 不匹配的项被跳过。
4. `IOResourceMatch` 对应的 provider 必须已发布。
5. 剩余候选按 `IOProbeScore` 排序。
6. 每个候选运行 `probe()`。
7. 启动成功的最高分候选获得 provider。

## 下一步

- [XNU 驱动](/zh/drivers/xnu-drivers)
- [设备树](/zh/porting/device-tree)
- [kext 包](/zh/drivers/kexts)
