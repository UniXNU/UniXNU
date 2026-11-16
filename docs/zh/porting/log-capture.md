# 抓取日志与自动启动测试

按移植进度建立日志抓取流程：先获取固件日志，再记录内核交接，随后实现持久化日志和自动重启测试。
使用[启动检查点](/zh/porting/bring-up)确定当前验证的阶段。

| 阶段 | 所需支持 | 保存结果 |
| --- | --- | --- |
| UEFI 菜单 | GOP 显示、菜单输入、Advanced Logger 和二维码插件 | 扫描屏幕导出的固件 `.log` 文件 |
| XNU 入口 | UART 或屏幕诊断 | 串口日志或最后检查点/panic 的照片 |
| 存储 | 预留日志区域、内核写入器和 Linux 或 recovery 读取器 | 内核消息缓冲和诊断快照 |
| 重复测试 | 可用的日志读取与返回 bootloader 功能 | 每次启动独立的证据目录 |

## 1. 集成固件日志导出器 {#firmware-setup}

按 [UEFI 集成](/zh/porting/uefi-firmware)准备固件仓库。
通用导出器位于 UniXNU 的
`package/UniXNUPkg/Driver/AdvancedLogDxe/AdvancedLogDxe.inf`。
它在 UEFI boot services 可用时读取 Advanced Logger 内存缓冲。

1. 在固件 DSC 的 `[Components]` 中加入：

   ```ini
   UniXNUPkg/Driver/AdvancedLogDxe/AdvancedLogDxe.inf
   ```

   在 FDF 的 DXE 固件卷中加入：

   ```ini
   INF UniXNUPkg/Driver/AdvancedLogDxe/AdvancedLogDxe.inf
   ```

2. 启用平台的 Advanced Logger 日志收集模块，将所需固件调试输出接入它。
   导出器在 `gAdvancedLoggerProtocolGuid` 安装后加载。
   INF 还依赖 `AdvLoggerPkg`、`MsGraphicsPkg`、`AdvancedLoggerAccessLib` 和 `QrEncoderLib`。
   从固件仓库查找当前 Mu 版本提供的库实例：

   ```sh
   find . -name '*AdvancedLogger*.inf' -o -name '*QrEncoder*.inf'
   ```

   在 DSC `[LibraryClasses]` 中映射日志访问库和二维码库，将对应包根目录加入
   `board.toml` 的 `[firmware] packages`。查不到文件时先初始化这些包所在的子模块。
   日志缓冲区和调试库映射采用该平台的 Advanced Logger 配置。
3. 在 DSC `[PcdsFixedAtBuild]` 中把 `gUniXNUPkgTokenSpaceGuid.PcdUniXNUDeviceModel`
   设置为板型的 ASCII 名称。导出文件名使用该值。
4. 在设备 `board.toml` 已有的 `[payload]` 表中加入 `tools = true`，生成的启动菜单会包含
   **Tools**。手写的 `unixnu.toml` 使用 [`action = "tools"` 菜单项](/zh/reference/boot-configuration)。
