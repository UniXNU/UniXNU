# 文档站

文档是 `docs/` 下的 VitePress 站点，发布到 `https://unixnu.com`。

## 操作步骤 {#procedure}

1. 确定所属页面及其中英文版本；设备结果更新设备的[结构化记录](#设备记录)。
2. 编辑当前操作步骤或参考内容。操作应写明前置输入、工作目录、有序命令、预期结果和下一步。
3. 从对应流程链接到该页，新增页面按[新增页面](#新增页面)设置导航和语言版本。
4. 在主仓库运行 `npm --prefix docs run build`，解决构建错误，再从[移植设备](/zh/porting/steps)和[技术参考](/zh/reference/)沿正文链接进入两个语言版本。
5. 按[本地开发](#本地开发)预览页面，检查命令块和下一步链接，再发布文档提交。

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

格式 2 设备页按[记录发布](/zh/porting/records#publishing-and-reuse)生成。手写指南使用以下步骤。

1. 在对应章节创建 Markdown 文件。
2. 在 `docs/.vitepress/config.mts` 的 sidebar 中加入页面。
3. 在 `docs/zh/` 下创建中文页面，并加入中文 sidebar。
4. 从[移植设备](/zh/porting/steps)可达的相关指南或主题索引中加入正文链接。在页面正文中链接任务前置步骤和下一步。
5. 在两个语言版本中从起始页沿正文链接检查新页面是否可达。
6. 运行 `npm run build`，修复坏链。
7. 新章节需要加入语言切换配置。

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
- 操作页按执行顺序编号，写明输入、工作目录、命令、预期结果和下一步；参考页链接到对应操作。

## 链接检查

```sh
cd docs
npm run build
```

VitePress 在内部链接断开时构建失败。

## 下一步

- [仓库布局](/zh/contributing/repository)
- [移植设备](/zh/porting/steps)

## 设备记录

站点构建需要 Python 3.11 或更新版本。`npm run build` 渲染已提交的目录和记录快照。
每天两次的目录工作流发现源码、固定版本并更新格式 2 设备页、索引和导航。
更新设备记录时修改并发布设备仓库的 `porting.toml`，中英文页面使用同一份记录。
已有旧格式页面保留原文，新收录的旧格式条目只包含仓库链接。
详见[记录指南](/zh/porting/records#publishing-and-reuse)。

## 驱动指南

按硬件输入、接口实现、OS 接入、构建和验证组织步骤。链接已核对版本的真实源码文件，
写明关键符号、调用顺序、数据所有权和错误处理。板级源码作为参考，设备状态写入设备记录。
每个步骤说明需要修改什么和如何观察结果，英文与中文使用相同源码引用。

移植页面的适配步骤只链接其他移植页面。`drivers/` 下的组件页面属于参考内容，
从[技术参考](/zh/reference/)进入。
