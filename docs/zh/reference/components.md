# 组件目录

UniXNU 根目录的 `components.toml` 记录维护中的组件。配置通过 `[components] include`
选择规范 ID。解析器补全依赖，并在使用者之前运行依赖组件的构建命令。


## 查找并选择实现

1. 在[驱动适配清单](/zh/porting/drivers)中找到目标能力。
2. 在 `components.toml` 中搜索组件 ID，阅读实现和板级依赖。
3. 对照硬件和 OS ABI 输入，按对应适配流程补齐板级接口。
4. 在设备 profile 中选择组件，加入归档或集成步骤，再检查结果：

```sh
./unixnu status --json
```

依赖和源码版本符合目标移植后，继续[构建](/zh/building)。


## 字段

| 字段 | 含义 |
| --- | --- |
| `id` | 规范组件 ID |
| `kind`, `path` | 模块类型和检出路径 |
| `repository`, `revision` | 源码仓库和固定版本 |
| `legacy_name` | 官方兼容输入名称 |
| `function` | 组件提供的能力 |
| `scope` | 实现范围 |
| `hardware` | 所需控制器、协议或 GPU 系列 |
| `os_abi` | XNU 或用户态 ABI 要求 |
| `board_dependencies` | 固件、连接、内存或策略输入 |
| `verified_devices` | 有硬件验证记录的设备 |
| `dependencies` | 先构建的组件 ID |
| `build_stage` | 内核、payload、固件、预链接或嵌入式集成 |
| `build` | 构建命令参数 |
| `outputs` | 目标树中的输出路径 |
| `runtime_identifiers` | 源文件名、类名、bundle/plugin ID、符号和协议 |

实现范围和硬件验证分别记录。Adreno740 实现 SM8550 使用的 A740 GPU 接口。AdrenoMetal 通过 metal2vulkan 和 Turnip 提供 Metal
前端，依赖内核接口和 OS ABI。

## 选择

```toml
[components]
include = ["ArmDTPlatform", "ArmCpu", "Adreno740", "AdrenoMetal", "GopFramebuffer"]
```

内核阶段构建命令按依赖顺序运行。`[kernel] archives` 可以在辅助命令之间用 `component:<ID>` 指定组件位置。payload、固件、预链接和嵌入式条目描述对应阶段的集成。

设备的 `include` 数组替换继承的数组。完整列出所需组件，解析器补全依赖。查看组件
选择、源码版本、本地覆盖和构建顺序：

```sh
./unixnu status --json -D /path/to/device
```

实现能力前，搜索组件目录、[组件页面](/zh/drivers/repositories)、README 和源码，
核对接口、硬件范围、OS 要求与板级输入。

## 源码身份

官方兼容名称根据目录记录的仓库身份解析。例如，官方 `UniXNU/NativeAdreno` 源码
解析为 `Adreno740`。`another-owner/NativeAdreno` 等源码保留自己的身份和组件选择。
编辑 feed 前核对 remote 和版本。

[迁移名称表](/zh/porting/migration#组件名称)列出兼容输入。源文件名和运行时标识符
保持 ABI 使用的值。例如，`AdrenoMetal` 组件发布 `NativeAdrenoMetal` 插件文件。
