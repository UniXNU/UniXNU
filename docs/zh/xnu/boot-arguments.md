# 启动参数

## 应用启动参数 {#apply-arguments}

有效命令行依次合并板级配置的 `[payload] kernel_args`、`unixnu.local.toml` 的 `[build] kernel_args` 和 `--kernel-arg`。后面的来源覆盖同名参数。负载构建器将结果写入 `EFI/UniXNU/unixnu.toml` 中 XNU 启动项的 `args`。UniXNU 将选中的启动项交给 DarwinBoot，DarwinBoot 在启动时将命令行复制到 XNU 的 `boot_args.CommandLine`。内核配置开关由 `./unixnu kernel` 编译。

保存[本地构建参数](/zh/reference/configuration#local-build-inputs)后运行：

```sh
./unixnu payload --kernel-arg serial=3 --kernel-arg debug=0x14e
./unixnu bootimg
jq -r .kernel_args out/<device>/<os_profile>/<config>/payload/payload.json
mtype -i out/<device>/<os_profile>/<config>/payload/payload.img ::/EFI/UniXNU/unixnu.toml
```

启动新生成的 `boot/boot.img`。`bootimg` 将当前负载复制进该文件，打包后修改负载需要再次运行 `bootimg`。指定 `--ramdisk FILE` 时使用该文件中的配置。检查选中的 XNU 启动项及追加的 `confirm_args`。多个卷包含 `unixnu.toml` 时，先检查启动管理器所在卷的配置。

负载命令输出 `kernel args:`，DarwinBoot 在交接前输出 `DARWINBOOT: command line:`。两者不同时检查所选卷和启动项；两者相同但行为未变时，检查内核或所选驱动是否实现该参数。绿色交接条的检查步骤见[早期启动诊断](/zh/guide/debugging#green-bar)。

## 格式

参数匹配：

```
[A-Za-z0-9_.-]+(=[A-Za-z0-9_.,-]+)?
```

合并后的行最多 1000 字节。DarwinBoot 把它复制到 1024 字节缓冲区。

```sh
./unixnu build payload --kernel-arg serial=3 --kernel-arg debug=0x14e
```

## 常用参数

| 参数 | 用途 |
| --- | --- |
| `-v` | 详细内核输出 |
| `serial=3` | 选择串口控制台 |
| `debug=0x14e` | 调试输出掩码 |
| `kextlog=0xfff` | kext 详细日志 |
| `-apfs_shared_datavolume` | 使用 APFS 共享 Data 卷 |
| `-no_slto_panic` | 关闭 SLTO panic |
| `kt_fixed_zones=<n>` | 固定 kernel trace zone 数量 |
| `boot-progress=<n>` | 选择启动进度显示级别 |
| `cs_debug=<mask>` | 代码签名调试输出 |
| `amfi_get_out_of_my_way=1` | 关闭 AMFI 强制执行 |
| `pmap_debug=<mask>` | pmap 调试输出 |
| `zlog=<name>` | 选择 zone 日志 |

`amfi_get_out_of_my_way=1` 只用于诊断启动，它会改变安全策略。

## 平台参数

| 参数 | 用途 |
| --- | --- |
| `sheng-platform-stage=<n>` | 在平台专家固定阶段停住 |
| `sheng-pmgr=<n>` | 选择板级 PMGR 集成 |
| `native-ufs-root=1` | 使用原生 UFS 根路径 |
| `native-ufs-stats-delay=<n>` | 延迟 UFS 统计读取 |
| `armcpu-diagnostics=1` | 打印 CPU 和中断状态 |
| `armcpu-spi-ipi=1` | 使用 SPI 路径发送核间中断 |
| `sheng-smp=1` | 启动 secondary CPU |
| `sheng-cpufreq=<n>` | 选择 CPU 频率路径 |
| `sheng-touch=<n>` | 运行触控探针阶段 |
| `sheng-touch-hz=<n>` | 选择触控 SPI 时钟 |
| `sheng-touch-mode=<n>` | 强制触控 SPI 模式 |
| `sheng-touch-hid=1` | 把触控点发布到 HID |
| `sheng-aks=1` | 启用 AKS 路径 |
| `sheng-aks-sls=<n>` | 选择上报的锁定状态；3 表示无密码 |
| `sheng-usb=<n>` | 运行 QcomDwc3；2 增加寄存器采样，3 另外让总线断开重连一次 |
| `sheng-usb-host=<s>` | 延时后强制进入 USB 主机模式 |
| `sheng-usb-back=<s>` | 强制主机模式持续该时间后，回到线缆决定的角色 |
| `sheng-gpu-power=<n>` | 选择 GPU 电源序列 |
| `sheng-gpu-metal=1` | 启用 Metal 路径 |
| `sheng-gpu-addon=1` | 挂载 GPU addon 内容 |
| `sheng-data-persist=<n>` | 1 只验证 Data store 窗口，2 打开写窗口 |
| `sheng-data-reset=<n>` | 1 丢弃 Data overlay，2 同时要求 Setup |
| `sheng-log-reserve=<mib>` | userdata 末尾为诊断日志和导出区保留的空间，默认 1024 |
| `sheng-data-fua=1` | Data store 改为直写（每次写入带 FUA），不使用回写 |
| `sheng-ufs-bench=1` | 在启动继续之前运行 UFS 读取基准，结果写入日志，然后重启回 fastboot |
| `sheng-disable-watchdogd=1` | 停止 watchdog daemon |
| `sheng-disable-jobs=<list>` | 跳过指定 launch job |
| `offline-legacy-*=1` | 启用 legacy 显示和输入探针 |
| `offline-owner-root-check=1` | 启动 verified root 检查 |
| `offline-owner-root-audit=1` | 启用根绑定审计 |
| `offline-apfs-load=1` | 在离线检查点加载 APFS |
| `offline-mobile-graphics-*=1` | 启用 mobile graphics 探针 |
| `boot-ui-focus=<name>` | 选择启动 UI trace 的进程 |

上表包含板级参数。设备使用的集合以设备页面和板级文件为准。

## 新增参数

1. 把默认值加入 `[payload] kernel_args`。
2. 用 `--kernel-arg` 加入一次性取值。
3. 内核中用 `PE_parse_boot_argn` 读取：

```c
unsigned stage = 0;
if (PE_parse_boot_argn("my-driver-stage", &stage, sizeof(stage))) {
  ...
}
```

4. 在设备页面记录该参数。

## 调试

| 需求 | 参数 |
| --- | --- |
| 早期内核输出 | `-v serial=3 debug=0x14e` |
| kext 加载细节 | `kextlog=0xfff` |
| 启动进度 | `boot-progress=2` |
| 平台停点 | `sheng-platform-stage=<n>` |
| 存储细节 | `native-ufs-root=1 native-ufs-stats-delay=30` |
| 显示细节 | `offline-legacy-gop=1 offline-legacy-phase=<n>` |
| 代码签名细节 | `cs_debug=<mask>` |

panic 日志记录最后的内核输出。设置 `XNU_DT_PANIC_REGION` 时，内嵌 panic 区域从设备树读取。

## 下一步

- [故障排查](/zh/reference/troubleshooting)
- [启动镜像](/zh/guide/boot)
- [调试与日志](/zh/guide/debugging)
- [设备](/zh/devices/)
