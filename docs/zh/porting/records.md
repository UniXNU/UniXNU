# 设备适配记录

格式 2 设备仓库维护 `porting.toml`，维护者和 agent 在开发过程中更新同一份记录。
文档站从固定版本的源码快照生成设备页。

## 操作步骤 {#procedure}

1. 从 `examples/device/porting.toml` 创建记录，或编辑已有设备记录，确保设备身份与 `board.toml` 一致。
2. 按[记录字段](#记录格式)填写每个[必需部分](#必需部分)，包含所选组件、板级 package 代码、输入和有序操作。
3. 按源码、主机或设备证据选择[完成等级](#completion-levels)，记录缺失输入和下一项具体操作。
4. 运行[改动流程](#改动流程)中的检查器，修复报告的身份、覆盖范围和证据错误。
5. 发布设备提交，按[发布与复用](#publishing-and-reuse)操作，确认生成页面链接到已发布版本。

## 必需部分

每个部分记录输入、配置、步骤、开发经验、完成条件、当前范围、下一步和证据。

| 部分 | 必需技术信息 |
| --- | --- |
| 配置 | SoC 和 OS 配置、源码固定版本、组件选择、数组替换、defconfig 和补丁顺序 |
| 固件与启动 | 启动格式、固件版本、PSCI、framebuffer 和内存交接 |
| CPU 与中断 | CPU affinity、启用核心、GIC 范围、定时器频率、中断和 IPI |
| 内存与 DMA | DRAM、保留区、地址转换、DMA 位宽、缓存规则和 SMMU 所有权 |
| 存储与根卷 | 控制器、PHY、时钟、复位、电源、SMMU stream、DMA、LUN、GPT、根卷和持久 Data |
| 显示 | 控制器或 GOP、面板、stride、格式、时序、背光和呈现 |
| 输入 | 总线、传感器协议、引脚、中断、固件、触点 ID 和坐标映射 |
| GPU | GPU/GMU 型号、固件、电源请求、SMMU、提交、fence、前端 ABI 和呈现 |
| 网络 | 总线、固件、中断、DMA、OS 接口、连接和数据包传输 |
| 音频 | DSP、codec、时钟、固件服务、路由和播放/录音 |
| 电源 | 稳压器、时钟、电池单位、固件所有权和支持的状态转换 |
| 镜像组装 | XNU/IPSW 版本、ABI 输入、补丁顺序、ADT、payload 和启动镜像格式 |
| 诊断 | 日志通道、检查点、恢复方法、命令和镜像/源码版本 |

其他外设增加独立部分。所选组件及其目录依赖必须归属某个部分。超出设备范围的功能
使用 `not-applicable`，在 `limits` 中说明原因；待开发功能使用 `planned`。

## 记录格式

复制 `examples/device/porting.toml`。设备名称、SoC 和 OS 配置必须与 `board.toml`
一致。记录本身使用格式 1，`schema_version` 保持 `1`，与 `board.toml` 的
`schema_version = 2` 不同。每个 `[[area]]` 包含以下字段：

| 字段 | 内容 |
| --- | --- |
| `id` | 稳定的部分标识符 |
| `status` | 下表定义的完成等级 |
| `components` | 组件规范名称，包括依赖 |
| `paths` | 该部分负责的仓库相对路径模式 |
| `inputs` | 硬件资源、外部输入和依赖 |
| `configuration` | 实际 TOML 字段、DTS 属性和内核选项 |
| `procedure` | 有序操作与命令 |
| `findings` | 观察、已确认原因、实现决策和复用条件 |
| `completion` | 各阶段需要观察到的结果 |
| `limits` | 当前实现范围和待确认输入 |
| `next_action` | 下一项测量或实现操作 |
| `evidence` | 源码、主机或设备记录，包含引用和结果 |

开发经验使用具体技术事实。例如，启用硬件门控的 UFS AHB 分支在空闲时可能报告
`CLK_OFF`，探测过程需要一起检查使能位和门控位，并引用实现或寄存器记录。
原因未查明时，记录现象和下一项测量。

## 完成等级 {#completion-levels}

| 状态 | 必需证据 |
| --- | --- |
| `planned` | 所需输入和下一步 |
| `implemented` | 源码引用和实现范围 |
| `host-verified` | 主机命令、完整源码提交、结果和可访问的日志 |
| `device-verified` | 设备命令、完整源码提交、结果，以及标明设备、固件和镜像的日志 |
| `not-applicable` | `limits` 中的范围说明，组件列表为空 |

每项证据包含 `kind`、`reference` 和 `result`。主机与设备证据还需要 `command`
和完整的 40 字符 `revision`。引用使用 HTTPS 或设备仓库内已提交文件的相对路径。
大型日志使用 release 或 CI 产物链接。缺少的输入记入 `limits`，对应测量记入
`next_action`。

## 改动流程

1. 实现前阅读设备记录和相关公共指南。
2. 确定受影响部分及已有组件。
3. 修改实现，并更新各受影响部分的经验或证据。
4. 接口变化时同步更新配置、步骤和完成条件。
5. 运行记录检查和实现已有的相关检查。
6. 代码和文档分别提交，放在同一个 pull request 中。
7. 发布设备改动，由目录工作流更新源码版本和生成页面。

```sh
python3 scripts/porting-record.py check --device ../UniXNU-sheng
python3 scripts/porting-record.py check --device ../UniXNU-sheng --base origin/main
```

第二条命令在待提交的设备分支上运行，比较已提交改动与基准版本。每个代码路径
需要归属部分，每个匹配部分需要更新经验或证据。Markdown 改动按文档流程审阅。
`porting.toml` 是设备记录的权威来源。

设备模板包含 `.github/workflows/porting-record.yml`。官方设备分支要求其
`Porting record` 检查通过。审阅者确认硬件事实、证据质量、组件复用和完成等级。

## 发布与复用 {#publishing-and-reuse}

按[仓库发布步骤](/zh/porting/device-repository#publish)添加 `unixnu` GitHub topic。

[目录工作流](https://github.com/UniXNU/UniXNU/actions/workflows/sync-devices.yml)
每天在 UTC 00:00 和 12:00 运行，对应 UTC+8 的 08:00 和 20:00。检索范围包括 UniXNU
组织、带 `unixnu` topic 的公开仓库，以及名称或描述包含 UniXNU 的公开仓库。
工作流按固定提交读取根目录的 `board.toml` 和 `porting.toml`。

`board.toml` 使用 `schema_version = 2`，记录使用 `schema_version = 1`。
工作流检查设备身份、必需部分、组件覆盖和证据，按有效记录生成中英文设备页、设备索引
和导航。格式 2 缺少记录或记录无效时，页面链接到仓库并说明需要补齐的记录。
已有旧格式页面保留原文，新收录的旧格式条目只包含仓库链接。

`devices.toml` 保存仓库身份、页面路径和源码版本，`docs/.vitepress/device-records/`
保存源记录。站点构建使用这些已提交快照，中英文使用相同的记录正文。
记录使用简洁英语，站点源码和部署保留在 UniXNU。

立即触发扫描：

```sh
gh workflow run sync-devices.yml --repo UniXNU/UniXNU
```

本地扫描前用 `gh auth login` 登录，或设置 `GITHUB_TOKEN`，再从 UniXNU 检出目录执行：

```sh
python3 scripts/sync-devices.py
npm --prefix docs run build
```

工作流先构建站点，再提交生成结果并通过 Docs 工作流发布该提交。
源码记录错误会写入工作流摘要。修正设备记录并发布后，下一次扫描会重新处理。

本地预览：

```sh
python3 scripts/porting-record.py site --local sheng=../UniXNU-sheng
cd docs
npx vitepress build
```

通用方法经过硬件和 ABI 条件检查后写入对应公共指南。设备记录保留具体参数和证据，
并链接指南。README 包含职责、依赖、构建入口和记录链接；`AGENTS.md` 指向相同的必读内容。

- [UFS 移植](/zh/porting/ufs)
- [设备仓库](/zh/porting/device-repository)
- [Bring-up 顺序](/zh/porting/bring-up)

按[驱动适配清单](/zh/porting/drivers)填写显示、亮度、输入、GPU、Wi-Fi、DSP、音频和电源的操作流程与完成条件。
