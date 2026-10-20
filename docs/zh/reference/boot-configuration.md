# 启动配置

UniXNU 启动管理器先从启动所在卷读取 `\EFI\UniXNU\unixnu.toml`，再扫描其他卷。kit 目录中的 `Kit.toml` 使用相同的 match 和注入段。

## unixnu.toml

```toml
version = 1

[boot]
timeout = 5
rotate = 0
fallback_timeout = 10
connect_all = true
default = "xnu"

[ui]
title = "UniXNU"
scale = 0
logo = true
layout = "auto"
portrait_below = 800
console = "auto"
```

### [boot]

| 键 | 默认 | 含义 |
| --- | --- | --- |
| `timeout` | 5 | 秒数，负数等待输入 |
| `rotate` | 0 | 空闲高亮轮换秒数，0 关闭 |
| `fallback_timeout` | 10 | 无输入设备时的超时 |
| `connect_all` | true | 对所有 handle 调用 `ConnectController` |
| `default` | 第一项 | 菜单项 id 或索引 |

### [ui]

| 键 | 默认 | 含义 |
| --- | --- | --- |
| `title` | `UniXNU` | 菜单标题 |
| `scale` | 0 | 字形缩放，0 自动 |
| `logo` | true | 绘制标志 |
| `layout` | `auto` | `auto`、`landscape` 或 `portrait` |
| `portrait_below` | 800 | `auto` 时，宽 / 高乘以 1000 低于此值则使用竖屏 |
| `console` | `auto` | `auto`、`graphics`、`text` 或 `none` |

竖屏布局是为手机等竖向屏幕设计的单列版式：标志位于顶部，菜单项是底部带编号的卡片，状态行在分隔线下自动换行。标志自带 UniXNU 字标，所以只有 `logo` 为 false 或 `title` 不是 `UniXNU` 时才绘制标题文字。`auto` 下，1080x2400 的屏幕（比值 450）和 3:4 平板（750）使用竖屏，4:5（800）及更宽的屏幕保持横屏布局。未设置 `scale` 时，竖屏布局取 宽度 / 270 作为字形缩放，1080 像素宽的屏幕每行约 33 个字符。

### [[driver]]

```toml
[[driver]]
path = "Drivers/MyDriver.efi"
args = "board=1"
connect = true
enabled = true
```

| 键 | 默认 | 含义 |
| --- | --- | --- |
| `path` | 必需 | 文件路径或 `fv:<GUID>` |
| `args` | | load options |
| `connect` | true | 驱动启动后连接控制器 |
| `enabled` | true | `false` 跳过 |

kit 驱动使用 `file` 代替 `path`。

### [[dt_patch]]

```toml
[[dt_patch]]
op = "set"
node = "/chosen"
prop = "bootargs"
value = "console=ttyAMA0"
type = "string"
```

| 键 | 含义 |
| --- | --- |
| `op` | `set`、`delete-prop`、`add-node`、`delete-node` 或 `overlay` |
| `node` | 绝对节点路径 |
| `prop` | `set` 和 `delete-prop` 的属性名 |
| `value` | `set` 的值 |
| `type` | `string`、`stringlist`、`u32`、`u64`、`bytes` 或 `empty` |
| `file` | `overlay` 的文件 |

补丁应用于 EFI 和 Linux 菜单项。Darwin 路径使用 `.adt` sidecar。

### [[block_slice]]

```toml
[[block_slice]]
partition = "<GPT name>"
name = "<slice name>"
offset = 0
length = 0
writable = false
enabled = true
```

| 键 | 含义 |
| --- | --- |
| `partition` | GPT 分区名 |
| `name` | 设备路径中的标签 |
| `offset` | 相对分区起始的字节偏移 |
| `length` | 字节长度，0 表示到末尾 |
| `writable` | 发布可写块设备 |
| `enabled` | `false` 跳过 |

切片以整盘形式出现，子分区方案或文件系统驱动可以绑定。

### ACPI

```toml
[acpi]
add = ["Tables/DSDT.aml", "Tables/SSDT.aml"]
```

每个表通过 `EFI_ACPI_TABLE_PROTOCOL` 安装，header 长度必须匹配文件大小。

### kit

```toml
[[kit]]
path = "Kits/MyKit.kit"
enabled = true

[kits]
autoload = true
directory = "Kits"
```

显式 kit 先加载。`autoload` 为 true 时，`directory` 下每个 `*.kit` 按名称顺序加载。

### [[entry]]

```toml
[[entry]]
id = "xnu"
title = "UniXNU"
type = "xnu"
path = "Payloads/kernel.macho"
args = "-v serial=3"
initrd = "Payloads/scratch-data.img"
confirm = "Boot the kernel?"
confirm_titles = ["Normal", "Verbose"]
confirm_args = ["", "debug=0x14e"]
enabled = true
```

