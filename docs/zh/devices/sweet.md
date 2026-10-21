# Redmi Note 10 Pro（sweet）

sweet 是搭载 SM7150、Snapdragon 732G 和 Adreno 618 的 Redmi Note 10 Pro。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-sweet](https://github.com/dipa-studio/UniXNU-sweet) | [dipa-studio](https://github.com/dipa-studio) | 平台和加载器 bring-up |

## 状态

移植包含 Sweet ADT、ArmCpu override、DarwinBoot override 和 A618 legacy HFI 传输。主机检查和 EFI 加载器检查通过。还没有可启动的 sweet 镜像，也没有加速桌面。现有手机分区未改动。

## 构建

主机检查：

```sh
python3 scripts/check-host.py
python3 scripts/make-sweet-adt.py --output out/sweet.adt
```

设备仓库集成：

```sh
python3 ../UniXNU/unixnu defconfig sweet_defconfig -D . --out out/driver
python3 ../UniXNU/unixnu status -D . --out out/driver
```

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
