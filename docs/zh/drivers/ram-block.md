# RamBlock

先按[适配流程](/zh/porting/platform)准备板级输入、修改源码、接入构建并逐步验证。

稀疏 RAM 块存储，以及可选的持久存储回调。

[源码仓库](https://github.com/UniXNU/RamBlock).

RamBlock 将 Data 镜像发布为块设备。持久存储接口使用 native_ufs_store 回调，板级提供存储与重置策略。

## 直接模式

持久存储以读写方式打开时，修改过的页只保存在存储窗口中，其余页由 seed 提供。
请求并发执行：读取不加锁，同一页的写入不会重叠，flush 会等待进行中的写入完成，
因此介质上的每个位图位都指向已落盘的页。存储提供缓存写入时以回写方式运行
（`data-fua=1` 改为直写）；自上次 flush 以来没有写入时，synchronize 不发送命令。

## 集成

组件目录记录实现范围、硬件与 OS 要求、板级依赖、源码版本、构建阶段、输出和运行时标识符。所选配置按依赖顺序运行构建命令。

```sh
./unixnu build kernel -D /path/to/device
```

[组件目录](/zh/reference/components)
