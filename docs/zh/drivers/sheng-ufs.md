# ShengUfs

先按[适配流程](/zh/porting/ufs)准备板级输入、修改源码、接入构建并逐步验证。

ShengUfs 提供 SM8550 UFS 存储路径，管理主机控制器、SMMU 映射、
命令队列和根卷读取。板级集成包含时钟资源、持久 Data 区域和日志区域。

| 字段 | 值 |
| --- | --- |
| 仓库 | [UniXNU/ShengUfs](https://github.com/UniXNU/ShengUfs) |
| 硬件 | SM8550 UFS 主机、PHY、时钟和 SMMU 资源 |
| 板级依赖 | 板级电源策略和存储布局 |
| 已验证设备 | [参考原生 UFS 根卷](/zh/devices/sheng#storage) |
| 运行时类 | `NativeUfs` |

组件目录提供内核 archive 构建命令。设备配置启用 `CONFIG_XNU_NATIVE_UFS` 并提供板级输入。

```sh
./unixnu build kernel -D /path/to/device
```

## 移植与记录

ShengUfs 由设备仓库作为子模块提供。阅读 [UFS 移植指南](/zh/porting/ufs)，
按[设备存储记录](/zh/devices/sheng#storage)维护控制器、时钟、PHY、SMMU、DMA、
分区和完成条件。

arm64e 的公开源码构建方法及当前链接、运行时限制见[公开源码驱动构建](/zh/porting/migration#source-drivers)。历史 iOS 17 真机结果不代表该路径已通过验证。

## Wi-Fi DMA 窗口

WCN7850 DMA 窗口为 128 MiB，IOVA 从 0x10000000 起，使用独立
SMMU 上下文中的 64 个 2 MiB 块。设备验证已达到 Wi-Fi 接口就绪和
网络传输，DMA 分配失败为零；板级 `scripts/check-wifi-dma.py` 检查
容量和分配边界。
