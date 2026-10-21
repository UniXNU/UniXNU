# 仓库布局

基础仓库和每个设备仓库使用相同布局。

```
UniXNU/
  unixnu                  入口
  scripts/unixnu/         构建驱动
  package/                UniXNU EDK II package
  drivers/                内置 XNU 驱动
  kits/                   内核库
  patches/                XNU、libpthread、Mesa 补丁
  scripts/                构建和校验脚本
  docs/                   本文档站
  assets/                 标志
  feeds.toml              固定的外部源码
  .gitmodules             模块子模块
  examples/device/        示例设备仓库
```

驱动和 kit 是 UniXNU 组织下的独立公开仓库，以子模块形式引入。克隆时使用 `--recurse-submodules`，或运行 `git submodule update --init --recursive`。

## 模块类型

| 类型 | 目录 | 内容 |
| --- | --- | --- |
| driver | `drivers/<Name>` | XNU 驱动源码和参考 plist |
| kit | `kits/<Name>` | 内核库 |
| patch | `patches/<Name>` | 补丁集 |
| script | `scripts/` | 构建和校验脚本 |
| package | `package/` | UniXNU package |
| refer | 拉取的树 | Apple 源码或 edk2 |

设备仓库可以提供任意类型，同名模块覆盖基础模块。

## 解析顺序

1. `--local-module [KIND:]NAME=PATH`
2. `--local-<kind> DIR`
3. `--local DIR`
4. `feeds.toml` 的 `local` 键或 `local.toml`
5. 设备仓库
6. 基础仓库，包括其模块子模块
7. `feeds.toml` 的 git 源码

## 构建树

`unixnu tree` 写 `out/<board>/tree`：

```
tree/
  drivers/  kits/  patches/  refer/
  scripts/  package/
  build/    .cache/
```

符号链接指向选中的模块，脚本被复制，设备 `package/` 出现在 `kits/<board.kit>`。

## 脚本

构建脚本从自身路径定位构建树。`scripts/` 中的脚本可以读取 `ROOT`、`build/`、`.cache/`、`refer/`、`drivers/`、`kits/`、`patches/` 和 `package/`。

## 新增模块

组织中的每个仓库都带有 `unixnu` topic。

1. 在 UniXNU 组织下创建公开仓库。
2. 在仓库设置中添加 `unixnu` topic。
3. 把它作为子模块加入 `drivers/` 或 `kits/`。
4. 从板级文件或内核脚本引用。
5. 在对应文档章节记录。

设备适配完成后，把设备页面和移植记录贡献到本仓库。

## 提交范围

一个提交只改一个主题：

| 前缀 | 主题 |
| --- | --- |
| `feat(<area>)` | 新能力 |
| `fix(<area>)` | 缺陷修复 |
| `docs` | 文档 |
| `build(<area>)` | 构建系统 |
| `chore` | 清理 |

提交信息描述变化，文档描述当前状态。

## 下一步

- [设备仓库](/zh/porting/device-repository)
- [文档站](/zh/contributing/documentation)
- [构建](/zh/building)
