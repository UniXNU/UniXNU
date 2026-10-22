# 小米平板 7 / POCO Pad X1（uke）

uke 是搭载 SM7675 的小米平板 7 和 POCO Pad X1。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-uke](https://github.com/Allenwdk/UniXNU-uke) | [Allenwdk](https://github.com/Allenwdk) | 设备仓库，根已挂载，launchd 启动；显示待完成 |
| [uefi-uke](https://github.com/Allenwdk/uefi-uke) | [Allenwdk](https://github.com/Allenwdk) | Mu-Silicium UEFI 移植 |

## 状态

原厂 ABL 已到阶段 1 到 5：UEFI 固件、UniXNU 菜单、负载、DarwinBoot 和 XNU 入口。绿色条表示内核入口代码已执行。真机上 UFS 根已挂载，launchd 启动。屏幕停在 Apple 标志，因为 IOMFB 找不到默认 framebuffer surface。

阶段 6 的完整内核用 `uke-full_defconfig` 编译并预链接。UFS 块类绑定到固定的原始候选。真机上根卷已挂载，launchd 已运行；显示和 GPU 仍是阻塞点。

| 区域 | 状态 |
| --- | --- |
| UEFI 固件 | 工作 |
| UniXNU 菜单 | 工作 |
| 负载和 DarwinBoot | 工作 |
| XNU 入口 | 工作，绿色条 |
| 根设备 | 已挂载，launchd 启动 |
| 显示 | Apple 标志，无默认 framebuffer surface |
| watchdog | 部分生效，watchdogd 仍触发 SIGTRAP |
| 触控 | 仅探针，固件对象为空 |
| GPU | 已记录 Adreno 732 数值，驱动待完成 |
| USB、音频、Wi-Fi、传感器 | 不在当前阶段 |

## 构建

Linux 上构建固件和启动镜像：

```sh
cd /path/to/UniXNU
./unixnu defconfig uke_defconfig -D ../UniXNU-uke
./unixnu fetch -D ../UniXNU-uke
./unixnu build firmware --skip-preflight -D ../UniXNU-uke --uefi ../uefi-uke -j 8
./unixnu bootimg -D ../UniXNU-uke --uefi ../uefi-uke --dtb ../uke-port/data/vendor_boot.dtb --ramdisk none
```

内核在仓库的 GitHub Actions 中构建：

```sh
gh workflow run build-uke-kernel
```

userdata 镜像需要 macOS `hdiutil`。当前阶段、产物和剩余工作见设备仓库的 `docs/PROGRESS.md`。

## 维护

表中的维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
