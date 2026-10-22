# 小米 Poco F6 / Redmi Turbo 3（peridot）

peridot 是搭载 SM8635 的小米 Poco F6 和 Redmi Turbo 3。下面的移植是独立的社区项目，UniXNU 组织不维护它。内核和根文件系统来自 DarwinXNU peridot 工作，启动链是 Mu-Silicium UEFI 固件加内嵌 XNU 加载器。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [DarwinXNU](https://github.com/hoshikv/xnu-darwin-peridot) | [hoshikv](https://github.com/hoshikv) | 已在真机到达 iOS 16.7.16 用户态 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| UEFI 固件和 boot shim | 工作，`fastboot boot` 加载镜像后加载器完成交接 |
| 负载块 | `XNUKERN1`、`XNUFDT01` 和 `XNUROOT1` 尾部块被校验和读取 |
| XNU 和 iOS 用户态 | 内核启动、挂载 UFS 根，并在屏幕上到达 iOS 16.7.16 锁屏和主屏幕 |
| 显示 | AppleCLCD 控制台在 1220x2712 面板上，以 1125x2436 呈现 |
| UFS 和根 | userdata `ufsroot0` 设备以读写方式挂载，launchd 运行 |
| 触摸和按键 | 从 ios-sweet 移植；当前镜像未启用 |
| GPU | 无加速器，帧缓冲通过空的 `IOAcceleratorES` 呈现 |

镜像只用 `fastboot boot` 启动。它是临时启动，不修改 Android 和任何分区。

## 取值

| 项 | 取值 |
| --- | --- |
| 板级 | Poco F6 / Redmi Turbo 3，SM8635，代号 peridot |
| SoC | 高通骁龙 8s Gen 3（SM8635） |
| IPSW | iPhone X（D22AP / iPhone10,3），iOS 16.7.16（`20H392`） |
| 内核源码 | xnu-8796.141.3，macOS 13.5，`MACHINE_CONFIG=PERIDOT` |
| 固件 | Mu-Silicium peridot，`FD_BASE=0xA7100000`，`FD_SIZE=0x300000` |
| 负载 | `XNUKERN1`（内核 Mach-O）、`XNUFDT01`（ADT）、`XNUROOT1`（根镜像） |
| ADT | `tools/mkadt.py`；合成 ECID `PERIDOT`；chip-id `0x8015` |
| 根 | iPhone X 16.7.16 根镜像（`ufsroot0`，读写） |
| 启动参数 | `serial=3 cpus=8 rd=ufsroot0 ufsrw=1 rootrw=1 peridotfb_hz=30 peridotfb_default=1080` 以及 peridot 驱动标志 |

## 构建

构建需要将 DarwinXNU 补丁应用到 xnu-8796.141.3、一个 Mu-Silicium peridot 树，以及一个 iOS 16.7.16 iPhone X 根镜像。内核在 macOS CI 上构建（`MACHINE_CONFIG=PERIDOT`）。镜像端到端复现：

```sh
tools/build-image.sh \
  --mu /path/to/mu \
  --kernel kernel.development.peridot \
  --root /path/to/ios16-root-peridot.img
```

启动：

```sh
fastboot boot Mu-peridot.img
```

内核、ADT 和根镜像是外部输入，不存放在仓库中。

## 启动链

```
ABL -> fastboot boot Mu-peridot.img
        img = [BootShim.bin][SILICIUM_UEFI.fd][pad]XNUKERN1|size|kernel Mach-O[pad]XNUFDT01|size|ADT[pad]XNUROOT1|size|root
    -> BootShim 将 FD 复制到 FD_BASE 并存储尾部地址。
    -> Mu UEFI 启动内嵌 XnuLoader，校验尾部块并填充 boot_args。
    -> XnuLoader ExitBootServices 并跳转到内核入口。
```

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