| 键 | 含义 |
| --- | --- |
| `id` | 菜单项标识 |
| `title` | 菜单标题 |
| `type` | `efi`、`linux`、`action` 或 `xnu` |
| `path` | EFI 程序、Linux 镜像或内核路径 |
| `args` | load options 或内核命令行 |
| `dtb` | `firmware`、文件路径或省略 |
| `initrd` | initrd 路径 |
| `confirm` | 启动前显示的问题。该菜单项不会被倒计时启动 |
| `confirm_titles` | 可选的选项标题。需要同时给出 `confirm` 和 `confirm_args` |
| `confirm_args` | 每个选项一个参数字符串，选中项追加到 `args` |
| `action` | `action` 类型的 `reset`、`shutdown` 或 `exit` |
| `enabled` | `false` 跳过 |

带 `confirm` 的菜单项只在按 Enter 时启动。没有选项时，其他按键取消；没有输入设备的机器也取消。给出 `confirm_titles` 时，上下键切换选项，Cancel 默认选中。选中的 `confirm_args` 追加到菜单项 `args` 的副本。

默认项需要确认时，倒计时改用第一个不需要确认的菜单项。

内置配置包含 `exit`、`reset` 和 `shutdown`。找不到文件时，可移动加载器会加在它们之前。

### [entry.chosen]

```toml
[entry.chosen]
bootargs = "console=ttyAMA0"
```

每个键成为 `/chosen` 属性，在菜单项补丁之后应用。

### [[entry.kext]]

```toml
[[entry.kext]]
bundle = "Kexts/MyDriver.kext"
plist = "Contents/Info.plist"
executable = "Contents/MacOS/MyDriver"
enabled = true
```

菜单项 kext 只作用于声明它的菜单项。

### [[entry.variable]]

```toml
[[entry.variable]]
guid = "00000000-0000-0000-0000-000000000000"
name = "MyVariable"
value = "hello"
type = "ascii"
volatile = true
```

| 键 | 含义 |
| --- | --- |
| `guid` | 变量 GUID |
| `name` | 变量名 |
| `value` | 值 |
| `type` | `ascii`、`ucs2`、`u8`、`u16`、`u32`、`u64` 或 `bytes` |
| `volatile` | `false` 加入 `EFI_VARIABLE_NON_VOLATILE` |

变量在菜单项启动前设置。

### [[entry.dt_patch]]

菜单项接受自己的 `[[dt_patch]]` 数组，在全局补丁之后应用。

## Kit.toml

```toml
schema = 1

[kit]
name = "MyKit"
version = "1.0.0"
description = "Board support"

[match]
arch = "AARCH64"
fdt_compatible = ["vendor,board"]
firmware_vendor = ["Vendor"]
requires_protocol = ["00000000-0000-0000-0000-000000000000"]

[[driver]]
file = "MyDriver.efi"
args = "from-kit"

[[overlay]]
file = "board.dtbo"

[[dt_patch]]
op = "set"
node = "/chosen"
prop = "from-kit"
value = "1"
type = "u32"

[[acpi]]
file = "DSDT.aml"

[[kext]]
bundle = "MyDriver.kext"
entry = "xnu"
```

| 段 | 含义 |
| --- | --- |
| `[kit]` | 名称、版本、描述 |
| `[match]` | 所有存在的键必须匹配 |
| `[[driver]]` | 相对 kit 的驱动文件 |
| `[[overlay]]` | 相对 kit 的设备树 overlay |
| `[[dt_patch]]` | 设备树补丁 |
| `[[acpi]]` | 相对 kit 的 ACPI 表 |
| `[[kext]]` | 限定菜单项 id 的 kext 包 |

match 键：

| 键 | 含义 |
| --- | --- |
| `arch` | `AARCH64` |
| `fdt_compatible` | 固件根 `compatible` 列表中的字符串 |
| `firmware_vendor` | `gST->FirmwareVendor` 的子串 |
| `requires_protocol` | 必须已安装的 GUID |

同一个键内任意值匹配，跨键必须全部匹配。

## 菜单行为

| 条件 | 结果 |
| --- | --- |
| 有输入设备 | 倒计时到超时 |
| 无输入设备 | 使用 `fallback_timeout` |
| 负超时且有输入 | 等待按键 |
| 负超时且无输入 | 使用 `fallback_timeout` |
| 启动失败 | 返回菜单，不再倒计时 |

菜单显示配置来源、菜单项、注入摘要和第一条错误。

## 下一步

- [启动负载](/zh/concepts/payload)
- [kext 包](/zh/drivers/kexts)
- [设备配置](/zh/reference/configuration)
