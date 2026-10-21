# 文档站

文档是 `docs/` 下的 VitePress 站点，发布到 `https://unixnu.com`。

## 环境

| 工具 | 版本 |
| --- | --- |
| Node.js | 22 或更新 |
| npm | 10 或更新 |

## 本地开发

```sh
cd docs
npm install
npm run dev
```

VitePress 会打印本地地址。`npm run build` 把静态站点写到 `docs/.vitepress/dist`，`npm run preview` 提供构建结果。

## 结构

```
docs/
  .vitepress/
    config.mts          站点配置
    theme/              自定义 CSS
  public/
    CNAME               自定义域名
    logo-light.svg
    logo-dark.svg
  guide/                入门与构建
  concepts/             启动链、负载、预链接、userdata、安全
  porting/              设备移植
  drivers/              UEFI、XNU 和 kext 驱动
  xnu/                  源码、补丁、页表、启动参数
  devices/              设备页面和示例
  reference/            命令行、配置、输出、QEMU、术语
  contributing/         本节
  zh/                   简体中文
```

## 新增页面

1. 在对应章节创建 Markdown 文件。
2. 在 `docs/.vitepress/config.mts` 的 sidebar 中加入页面。
3. 在 `docs/zh/` 下创建中文页面，并加入中文 sidebar。
4. 运行 `npm run build`，修复坏链。
5. 新章节需要加入语言切换配置。

## 语言版本

| 语言 | 路径 | 语言代码 |
| --- | --- | --- |
| 英文 | `/` | `en-US` |
| 简体中文 | `/zh/` | `zh-CN` |

两个版本包含相同页面。修改一个页面时，在同一个 pull request 中更新另一个版本。

## 写作规则

- 使用标准术语。
- 直接陈述当前行为。
- 不使用长破折号和短破折号。
- 不使用比喻。
- 标题使用中性名词。
- 一个页面只讲一个主题。
- 参考内容用表格，操作步骤用列表。
- 设备相关数值放在设备页面。
- 每个操作步骤给出具体命令。

## 链接检查

```sh
cd docs
npm run build
```

VitePress 在内部链接断开时构建失败。

## 下一步

- [仓库布局](/zh/contributing/repository)
- [总览](/zh/guide/overview)
