# 迁移设备适配

## 为什么迁移

格式 2 让多个设备复用 SoC 支持、OS profile 和组件构建配方。共享 SoC 仓库保存控制器资源和平台操作，设备仓库负责板级连接、固件选择和设备策略。公共修复集中维护，其他设备需要提供的输入也有明确位置。组件目录列出实现的硬件范围和 ABI 要求；按设备、OS profile 和配置划分的输出目录保存各自的补丁后内核与生成文件。

本指南将已有设备仓库转换为格式 2。完成后，设备具有固定版本的 SoC 源码、板级 DTS、完整组件选择，以及可重复执行的内核、固件和 payload 构建命令。新设备从[移植设备](/zh/porting/steps)开始。已有格式 2 设备可按下列检查复核配置。两条流程均按相同的[仓库要求和发布步骤](/zh/porting/device-repository#completion)完成，包括添加 `unixnu` GitHub topic。

## 开始前

阅读将要修改的仓库根目录 `AGENTS.md`、[设备仓库规范](/zh/porting/device-repository)和[组件目录](/zh/reference/components)，准备[主机构建工具](/zh/guide/requirements)。以下命令从 UniXNU 主仓库执行，并使用同一个 shell。将这些值改成已有设备及 defconfig：

```sh
DEVICE=myboard
DEVICE_DIR="../UniXNU-$DEVICE"
DEFCONFIG="${DEVICE}_defconfig"
MIGRATION_DIR="$PWD/out/migration-$DEVICE"
mkdir -p "$MIGRATION_DIR"
```

`examples/device/` 提供单个文件的示例。在已有设备仓库中逐项修改，保留硬件值、补丁、脚本和源码固定版本。

## 1. 记录当前配置

```sh
git -C "$DEVICE_DIR" status --short
git -C "$DEVICE_DIR" submodule status --recursive
python3 - "$DEVICE_DIR/board.toml" <<'PYCODE'
import pathlib, sys, tomllib
board = tomllib.loads(pathlib.Path(sys.argv[1]).read_text())
print("schema_version:", board.get("schema_version", 1))
print("defconfig:", board.get("kernel", {}).get("defconfig"))
PYCODE
./unixnu status --json -D "$DEVICE_DIR" > "$MIGRATION_DIR/before.json"
cp "$DEVICE_DIR/board.toml" "$MIGRATION_DIR/board-before.toml"
```

省略 `schema_version` 时使用格式 1。记录本地改动和未跟踪文件，在移动文件前，将需要保留的源码改动保存到工作分支。若 `status` 失败，先补齐它报告的源码或配置，使报告能完整记录起始状态。

清点 `.gitmodules`、`feeds.toml`、`local.toml`、`unixnu.lock`、构建脚本、CI、固件 DSC/FDF 和文档。逐个记录组件的 origin URL、检出提交、本地改动、使用者和构建输出：

```sh
rg -n 'Native|drivers/|kits/|archives|patches|make-.*-adt' "$DEVICE_DIR"
git -C <component-checkout> remote get-url origin
git -C <component-checkout> rev-parse HEAD
git -C <component-checkout> status --short
```

**完成结果：** 保存当前配置，并列出每项能力对应的源码、版本和外部输入。

## 2. 选择 SoC 与 OS profile

按[SoC 支持步骤](/zh/porting/soc-support)选择或建立匹配的共享仓库，
确认 `soc.toml`、配置片段、DTSI 和补丁系列，并选择已审查的提交。

将已有配置按下表确定归属：

| 配置 | 位置 |
| --- | --- |
| ARM64 公共配置和补丁 | `UniXNU/profiles/arch/arm64/` |
| SoC 寄存器、中断、CPU 拓扑和平台操作 | `UniXNU-<soc>-common` |
| XNU/IPSW 版本、预链接根组件、ABI 和 OS 修复 | `UniXNU/profiles/os/<profile>/` |
| 板级连接、启用的外设、固件和电源策略 | 设备 DTS、`board.toml` 和 `package/` |
| 分区布局和镜像参数 | 设备 `board.toml` |
| 可复用驱动配方和依赖 | `UniXNU/components.toml` 与组件仓库 |
| 私有固件来源和哈希 | 设备 `proprietary-files.txt` |

移动配置前，逐项与所选 profile 比较；设备值不同时，保留板级覆盖。OS profile 必须匹配设备使用的 kernelcache 和 ABI 输入。为其他 OS 版本建立 profile 时，按[预链接指南](/zh/concepts/prelink)准备输入。

以下以 SM8550 为例，检查本地 SoC 仓库并取得具体版本：

```sh
SOC_DIR=../UniXNU-sm8550-common
```

本地尚无仓库时先创建：

```sh
git clone https://github.com/UniXNU/UniXNU-sm8550-common "$SOC_DIR"
```

检查所选仓库：

```sh
git -C "$SOC_DIR" rev-parse HEAD
git -C "$SOC_DIR" status --short
```

在设备 `feeds.toml` 中添加以下条目，将 `REQUIRED_SOC_COMMIT` 替换为已审查的 40 位提交：

```toml
[[source]]
name = "sm8550"
kind = "soc"
git = "https://github.com/UniXNU/UniXNU-sm8550-common"
commit = "REQUIRED_SOC_COMMIT"
```

保留其他必需源码。发布构建使用已提交的固定版本。开发本地 SoC 改动时，为解析设备的命令添加 `--local-module soc:sm8550=../UniXNU-sm8550-common`，并在记录中注明覆盖。

**完成结果：** SoC 源码版本已固定，OS profile 已选定，每项配置都有明确归属。

## 3. 按源码身份更新组件名称 {#组件名称}

| 官方兼容输入 | 规范 ID |
| --- | --- |
| `NativeAdreno` | `Adreno740` |
| `NativeMetal` | `AdrenoMetal` |
| `NativeUfs` | `ShengUfs` |
| `NativeHidInput` | `ShengHidInput` |
| `NativeNovatekTouch` | `ShengNovatekTouch` |
| `NativeGeniSpi` | `QcomGeniSpi` |
| `NativeMobileDisplay` | `GopFramebuffer` |
| `NativeAES` | `SoftwareAES` |
| `NativeKeyStoreEvents` | `AppleKeyStoreState` |
| `NativeRamBlock` | `RamBlock` |
| `NativeVirtioBlock` | `VirtioMmioBlock` |
| `NativeVirtioConsole` | `VirtioMmioConsole` |
| `NativePrelink` | `XnuPrelink` |
| `NativeWifi` | `Ath12kWifi` |

规范 ID 用于官方仓库 URL、检出目录、feeds、依赖、构建入口、archive、构建目录、
CI 和文档。保留 `runtime_identifiers` 记录的源文件名、运行时类名、bundle ID、
插件文件名、导出符号和协议 ID。

Adreno740 提供 A740 内核 GPU 接口，AdrenoMetal 提供 Metal 前端。元数据分别记录
A740/SM8550 实现范围和各设备验证结果。设备提供固件、电源策略、内存调整和显示集成。

改名前，先将各组件 origin URL 与组件目录对应。社区分支保留自身仓库身份和固定版本；将其作为独立组件选择时，在维护的组件目录中补齐元数据与构建配方。

逐个处理需要改名的官方组件：

1. 已有子模块使用 `git -C "$DEVICE_DIR" mv <old-path> <new-path>` 移动，Git 会更新其 `.gitmodules` 路径。
2. 按组件目录更新 `.gitmodules` 中的 URL，或更新 `feeds.toml` 条目。
3. 修改 `.gitmodules` 后运行 `git -C "$DEVICE_DIR" submodule sync --recursive`。
4. 根据组件目录的配方和 `outputs`，更新组件 ID、脚本名称、archive 路径及使用者。
5. 将检出提交和本地改动与步骤 1 的清单核对。

使用[驱动适配清单](/zh/porting/drivers)将存储、GPU、Wi-Fi、亮度、输入、音频和电源对应到具体实现，同时检查设备 package 中的代码和独立组件仓库。

**完成结果：** 每个所选组件都对应预期源码与构建配方，硬件要求和板级依赖已记录。

## 4. 修改 board.toml 与内核输入

在首个表之前添加 `schema_version = 2`，将以下字段合入已有表。示例选择 SM8550 和 iPadOS 17.7.11；设备名称、kit、defconfig 和 DTS 路径替换为当前设备值：

```toml
schema_version = 2

[board]
name = "myboard"
kit = "myboard"
soc = "SM8550"
soc_source = "sm8550"
os_profile = "ipados-17.7.11-21H461"

[components]
include = ["ArmDTPlatform", "ArmCpu", "SoftwareAES", "XnuPrelink", "DarwinBoot"]

[kernel]
defconfig = "myboard_defconfig"
config_fragments = ["arch:configs/common.config", "soc:configs/sm8550.config", "os:configs/ipados.config"]
patch_series = ["arch:patches/xnu/series", "soc:patches/xnu/series", "os:patches/xnu/series", "device:patches/xnu/series"]

[device_tree]
source = "device:dts/myboard.dts"
include_dirs = ["soc:dts"]
```

运行解析器前完成这些修改：

1. 根据步骤 3，在 `components.include` 中补齐设备需要的全部驱动。
2. 保留 `configs/<defconfig>` 及必需开关。共享片段按列表顺序应用，设备 defconfig 最后应用。
3. 创建 `patches/xnu/series`，每行填写一个相对于该目录的板级补丁路径。全部补丁来自共享 profile 时，可使用空 series。
4. 将继承的 archive 计划与设备必需的构建器比较。设置 `kernel.archives` 时写出完整有序列表。组件目录配方使用 `component:<ID>`，辅助构建器使用脚本文件名。[参考 board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/main/board.toml)提供了两者组合的完整示例。
5. 保留设备的固件路径、分区布局、启动镜像设置和 payload 策略。OS 属性放在所选 OS profile，板级 ADT 覆盖放在设备带类型的 `[adt]` 表中。

**表按键合并，数组整体替换。** 组件、配置片段、补丁序列和 archive 列表都遵循此规则。覆盖数组时写出全部必需条目。显式 archive 计划必须覆盖每个所选内核阶段配方，组件构建顺序由依赖确定。

**完成结果：** 设备配置包含四层 profile、完整组件选择、有序内核输入和原有板级设置。

## 5. 将硬件描述转换为 DTS

阅读[设备树规范](/zh/porting/device-tree)和[驱动匹配规则](/zh/drivers/device-tree-matching)。检查已有 ADT 脚本及驱动读取的属性，按下表转换：

| 输入 | 操作 |
| --- | --- |
| CPU、GIC、计时器和共享控制器资源 | 复用或补充 SoC DTSI 中的描述 |
| 板级内存、CPU 选择、外设和保留区域 | 定义在 `dts/<device>.dts` |
| XNU 驱动读取的节点 | 用 `unixnu,adt-name` 和 compatible 属性保留匹配名称 |
| 地址范围、中断和引用 | 声明父节点 cell 宽度、`ranges`、中断提供者及引用参数数量 |
| Apple 身份和带类型的 OS 属性 | 定义在 OS 的 `[adt]` 表 |
| 根卷 UUID 和 payload 交接选项 | 保留在设备 `[payload.adt]` |

板级 DTS 包含所选 SoC DTSI，所有硬件值来自目标设备。准备好所选 SoC 检出后编译：

```sh
dtc -I dts -O dtb -i "$SOC_DIR/dts" \
  -o "$MIGRATION_DIR/hardware.dtb" "$DEVICE_DIR/dts/$DEVICE.dts"
```

按 `[device_tree] source` 调整文件名。解决编译错误，并对照绑定检查警告。格式 2 在 `./unixnu payload` 阶段将该硬件描述交给公共 ADT 生成器，添加 NVRAM、熵和 payload 交接属性。

**完成结果：** 硬件 DTB 编译成功，包含所选驱动需要的资源和属性。

## 6. 解析迁移后的配置

```sh
./unixnu defconfig "$DEFCONFIG" -D "$DEVICE_DIR"
./unixnu fetch -D "$DEVICE_DIR"
./unixnu status --json -D "$DEVICE_DIR" > "$MIGRATION_DIR/after.json"
./unixnu tree -D "$DEVICE_DIR"
python3 - "$MIGRATION_DIR/after.json" <<'PYCODE'
import json, pathlib, sys
status = json.loads(pathlib.Path(sys.argv[1]).read_text())
for key in ("output", "configuration", "profiles", "components", "patch_order"):
    print(key, json.dumps(status.get(key), indent=2))
PYCODE
```

将报告与步骤 1 至 5 对照：

- profile 按 ARM64、SoC、OS、设备顺序解析。
- 源码、版本和本地覆盖与清单一致。
- 组件范围和依赖符合设备要求。
- 补丁前置条件位于使用者之前，每个补丁出现一次。
- `output` 指向 `out/<device>/<os_profile>/<config>/`。

更新本地脚本和 CI，使用共享解析器及其 `output` 路径。组装的 `tree/` 包含共享脚本、所选模块和位于 `kits/<board.kit>` 的设备 package。检查保留的私有脚本所需的辅助文件及源码路径。

**完成结果：** 解析配置和组装目录与迁移清单一致。后续日志与产物检查使用该输出目录。

## 7. 准备固件和本地构建输入

在设备 UEFI 的 DSC 和 FDF 中包含 UniXNU、UniXNUDxe、DarwinBoot、`UniXNURamDiskDxe`、DiskIoDxe 和 FAT 支持。按[必需的固件集成](/zh/porting/uefi-firmware#required-integration)设置模块路径和库映射。核对 `board.toml` 的 `[firmware]` 与固件仓库中的配置名、DSC、FD 路径和 package 路径。

已有 `unixnu.local.toml` 时直接编辑；尚无该文件时，将 `unixnu.example.toml` 复制到此路径。在 `[build]` 下填写设备仓库、固件仓库、固件 DTB、kernelcache 和设备需要的 payload 输入。[本地配置参考](/zh/reference/configuration#local-build-inputs)列出各字段。私有输入保存到本地路径，来源和版本写入适配记录。例如，将以下值填写为设备的实际路径和种子：

```toml
[build]
device = "../UniXNU-myboard"
uefi = "../uefi-myboard"
dtb = "/path/to/firmware.dtb"
kernelcache = "/path/to/kernelcache"
unique_chip_id = "REQUIRED_DEVICE_SEED"
trust_cache = "/path/to/trustcache.bundle"
data_ramdisk = "/path/to/data-seed.dbr"
```

所选 payload 需要 trust cache 或 Data seed 时，填写对应条目。

启用 `panic_screen = true` 时，固件仓库提供 `FrameBufferSerialPortLib/Font.h`，UniXNU 主仓库提供入口探针和渲染源码。参见 [panic 屏幕输入](/zh/guide/debugging#panic-屏幕)。

### 构建输入 {#build-inputs}

按所选 archive 与镜像配方准备输入：

- 含 iPhoneOS SDK 的完整 Xcode。
- `storage-abi/interface-audit.json` 及匹配的存储 ABI 输入。
- HID 和显示构建器使用的已确认 `build/xnu-prelink/*candidate.macho` 及其 JSON ABI 记录。
- 所选配置需要的 VerifiedRoot 和 verified VirtIO 策略 archive。
- `proprietary-files.txt` 列出的板级固件，包括 GPU 固件。
- Metal 插件使用的 `.cache/mesa-work`、已构建的 Turnip 和 metal2vulkan 输入。
- 所选 IPSW 成员、平台种子、trust cache、Data seed 和固件 DTB。

按所选配方和[驱动适配](/zh/porting/drivers)中链接的子系统指南确定所需输入。

**完成结果：** 固件集成和本地输入路径已配置。缺失输入与依赖它的构建步骤一并记录。

## 8. 按依赖顺序构建

上一条命令成功后，再执行下一条：

```sh
./unixnu ipsw fetch -D "$DEVICE_DIR"
./unixnu kernel -D "$DEVICE_DIR"
./unixnu build package -D "$DEVICE_DIR"
./unixnu firmware -D "$DEVICE_DIR"
./unixnu payload -D "$DEVICE_DIR"
./unixnu bootimg -D "$DEVICE_DIR"
```

简写命令读取 `unixnu.local.toml`。根镜像准备和组件专用构建前置条件见[构建指南](/zh/building)。修改启动参数后，重新生成 payload 和启动镜像。

| 相对于解析输出目录的路径 | 检查内容 |
| --- | --- |
| `.config` | 必需设备开关和 archive 路径 |
| `tree/.cache/xnu-work/` | 目标独立的补丁后 XNU 源码 |
| `kernel/kernel.macho` | 内核链接与预链接成功 |
| `device-tree/hardware.dtb` | payload 组装时编译的硬件树 |
| `payload/payload.img` | 内核、ADT 和已配置的可选输入 |
| `payload/payload.json` | 最终启动参数和 payload 输入 |
| `boot/boot.img` | 固件、固件 DTB 与 payload 打包成功 |
| `logs/` | 上述命令的日志 |

FD 写入固件仓库中 `[firmware] fd` 指定的路径。读取输出目录并检查打包文件：

```sh
OUTPUT_DIR=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["output"])' "$MIGRATION_DIR/after.json")
mtype -i "$OUTPUT_DIR/payload/payload.img" ::/EFI/UniXNU/unixnu.toml
mcopy -i "$OUTPUT_DIR/payload/payload.img" \
  ::/EFI/UniXNU/Payloads/kernel.macho.adt "$MIGRATION_DIR/kernel.macho.adt"
```

核对最终[启动参数](/zh/xnu/boot-arguments#apply-arguments)，将导出的 ADT 与硬件 DTB 一起保存，供按[必需节点](/zh/porting/device-tree#必需节点)和驱动匹配规则复核。

**完成结果：** 每项成功构建记录输出和日志，待完成步骤写明所需输入。

## 9. 更新适配记录、CI 和文档

缺少 `porting.toml` 或 `.github/workflows/porting-record.yml` 时，从模板补充；已有文件直接更新。合并模板的 `.gitignore` 规则，并添加说明本机覆盖路径的 `local.toml.example`。填写设备身份、所选组件、源码版本及各部分的配置、操作和证据。按[适配记录指南](/zh/porting/records)完成后运行：

```sh
python3 scripts/porting-record.py check --device "$DEVICE_DIR"
npm --prefix docs run build
```

更新设备 README 和根目录 `AGENTS.md` 中的当前命令与必读文档，同时更新受影响的中英文站点页面、组件引用、CI 路径和固件说明。完成统一的[仓库清单](/zh/porting/device-repository#completion)，再按[发布步骤](/zh/porting/device-repository#publish)推送设备提交、添加 **`unixnu` GitHub topic**、检查 CI 并固定站点记录版本。将步骤 6 的解析配置与清单及步骤 1 的输入记录核对。完成后的仓库与新建仓库使用相同的布局、源码固定方式、构建接口、记录和发布步骤。

向其他维护者或 agent 交接时，使用以下报告：

```text
设备、defconfig 和 OS profile：
源码版本与本地覆盖：
组件选择与补丁顺序：

主机检查：
  命令 | 结果 | 输出或日志
  配置和源码解析：
  DTS 和 ADT：
  内核与预链接：
  Package 和固件：
  Payload 和启动镜像：
  适配记录和文档：

设备观察：
  设备、固件和镜像版本：
  启动 / 存储 / 显示 / 输入 / GPU / 网络 / 音频 / 电源：

待完成事项：
  所需输入或操作 | 受影响步骤 | 证据
```

主机构建结果和设备观察分别记录。设备结果按[启动验证顺序](/zh/porting/bring-up)填写，共享启动检查点参见 [QEMU 指南](/zh/reference/qemu)。

## 完整 SM8550 示例

[UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng)提供维护中的格式 2 示例。结合阅读 `board.toml`、`feeds.toml`、`configs/sheng_defconfig`、`dts/sheng.dts`、`patches/xnu/series`、`package/` 和 `porting.toml`。共享源码位于 [UniXNU-sm8550-common](https://github.com/UniXNU/UniXNU-sm8550-common)，OS profile 位于 `profiles/os/ipados-17.7.11-21H461/`，固件位于 [uefi-sheng](https://github.com/UniXNU/uefi-sheng)。

按目标设备仓库设置 `DEVICE`、`DEVICE_DIR` 和 `DEFCONFIG`，准备[构建输入](#build-inputs)，再执行步骤 6 至 9。输出目录为 `out/<device>/<os_profile>/<config>/`。所选配置提供 GPU、存储、输入、显示和镜像组件，验证结果写入设备的 `porting.toml`。

## 下一步

- [驱动适配](/zh/porting/drivers)：补齐各子系统的板级输入和集成。
- [启动验证顺序](/zh/porting/bring-up)：使用生成的镜像记录检查点。
- [调试](/zh/guide/debugging)：调查构建失败和启动停留阶段。

## 存储与输入的公开源码构建 {#source-drivers}

`ipados-27.0.1-24A446` 配置可通过 `build-sheng-source-drivers.py`，使用已准备好的
XNU 12377 C/C++ 编译参数构建 ShengUfs、ShengHidInput 和板级输入传输代码。
配置固定了 Apple [macOS 26.5 源码清单](https://github.com/apple-oss-distributions/distribution-macOS/blob/83390100289cedfe669c31a96c94326d31afa1ed/release.json)
中的 IOStorageFamily 337.100.1 与 IOHIDFamily 2238.120.5。
Apple 的 [iOS 26.5 清单](https://github.com/apple-oss-distributions/distribution-iOS/blob/f92ef8bfffdb54c4aa4709717e3609f1647f59ed/release.json)
未发布这两个 Family。macOS 公开源码版本用于构建，不代表已证明与去除符号的
原版 iOS 或 iPadOS 二进制兼容。

准备好内核构建树、与配置固定提交一致的干净源码检出，以及设备缓存中的
Novatek 固件后，在 UniXNU 中运行参考构建器：

```sh
python3 scripts/build-sheng-source-drivers.py \
  --tree /path/to/resolved/tree \
  --device /path/to/device \
  --storage-source out/driver-sources/IOStorageFamily \
  --hid-source out/driver-sources/IOHIDFamily \
  --with-storage-family
```

源码地址、标签和提交见 OS 配置中的 `git`、`ref`、`commit`。
`--touch-firmware` 可指定其他已提取固件。构建器拒绝错误源码提交、修改过的源码、
目标不匹配的内核对象或空固件。每个对象均检查 arm64e 和 iOS 部署版本；编译命令、
依赖文件哈希、警告、固件身份和剩余导入保存在目标树的 `build/sheng-source-drivers`。

`--with-storage-family` 编译 14 个公开内核 C++ 源文件，并使用 Apple DriverKit SDK
生成、编译 IIG 实现；Apple 源码的警告会记录，但不作为错误。
输入传输 archive 包含板级触控、按键、GENI SPI、Novatek 协议、触点处理和固件，
无需调用旧显示驱动构建器。HID 使用 `IOHIDDevice.h` 和 `kIOHIDReportTypeInput`；
源码模式不安装 Darwin 23 固定虚表槽号的边缘事件补丁。旧 HID 构建器拒绝 arm64e 目标。

这些产物是可重定位 archive，尚不是启动镜像。报告中的 `link_qualified`、
`runtime_qualified` 和 `edge_gestures_qualified` 均为 false。HID 诊断与启动、
根卷策略与加密对象、元类注册、目标 Family 依赖及保留的 APFS 调用方仍需接入。
不要同时注册源码版与原版的同名 IOKit 类。公开 HID 源码缺少 `IOHIDEventTypes.h`、
`IOHIDEventStructDefs.h`，设备实现还依赖私有报告与分析头文件；输入设备编译成功
不代表仅凭此次公开发布就能构建整个 IOHIDFamily。

存储头文件准备过程会在每次 archive 构建时验证所选提交并替换生成的头文件目录，
避免切换源码后继续使用旧 OS 的缓存。原有 iOS 17 ABI 与真机证据继续标注其实际 OS 版本。
