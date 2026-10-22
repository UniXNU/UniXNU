# 设备树

设备移植涉及两棵树：

| 树 | 格式 | 使用方 |
| --- | --- | --- |
| UEFI 设备树 | 标准扁平设备树（FDT） | UEFI 固件、EFI 和 Linux 菜单项 |
| Apple 设备树（ADT） | Apple 节点编码 | XNU 平台专家和驱动 |

负载步骤在内核旁边生成 `kernel.macho.adt`，DarwinBoot 从菜单项目录读取它。

## Apple 设备树编码

Apple 设备树使用紧凑节点编码：

```
u32 property_count
u32 child_count
每个属性:
  char name[32]
  u32 length
  u8  value[length]
  填充到 4 字节
每个子节点:
  node
```

每个节点带有自己的 `name` 属性和结尾 NUL。

这棵树使用 Apple 自己的编码。`dtc` 编译 FDT 源码，libfdt 读取 FDT blob，两者只适用于 UEFI 树。

## 必需节点

通用 `ArmDTPlatform` 要求以下顶层节点：

| 节点 | 必需内容 |
| --- | --- |
| `/chosen` | `random-seed`、CHRP NVRAM proxy、DRAM 描述、`osenvironment` |
| `/cpus` | 每个核心一个 `cpuN` 子节点 |
| `/arm-io` | 带 `#address-cells`、`#size-cells`、`ranges` 的总线节点 |
| `/defaults` | 平台默认值 |
| `/options` | 平台选项 |

缺少任一节点时平台专家 `configure()` 失败。`/chosen` 没有可用 NVRAM proxy 时同样失败。

### NVRAM proxy

XNU 从 `/chosen` 发布真实 `IODTNVRAM`。proxy 使用 CHRP bank 格式：

| 属性 | 内容 |
| --- | --- |
| `nvram-bank-size` | bank 大小，32 位 |
| `nvram-bank-count` | bank 数量，32 位 |
| `nvram-current-bank` | 当前 bank，32 位 |
| `nvram-proxy-data` | bank 镜像 |

bank 镜像包含 `nvram` 头、带两 KiB 数据区的 `common` 头和 `free` 头。`common` 数据区偏移 16 处有 Adler-32 校验。

没有持久 NVRAM 控制器的设备使用空 proxy 即可。

### chosen 属性

| 属性 | 类型 | 用途 |
| --- | --- | --- |
| `random-seed` | 64 字节 | 内核熵种子 |
| `unique-chip-id` | 64 位 | 与 `chip-id` 一起生成 `IOPlatformUUID` |
| `chip-id` | 32 位 | 平台身份种子 |
| `osenvironment` | 字符串 | `main`、`recoveryos` 或 `ramdisk` |
| `dram-base` | 64 位 | 物理 DRAM 基址 |
| `dram-size` | 64 位 | 物理 DRAM 大小 |
| `crypto-hash-method` | 字符串 | Image4 哈希方法，例如 `sha2-384` |
| `root-matching` | 字典 | 根卷匹配字典 |
| `ephemeral-storage` | 32 位 | 标记可写 Data 卷为临时 |
| `darwinboot-memory-size` | 64 位 | 连续窗口请求，256 MiB 到 8 GiB，2 MiB 步进 |
| `amfi-only-platform-code` | 32 位 | 保持 AMFI 平台代码策略 |
| `boot-manifest-hash` | 字节 | owner 路径的启动 manifest 哈希 |

`unique-chip-id` 和 `chip-id` 生成 `IOPlatformUUID`。缺少它们时，以零超时调用 `gethostuuid()` 的进程会一直等待。

### memory-map

`/chosen/memory-map` 保存 DarwinBoot 填充的占位符：

| 属性 | 长度 | 填充内容 |
| --- | --- | --- |
| `RAMDisk` | 16 字节 | dense Data 镜像地址和大小 |
| `PackedRAMDisk` | 16 字节 | packed Data 镜像地址和大小 |
| `TrustCache` | 16 字节 | trust cache 地址和大小 |

每个输入都需要占位符。缺少占位符时 DarwinBoot 返回 `EFI_COMPROMISED_DATA`。

### CPU

