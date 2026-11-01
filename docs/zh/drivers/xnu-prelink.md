# XnuPrelink

代码匹配会识别编译器插入的完整 PAC 失败检查序列，输出内核仍保留这些检查。
两个生成入口都会核对匹配代码的签名，再复用已有映射。
`--fileset-reference FILE` 可以提供带符号的对照内核。唯一的代码匹配可提供符号名，
最终地址仍从实际编译的原生内核获取。映射记录中会保存对照文件的哈希。

sheng 的 iPadOS 27 构建在预链接前运行
`build-fileset-release-reference.py --tree . --lto`。该对照内核需要启用
LTO；非 LTO 对照会丢失原生 kext 所需的匹配，包括 corecrypto 启动时对
`kprintf` 的调用。启用 `--allow-missing` 时，打包可以成功，但该调用会在
运行时进入 `unixnu_fileset_unmapped` 并触发 panic。

对照内核构建脚本记录模式、源码、SDK、归档库、编译器和版本输入，复用前还
会核对输出哈希。没有记录的旧产物会重建；输入改变时使用独立构建目录。
LTO 模式从生成的 LTO 对象和非 LTO 文件列表检查导出符号。对照内核改变后，
需要重新生成映射、内核、payload 和 boot 镜像，并在上机前检查未解析目标报告。

24A446 的符号记录保留了从旧 RELEASE-LTO 映射恢复、并与对应启动镜像交叉
核对的 23 个导入函数身份，以及此次定位的 corecrypto `kprintf` 导入。
记录包含原始函数字节哈希和恢复依据；当前原生内核的目标地址仍按符号重新解析。

固定记录还按 `vdesc_name` 识别 13 个此前缺失的 vnode 操作描述符，按链式
指针目标识别 4 个 metaclass 指针槽，并通过源码调用方识别 `gIODTPHandleKey`
和 `audio_active`。APFS 注册时会读取这些描述符的操作下标；保留旧地址可能
把 zone 数据当成下标，导致 `vfs_fsadd` 越界。必须绑定到由新内核 VFS 初始化
的描述符。

对于 arm64e fileset 内核集合，`emit_prelink.py` 会选择 fileset 路径并生成
函数和数据映射。`--fileset-map FILE` 可以指定已有映射，输入哈希和匹配器版本
必须一致。输出保留所选根组件及其全部依赖。

输出工具把原生内核各段放进集合的代码、常量和数据范围，按原生链接器的分段
重定位记录改写地址，重建链式修正表和函数起点，并重新计算 corecrypto 的代码
HMAC。集合根头使用原生内核的链接地址，普通预链接的 `--slide` 不用于 fileset。
原生内核输入文件保持不变。

原生适配器通过 `BTI c; B` 跳板调用保留的 kext 函数，固定目标由 `N_ABS`
符号 `<stub>.original` 声明。这类跳转没有链接器分段重定位记录，因此输出工具
在布局完成后重新计算跳转，并核验目标位于保留组件的可执行范围内。报告中的
`native_original_branches` 记录每条绑定。构建脚本不得预先减去缓存的原生内核
位移；GOT 中的绝对数据指针保持固定值。

默认遇到缺失映射就停止。`--allow-missing` 可以生成实验映像，JSON 报告按
kext 列出所有未解析目标。结构验证通过后，仍需要补全映射并进行硬件验证，
才能确认启动兼容性。

`unixnu kernel --skip-prelink` 将原生可执行文件保存为 `kernel.macho`。
`unixnu prelink --skip-prelink` 可以使用已有构建。此模式不会加入原版 kext，
输出旁的记录标明 `native-only`。

先按[适配流程](/zh/porting/platform)准备板级输入、修改源码、接入构建并逐步验证。

内核预链接生成器与 ABI 工具。

[源码仓库](https://github.com/UniXNU/XnuPrelink).

XnuPrelink 将构建的 XNU 内核绑定到所选原始 kext，并写出预链接方案。OS 配置提供 kernelcache 固定版本、根组件、slide 和 ABI 设置。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build prelink -D ../UniXNU-sheng
```

[组件目录](/zh/reference/components)

24A446 打包配置还会按原始、未滑动的导入地址检查回归清单。新增未解析数据或
stub 调用会在替换上次内核产物前报错。完整重编曾丢失两个依赖顺序的匹配：
`IOCircularDataQueueCopyLatest` 和 `get_aiotask`；现在已根据源码和反汇编，
用原函数摘要及 native 符号固定其身份。
