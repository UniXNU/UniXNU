# UEFI 固件

UEFI 固件移植来自 Mu-Silicium，提供 UniXNU 和 DarwinBoot 使用的服务。

重复构建时，在 [unixnu.local.toml](/zh/reference/configuration#local-build-inputs) 保存路径。修改启动参数后，按[参数应用流程](/zh/xnu/boot-arguments#apply-arguments)重新构建负载和启动镜像。画面停在加载器交接阶段时，按[绿条诊断](/zh/guide/debugging#green-bar)检查。

## 操作步骤 {#procedure}

1. 准备设备的 Mu-Silicium 仓库、[厂商输入](#厂商输入)和子模块，核对 `board.toml` 与其[设备配置](#设备配置)、DSC 和 FD 路径。
2. 完成[必需的集成](#required-integration)：将模块加入 DSC/FDF 并设置库映射。payload 需要 RAM-disk、DiskIo 和 FAT 驱动。
3. 将固件路径保存到本地构建配置，执行[固件构建](#构建)，确认输出 FD 的路径和大小。
4. 构建 payload，再按[启动镜像集成](#启动镜像集成)打包。启动前检查 `boot/boot.json` 和打包的 payload。
5. 在设备上按[验证](#验证)确认配置中的菜单项和 DarwinBoot 交接。菜单项缺失时按[负载发现](#payload-discovery)逐项检查。

## 必需的集成 {#required-integration}

选择设备后，从 UniXNU 仓库构建固件：

```sh
./unixnu defconfig <device>_defconfig -D ../UniXNU-<device>
./unixnu build firmware --uefi ../uefi-<device>
```

固件 DSC 的 `[Components]` 和 FDF 固件卷都需要包含以下模块：

| 模块 | 用途 |
| --- | --- |
| `UniXNUPkg/Application/UniXNU/UniXNU.inf` | 启动菜单和配置读取 |
| `UniXNUPkg/Driver/UniXNUDxe/UniXNUDxe.inf` | 注册固件启动项 |
| `DarwinBootPkg/Driver/DarwinBoot.inf` | XNU 加载器 |
| `UniXNUPkg/Driver/UniXNURamDiskDxe/UniXNURamDiskDxe.inf` | 将 Mu-Silicium FDT 中的 initrd 发布为只读块设备 |
| `MdeModulePkg/Universal/Disk/DiskIoDxe/DiskIoDxe.inf` | 为文件系统驱动提供磁盘访问 |
| `FatPkg/EnhancedFatDxe/Fat.inf` | 发布负载的 FAT 文件系统 |

在 DSC 的 `[Components]` 中直接列出路径，在 FDF 中使用 `INF <path>`。在 DSC 的 `[LibraryClasses]` 中配置共享驱动的库：

```ini
HobLib|MdePkg/Library/DxeHobLib/DxeHobLib.inf
FdtLib|MdePkg/Library/BaseFdtLib/BaseFdtLib.inf
```

负载使用分区表时还需加入 `PartitionDxe`。FAT 驱动需要平台提供 Unicode collation 服务。参考固件的 `Include/DXE.inc` 包含这些依赖。

`UniXNURamDiskDxe` 供使用 Mu-Silicium FDT 交接的设备共用，源码位于 UniXNU 的 `package/UniXNUPkg/Driver/UniXNURamDiskDxe/`。板级内存保留区和内存补充由固件平台维护。

传入的 `.fd` 必须包含这些集成，并匹配设备的固件基址和大小。`./unixnu bootimg --fd <file>` 打包指定固件。修改 DSC、FDF 或驱动后，重新构建 FD。

使用所选设备的输入构建负载，然后打包镜像：

```sh
./unixnu build payload --unique-chip-id <hex> --trust-cache <file> --data-ramdisk <seed>
./unixnu bootimg --uefi ../uefi-<device> --dtb /path/to/firmware.dtb
```

按设备负载配置提供所需选项，详见[负载输入](/zh/concepts/payload)。

## 固件日志

按[日志导出器集成步骤](/zh/porting/log-capture#firmware-setup)加入 Advanced Logger 和
`AdvancedLogDxe`，启用 Tools 菜单。在存储适配前，使用[二维码抓取](/zh/porting/log-capture#qr-logs)
保存固件输出，再继续内核交接。

## 负载发现 {#payload-discovery}

Android bootloader 将 FAT 负载放入 RAM，并把地址写入固件 FDT 的 `/chosen/linux,initrd-start` 和 `linux,initrd-end`。两个属性均使用 32 位或 64 位大端地址。范围需要包含完整的 512 字节扇区，并在 UEFI 使用期间保持保留。

Mu-Silicium SEC 把传入的 FDT 地址以 `UINT64` 保存到入口参数 HOB（`DAEE82E6-8090-4E72-BFB9-78C13CD4E359`）。`UniXNURamDiskDxe` 读取该交接并发布 Block I/O。DiskIoDxe 和 FAT 驱动提供 `EFI_SIMPLE_FILE_SYSTEM_PROTOCOL`，供 UniXNU 读取 `\EFI\UniXNU\unixnu.toml` 并列出其中的启动项。

菜单出现但缺少配置中的启动项时，依次检查：

1. `boot/boot.json` 的 `ramdisk_bytes` 大于零。
2. FD 包含 `UniXNURamDiskDxe`、DiskIoDxe 和 FAT 驱动。
3. 固件 FDT 中的 initrd 起止地址有效。
4. 串口出现 `UNIXNURAMDISK: initrd block device` 且状态成功。
5. 负载 FAT 卷包含 `EFI/UniXNU/unixnu.toml` 及其引用的文件。

RAM disk 驱动需要嵌入固件，以便在读取负载配置之前发现负载卷。

## 必需服务

| 服务 | 使用方 |
| --- | --- |
| `EFI_GRAPHICS_OUTPUT_PROTOCOL` | UniXNU 菜单、DarwinBoot framebuffer 交接、XNU 控制台 |
| `EFI_SIMPLE_TEXT_IN_PROTOCOL` | UniXNU 菜单输入 |
| `EFI_SIMPLE_FILE_SYSTEM_PROTOCOL` | 配置、负载和内核文件 |
| `EFI_BLOCK_IO_PROTOCOL` | userdata 分区和块设备切片 |
| `EFI_SERIAL_IO_PROTOCOL` | 有 UART 的板级日志 |
| `EFI_ACPI_TABLE_PROTOCOL` | 可选 ACPI 表注入 |
| `EFI_FIRMWARE_VOLUME2_PROTOCOL` | UniXNUDxe 启动选项注册 |

缺少某项服务会限制对应阶段。把驱动加入固件卷或 UniXNU 负载后再运行依赖阶段。

## Mu-Silicium 布局

```
Mu-Silicium/
  BootShim/
    BootShim.S
  Resources/
    Configs/<device>.toml
    Scripts/mkbootimg.py
  Platforms/<Vendor>/<device>Pkg/
    <device>.dsc
    <device>.fdf
  Silicon/
  Common/
```

UniXNU 驱动读取 `Resources/Configs/<name>.toml` 和 `<device>.dsc`，启动镜像使用 `Resources/Scripts/mkbootimg.py`。

## 设备配置

`Resources/Configs/<device>.toml` 提供地址和镜像参数：

```toml
[boot_shim]
requires_kernel_header = true

[uefi_fd]
base = 0x00000000
size = 0x000000

[boot_image_kernel]
kernel_compression = "gzip"
append_dtb = true

[boot_image]
header_version = 0
base = 0x00000000
kernel_offset = 0x8000
tags_offset = 0x1e00000
pagesize = 4096
```

| 键 | 含义 |
| --- | --- |
| `boot_shim.requires_kernel_header` | bootloader 检查镜像开头的 ARM64 header |
| `uefi_fd.base` | 固件卷加载物理地址 |
| `uefi_fd.size` | 固件卷精确大小 |
| `boot_image_kernel.kernel_compression` | shim 和固件卷的压缩方式 |
| `boot_image_kernel.append_dtb` | 把设备树追加到 kernel 字段 |
| `boot_image.*` | Android 启动镜像 header 参数 |

固件基址和大小编译进 BootShim，并在打包启动镜像时检查。

## DSC 与 FDF

DSC 列出 package、库和组件，FDF 把组件放入固件卷。

UniXNU 使用 `PACKAGES_PATH`：

```
{uefi}:{tree}/package:{tree}/drivers/DarwinBoot:{edk2}:...
```

`{uefi}` 是 Mu-Silicium 仓库，`{tree}` 是组装后的构建树，`{edk2}` 是 Mu_Basecore。板级文件列出全部 package 路径。

UniXNU 和 DarwinBoot 通过 INF 加入：

```
UniXNUPkg/Application/UniXNU/UniXNU.inf
UniXNUPkg/Driver/UniXNUDxe/UniXNUDxe.inf
UniXNUPkg/Driver/UniXNURamDiskDxe/UniXNURamDiskDxe.inf
DarwinBootPkg/Driver/DarwinBoot.inf
```

使用 initrd 负载时，将这些模块嵌入固件卷，把配置和内核文件放入负载 FAT 卷。

## 预检

`[firmware] preflight` 列出 EDK II 构建前运行的构建树脚本，用于检查厂商输入、固件分区或板级文件。`--skip-preflight` 跳过。

## 厂商输入

Mu-Silicium 移植需要板级厂商二进制，例如：

- 存储、显示、输入或电源的 UEFI DXE 驱动。
- ACPI 表。
- 固件分区镜像。
- 配置数据。

板级预检脚本校验文件和哈希。

## 子模块与补丁

Mu-Silicium 使用子模块：

```toml
[firmware]
submodules = ["Common/Mu", "Silicon/Silicium", "Silicon/Qualcomm"]
patches = ["Resources/MuPatches/Gic-Spurious.patch"]
```

`patches` 中的补丁在构建期间应用到共享 edk2 树，之后还原。驱动在应用前运行 `git apply --check`。

## 构建

```sh
./unixnu build firmware --uefi /path/to/Mu-Silicium
```

驱动：

1. 运行预检脚本。
2. 初始化列出的子模块。
3. 缺少 `GenFw` 时构建 BaseTools。
4. 应用板级补丁。
5. 用 DSC、`AARCH64`、`CLANGPDB` 和板级 defines 运行 EDK II `build`。
6. 还原补丁。
7. 检查固件卷大小和路径。

输出路径来自 `[firmware] fd`：

```toml
fd = "Build/<device>Pkg/{target}_CLANGPDB/FV/SILICIUM_UEFI.fd"
```

## 外部固件构建

通过 `./unixnu bootimg --fd <file>` 传入的固件需要与所选 `[firmware]` 配置一致的
DSC/FDF 模块、package 路径、板级 define 和 EDK II 补丁。检查[必需的集成](#required-integration)，
并在打包镜像时使用匹配的板级配置。

## 启动镜像集成

`unixnu bootimg` 用固件基址和大小编译 BootShim：

```sh
clang --target=aarch64-none-elf -c \
  -DFD_BASE=<base> -DFD_SIZE=<size> \
  -DREQUIRES_KERNEL_HEADER=<0 or 1> \
  BootShim/BootShim.S -o shim.o
```

它追加固件卷，用 gzip 压缩，追加设备树，再打包 Android 启动镜像。

## 验证

| 检查 | 方法 |
| --- | --- |
| 固件卷大小 | 驱动与 `[uefi_fd] size` 比较 |
| shim header | 检查 `ARM\x64` 及基址和大小字段 |
| 启动镜像部分 | 解包并逐部分比较 |
| 菜单 | 串口出现 `UNIXNU:` 行 |
| 负载 | 菜单列出 `xnu` 项，DarwinBoot 打印交接信息 |

## 添加 UEFI 驱动

驱动可以放在固件卷或负载中。

| 位置 | 构建 | 加载 |
| --- | --- | --- |
| 固件卷 | 把 INF 加入 DSC 和 FDF | 固件 dispatch，或 UniXNUDxe 启动应用 |
| 负载 | 构建独立 `.efi` | `unixnu.toml` 的 `[[driver]]` 或 kit |

INF、入口和注入细节见 [UEFI 驱动](/zh/drivers/uefi-drivers)。

## 下一步

- [设备树](/zh/porting/device-tree)
- [bring-up 顺序](/zh/porting/bring-up)
- [UEFI 驱动](/zh/drivers/uefi-drivers)