```c
cpu0 {
  name = "cpu0";
  state = "running";
  reg = <0>;
  device_type = "cpu";
  compatible = "arm,cortex-a715";
  timebase-frequency = <19200000>;
}
```

第一个 CPU 是启动 CPU，`reg` 是 MPIDR affinity 值。多于一个 CPU 时加入 `/psci` 节点，`compatible = "arm,psci-1.0"`，`method` 为 `"smc"` 或 `"hvc"`。

### arm-io

```c
arm-io {
  name = "arm-io";
  device_type = "arm-io";
  #address-cells = <2>;
  #size-cells = <2>;
  ranges = <0 0x17000000 0x08000000>;
  intc {
    name = "intc";
    compatible = "arm,gic-v3";
    reg = <...>;
  };
}
```

`ranges` 映射总线窗口。子节点 `reg` 使用窗口内偏移。低于窗口基址的设备无法作为子节点表达，驱动改用板级常量中的物理地址。

### product 与 buttons

`/product` 提供产品名和型号，`/buttons` 提供按钮名称和 `home-button-type`。MobileGestalt 和平台代码读取这些节点。完整属性、手势设置和设备系列切换见 [MobileGestalt 身份](/zh/guide/mobilegestalt)。

### 平台默认值

`/defaults` 提供平台选项。例如 `sleep-disabled = <1>` 在未实现 suspend 时阻止 CPU 停驻。

## ADT 工具契约

`[payload.adt] tool` 指定设备仓库中的脚本。负载步骤按[启动负载](/zh/concepts/payload)列出的选项调用它。

工具把树写到 `Payloads/kernel.macho.adt`，并保证：

1. 生成合法 Apple 节点编码。
2. 加入新的 64 字节 `random-seed`。
3. 为输入加入 memory-map 占位符。
4. 提供种子时加入 `unique-chip-id` 和 `chip-id`。
5. 提供 UUID 时加入 `root-matching`。
6. Data 种子存在时加入 `ephemeral-storage`。
7. 提供窗口覆盖值时加入 `darwinboot-memory-size`。

## UEFI 设备树

固件通过 `EFI_DTB_TABLE` 暴露自己的 FDT。UniXNU 可以修改它并传给 EFI 或 Linux 菜单项。

菜单项选择设备树：

```toml
[[entry]]
id = "linux"
type = "linux"
path = "Payloads/Image"
dtb = "DeviceTree/board.dtb"
```

`dtb = "firmware"` 使用固件树，路径使用负载卷上的文件。树复制时预留 64 KiB，先应用全局补丁，再应用菜单项补丁，最后应用 `[entry.chosen]`。

补丁支持 `set`、`delete-prop`、`add-node`、`delete-node` 和 `overlay`：

```toml
[[dt_patch]]
op = "set"
node = "/chosen"
prop = "bootargs"
value = "console=ttyAMA0"

[[dt_patch]]
op = "overlay"
file = "DeviceTree/board.dtbo"
```

DarwinBoot 读取 `.adt` sidecar。`xnu` 菜单项设置 `dtb` 时会在加载器请求中携带设备树，发布版 DarwinBoot 会拒绝带非空设备树的请求。

## 启动镜像设备树

启动镜像在 gzip 流后携带设备树。原有 bootloader 可能需要固件树中没有的节点。

```toml
[[bootimg.dtb_node]]
path = "/reserved-memory/splash_region"
props = [
  { name = "label", type = "s", value = "cont_splash_region" },
  { name = "reg", type = "x", value = ["0x0", "0xb8000000", "0x0", "0x2b00000"] },
]
```

`unixnu bootimg` 用 `fdtput` 应用这些节点，并校验整数属性往返一致。

## 参考生成器

| 生成器 | 用途 |
| --- | --- |
| `scripts/qemu-entry/make-dt.py` | 单 CPU、可选 GICv3、VirtIO 和 NVRAM 的 QEMU fixture |
| 设备仓库的 `make-<device>-adt.py` | 带板级地址和身份的 ADT |

QEMU 生成器是最小完整示例。真实板级的数值记录在[设备](/zh/devices/)页面。

## 下一步

- [启动负载](/zh/concepts/payload)
- [设备树匹配](/zh/drivers/device-tree-matching)
- [bring-up 顺序](/zh/porting/bring-up)
