# QEMU virt

QEMU 目标在 AArch64 `virt` 机器上运行 UniXNU，用于在没有平板时做 bring-up。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-qemu](https://github.com/xVanTuring/UniXNU-qemu) | [xVanTuring](https://github.com/xVanTuring) | iPadOS 17 主屏幕和 Settings；使用 `--metal` 时在 Mac GPU 上运行 Metal |

## 状态

| 阶段 | 状态 |
| --- | --- |
| UniXNU 菜单、配置、作为驱动的 DarwinBoot | 工作 |
| DarwinBoot 交接、4 GiB 窗口、内核入口、MMU 和 4 KiB 页表 | 工作 |
| 平台专家和 IOKit | 工作 |
| verified VirtIO 根 | 工作，owner 签名的根已挂载 |
| AMFI 和原始 launchd | 使用原始 trust cache 启动 |
| SystemOS union 和 dyld shared cache | 工作 |
| Data ramdisk | 工作 |
| 显示 | ramfb 上的 NativeLegacyDisplay；不带 `--metal` 时 CPU 渲染，带 `--metal` 时由 Mac GPU 合成 |
| 触控和 Home | 工作，键盘输入尚未工作 |
| GPU | QemuMetal 设备；`--metal` 让 render server 的 Metal 工作跑在 Mac GPU 上。不带该选项时没有 Metal 设备，QuartzCore 使用 CPU 渲染 |
| Settings | 不带 `--metal` 时为白屏；带上后可以打开并列出全部项目，部分行图标缺失 |

`--metal` 需要 `scripts/build-qemu-metal.py` 生成的插件、owner trust cache 和 Data 种子。仓库 README 记录了构建 ESP 和启动 QEMU 的命令。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