5. 从 UniXNU 主仓库运行以下命令。先选定设备，并填好[本地输入](/zh/reference/configuration#local-build-inputs)：

   ```sh
   ./unixnu firmware
   ./unixnu payload
   ./unixnu bootimg
   ```

**结果：** 镜像包含导出器；平台日志协议可用时，菜单出现 **Tools → Advanced Logger**。

## 2. 在内核交接前扫描固件日志 {#qr-logs}

准备另一台带摄像头的手机或设备，打开 [OneSend（扫传）](https://onesend.01mvp.com)。
导出器通过连续的 OneSend 二维码帧传输日志。

1. 从主仓库启动镜像：

   ```sh
   fastboot devices
   fastboot -s <serial> boot out/<device>/<os_profile>/<config>/boot/boot.img
   ```

2. 停留在 UniXNU 菜单，选择 **Tools**，再选择 **Advanced Logger**。
   插件打开时读取一份当前固件日志快照。加载器报错并返回菜单时，在复位前打开插件抓取该错误。
3. 打开扫传的接收扫描功能，允许使用摄像头，将完整二维码置于画面内。
   保持扫描轮播帧，直到接收端完成传输。
4. **下键 / j** 降低轮播速度，**上键 / k** 提高速度。默认每秒一帧，五档间隔从 5 秒到
   250 毫秒。音量键映射为上下键的板型可使用音量键。按 **Enter** 或 **Escape** 返回菜单；
   电源键映射为 Enter 时也可用于返回。
5. 保存收到的 `<model>-<date>-<time>.log`，附上镜像版本和最后完成的检查点。
   文件名使用固件时钟。重新构建前，先查看文件中失败操作的输出。

**结果：** 在菜单可操作时获得可读的固件日志。`ExitBootServices` 之后的 XNU 执行使用步骤 3 的抓取方式。

| 现象 | 操作 |
| --- | --- |
| 没有 Tools | 检查 `[payload] tools`，重建 payload 和启动镜像 |
| 没有 Advanced Logger | 检查 DSC/FDF 中的 INF、依赖和平台日志协议 |
| 显示 `Advanced Logger: no log` | 检查日志收集模块、调试输出接入和缓冲区配置 |
| 扫描进度停止 | 降低轮播速度，继续扫描循环播放的帧 |
| 固件在菜单前停止 | 抓取平台 UART，或拍摄最后可见输出 |

## 3. 记录内核交接 {#kernel-logs}

1. 保存步骤 2 的固件日志，再选择内核启动项。
2. 按[调试步骤](/zh/guide/debugging#procedure)抓取板型 UART 或屏幕输出。
   停在绿色交接条时，按[入口探针步骤](/zh/guide/debugging#green-bar)操作。
3. 拍摄完整 panic 屏幕或检查点，保留寄存器和最后几行文字。记录构建后 payload 中的内核参数。
4. 修改参数后，重新运行 `./unixnu payload` 和 `./unixnu bootimg`。
   重复同一启动操作，对比最后确认的检查点。

**结果：** 存储适配期间也能保留内核阶段的证据。完成[存储验证](/zh/porting/ufs)后继续实现持久化抓取。

## 4. 选择持久化日志读取器 {#persistent-logs}

持久化读取器在测试内核交还控制权后读取预留日志区域。实现读取器前，先确定区域、文件头、启动 ID、完成标记和快照格式。写入器、读取器和解码器使用相同的块单位和字节范围。

1. 在目标存储布局中预留日志区域。记录分区、偏移、大小和块单位，并与根卷和 Data 区域一起核对。镜像构建器、分区提供者、写入器和读取器使用相同边界。
2. 将内核写入器接入存储驱动限定范围的读、写和同步操作。保存内核消息缓冲、诊断快照、启动 ID 和写入状态。区域打开后再启动写入器。
3. 根据设备可启动的环境选择读取器：

   **Linux 读取器。** 使用目标内核、DTB、存储驱动、USB device controller 和 CDC ACM 支持构建精简 Linux 镜像。将区域复制到 RAM，提供串口 shell，源分区保持只读。

   **Recovery 读取器。** 启动具有 root、块设备访问和 ADB 的兼容 recovery 镜像，在 recovery 中读取区域。类似 TWRP 的 recovery 提供读取器运行环境，主机负责传输结果。

   ```sh
   adb reboot recovery
   adb wait-for-device
   adb shell id
   adb shell ls -l /dev/block/by-name
   adb shell mkdir -p /tmp/unixnu-log
   adb shell dd if=/dev/block/by-name/<log-partition> \\
     of=/tmp/unixnu-log/log.bin bs=4M
   adb pull /tmp/unixnu-log/log.bin out/logs/log.bin
   ```

   日志区域位于 `userdata` 内部时，按设备记录中的偏移和长度使用 `dd skip=<block-offset> count=<block-count>`。recovery 保持只读挂载，记录 recovery 版本、块设备路径和命令。
4. 根据写入器文件头和快照格式适配主机解码器。自动发现无法确定唯一串口或 ADB 设备时，显式指定目标。
5. 为选定的读取器实现返回路径。使用板型的重启原因和复位接口，记录手动测试使用的 bootloader 与 recovery 命令。

[参考实现](https://github.com/UniXNU/UniXNU-sheng)提供 Linux 读取器、`userdata` 预留区域和返回 fastboot 的路径。可参考其中的 `package/BootLog.c`、`BootReset.c`、`BootResetCore.h`、`package/linux-log/` 和 `scripts/read-sheng-log.py`。其中的 PMIC 地址、watchdog 调用、存储预留和 Linux 镜像输入属于该板型的适配记录。

每轮写入应尽量少。参考实现的写入器（头部版本 5）每轮只写本轮文本槽实际使用的块，以及新内核消息写到的消息缓冲区块，在参考板型上约 7 KiB/s；panic 时整段写入消息区。用户态守护进程通过 syslog 或 os_log 记录日志，由 logd 限制存储大小，不写入无上限增长的文件：参考实现的 Wi-Fi supplicant 以 `-q -s` 运行。

**结果：** 一个读取器环境、一致的解码器格式、明确的存储范围，以及已经验证的 bootloader 或 recovery 返回路径。

参考 iOS 27 原生源码路径使用 `log=1 boot-ui-trace=1` 抓取用户态停滞时的进程栈。
源码存储归档包含 BootProcessWorker.c，由独立线程采样，避免读取用户页时的缺页等待阻塞持久化日志。
加入 boot-ui-focus3=chronod 可在 backboardd、SpringBoard 之外保留 chronod 的栈。
arm64e 采样器先去除返回地址的 PAC，再检查和编码地址；栈区域为空本身不能证明进程停止运行。

## 5. 手动完成一次抓取 {#manual-cycle}

1. 启用日志参数，构建测试 payload 和启动镜像。
2. 启动测试镜像，等待所测检查点。
3. 返回选定的读取器环境：

   ```sh
   fastboot -s <serial> boot <reader.img>
   ```

   或启动 recovery 镜像：

   ```sh
   adb reboot recovery
   adb wait-for-device
   ```
4. 运行读取器，将原始区域和解码文本保存到按启动 ID 命名的目录，确认文件头、快照和写入状态。
5. 返回设备 bootloader，在下一次测试前确认设备身份。

设备仓库提供 Linux 读取器命令；具有兼容 recovery 镜像的板型使用上面的 recovery 命令。

**结果：** 一次完整测试、可识别的证据目录和已验证的读取器返回路径。文件头缺失或属于旧启动时，检查写入器启动、区域范围和读取器命令。

## 6. 自动执行已验证的循环 {#automated-cycle}

1. 启用板型定时返回 bootloader 或 recovery 的功能。超时应覆盖已测检查点和日志同步时间。
2. 为主机执行脚本配置准确的设备身份、测试镜像、读取器或 recovery 镜像、输出目录和超时。
3. 脚本启动测试镜像，观察返回，启动选定的读取器，取回并解码日志，确认最终回到 bootloader。Recovery 读取器按手动步骤执行 `adb reboot recovery`、`adb wait-for-device` 和 `adb pull`。
4. 超时后记录失败阶段，按板型文档进入 bootloader 或 recovery。保留本次镜像和部分证据。
5. 在[适配记录](/zh/porting/records)中填写版本、参数、检查点、复位结果、读取器环境、输出目录和未解决错误。

自动脚本沿用手动循环的顺序。支持 recovery 访问的板型使用相同结构并替换为 ADB 命令。

Recovery 充电时，运行 `python3 scripts/arm-sheng-recovery-return.py --serial <serial> --seconds 7200` 启用返回 fastboot 的定时器。再次运行会更新单调时钟的截止时间。

sheng 的定时 macOS 镜像从设备仓库运行：

```sh
SERIAL=<serial> READER=<sheng-linux-log.img> OUT=<capture-directory> \
  scripts/run-sheng-unattended.sh <boot.img> 7500
```

首次安装时加入 `USERDATA=/path/to/userdata.sparse`。脚本核对 sheng 产品名与完整分区 sparse 容量，写入 userdata，再执行定时启动和日志采集。后续启动使用保留 Data 的镜像，并保持 `USERDATA` 未设置。

脚本生成以 `s` 开头的六字符 `build-tag`，并与采集文件头核对。字母前缀让 XNU 启动参数解析器按字符串读取。`cycle.json` 记录预期标签、采集匹配结果、启动确认、测试及读取器耗时、读取器退出状态和最终可响应命令的 fastboot 状态。

主机脚本在采集期间保持 Mac 唤醒。两小时会话使用 `autoreset=7200 diag=1 diag-export=6900`，Linux 读取器另有 300 秒返回定时器。每次 RAM 启动前，脚本刷新当前槽位的可启动状态和重试次数，`cycle.json` 记录最终的 fastboot 响应。

`scripts/repack-sheng-boot.py INPUT OUTPUT --partition-bytes <bytes>` 按实测启动分区容量调整 payload。使用 `--kernel-arg NAME=VALUE` 或 `--remove-arg NAME` 修改 XNU 参数。首次安装使用 `data-reset=1`，后续预编译启动保留 Data 和按构建区分的着色器 checkpoint。

`scripts/make-userdata-full.py --zstd userdata-root.img.zst <分区字节数> userdata.sparse` 将根镜像直接转换为 Android sparse 格式，并将剩余分区填充为零。磁盘需容纳压缩根镜像和 sparse 输出。

在主仓库运行 `python3 scripts/build-gpu-validation-deps.py` 构建 arm64e Vulkan 诊断依赖。在设备仓库中，使用匹配的验收工具 `files` 目录准备 RAM 启动镜像：

```sh
python3 scripts/prepare-sheng-gpu-lab.py boot.img gpu-lab.img \
  --tools <acceptance-files> --tools ../UniXNU/build/gpu-validation-deps/files \
  --plugin ../UniXNU/build/adreno-metal-plugin-macos27
```

Actions 构建可使用 `scripts/fetch-actions-artifact.py OWNER/REPOSITORY RUN_ID ARTIFACT OUTPUT --file prime-list.txt --file prime-list.json` 按 HTTP 字节范围获取指定文件。省略 `--file` 时获取产物中的文件，下载直接写入输出目录并检查 ZIP 完整性。1 MiB 以内的产物缓存在内存中，加快日志读取。使用 `--file NAME` 重新运行可续传未完成的文件，下载链接自动刷新。

已安装的根镜像所用 OS 镜像及策略保持一致时，以 `root_storage=false` 触发 `macos-lab.yml`，构建 boot、内核和 payload 产物。默认设置同时构建 userdata 镜像。

准备脚本通过 `--core <resolved-tree>` 选择构建树，读取匹配 Turnip 构建的 ICD 元数据，加入签名工具和 Shader Cache App，将代码标识追加到 owner trust bundle。使用 `--manual-session --preserve-data --autoreset 7200` 生成保留固件返回定时器的手动桌面会话。用户从“应用程序”打开 Shader Cache 并开始编译。`--shader-cache-view` 打开 App 窗口，`--graphics-view` 打开系统设置，`--graphics-comparison` 运行固定交互采集。

逻辑 FAT 容量为 256 MiB。sheng 配合支持该格式的固件，将其按 1 MiB 块独立压缩为 UEFI 流（`UNXNFAT1`）；编码后的 ramdisk 必须符合 190 MiB 板级上限。`UniXNURamDiskDxe` 使用 1 MiB 读取缓存提供逻辑 FAT。

无人值守脚本通过限时的 `fastboot getvar product` 请求确认设备就绪。启动确认超时后，脚本继续等待镜像的自动返回计时；最终状态以成功的命令响应为准。

**结果：** 每次测试都有可识别的证据目录和返回路径。继续完成其余[启动验证阶段](/zh/porting/bring-up)。
