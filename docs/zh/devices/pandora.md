# 小米 17 Pro（pandora）

pandora 是搭载 SM8850 的小米 17 Pro。下面的移植是独立的社区项目，UniXNU 组织不维护它。它在由 ios-sweet 补丁系列构建的 xnu-8796 内核上运行 iPhone X 的 iOS 16.7.16 用户态。由 `fastboot boot` 启动的小型加载器取代 UEFI 启动链。内核使用 UniXNU 的原生 4 KiB 补丁，原版 Apple kext 用 NativePrelink 预链接。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [ios-pandora](https://github.com/ShueiTsuki/ios-pandora) | [ShueiTsuki](https://github.com/ShueiTsuki) | 已在真机到达 iOS 16.7.16 锁屏，触控和按键可用 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| 启动 | `fastboot boot` 启动携带内核、ADT 和负载的加载器镜像；不修改 Android 和任何分区 |
| CPU | 8 核，4 KiB 页 |
| 存储 | 原生 UFS 驱动；根文件系统是 Android userdata 分区中的固定文件，按其 extent 读写，无需清除数据 |
| 显示 | 1220x2656 面板，使用引导程序的帧缓冲；亮度通过 DSI DCS 调节 |
| 输入 | Synaptics 触控走 GPI DMA；电源键和音量键 |
| 用户态 | iOS 16.7.16（20H392）锁屏；壁纸和小组件缺失 |
| 原版 kext | AMFI 及其依赖用 NativePrelink 预链接；QEMU 和真机运行进行中 |
| GPU、音频、相机 | 不可用 |

## 构建

内核由 GitHub Actions 工作流 `xnu.yml` 以 `machine_config=PANDORA` 构建。仓库中的脚本在 WSL 中构建 ADT 和负载，用 Android NDK 构建加载器：

```sh
python3 tools/mkprelink.py <kernel> <kernelcache> <out>
KERNEL=<out> tools/boot_ios.sh --file /data/local/tmp/iosroot.img --run <N> --rd ufsroot0
```

`tools/boot_ios.sh` 解析固定根文件的 extent，构建负载和加载器镜像，并用 `fastboot boot` 启动。内核、kernelcache、根镜像和信任缓存是外部输入，不存放在仓库中。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
