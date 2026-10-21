# OnePlus 7 Pro（guacamole）

guacamole 是搭载 SM8150 的一加 7 Pro（GM1910）。下面的移植是独立的社区项目，UniXNU 组织不维护它。内核和根文件系统来自 ios-sweet 的 guacamole 工作，UniXNU 和 DarwinBoot 提供启动链。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-guacamole](https://github.com/wochgn/UniXNU-guacamole) | [wochgn](https://github.com/wochgn) | 已在真机到达 iOS 16.7.16 用户态 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| UEFI 固件和 UniXNU 菜单 | 工作，菜单显示 `OnePlus 7 Pro - XNU` |
| 负载卷 | 64 MiB 的 `GUACESP` FAT32 卷可挂载和读取 |
| DarwinBoot | 校验 `kernel.macho` 和 `.adt` 并交接 |
| XNU 和 iOS 用户态 | r15 在屏幕上到达 iOS 用户态 |
| GPU 和 GMU | 在 ios-sweet 树中受阻 |

r15 镜像请求 3 GiB Darwin 窗口并到达 iOS 用户态。`fastboot boot` 是临时启动，不修改 Android 和任何分区。

## 构建

构建需要 ios-sweet 的内核和 ADT，`b6ae99c` 的 UniXNU 检出，以及 `0b798128` 的 Project Aloha 检出。应用仓库列出的三个补丁，然后运行：

```sh
python3 scripts/build-firmware.py
python3 scripts/build-payload.py
python3 scripts/build-bootimg.py \
  --fd uefi/Build/SurfaceDuo1Pkg/DEBUG_CLANGPDB/FV/SM8150_EFI.fd \
  --dtb inputs/uefi-prebuilt/guacamole.dtb \
  -o out/guacamole/boot/boot-32-r15.img
```

启动：

```sh
fastboot boot out/guacamole/boot/boot-32-r15.img
```

内核、ADT、DTB 和固件卷是外部输入，不存放在仓库中。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
