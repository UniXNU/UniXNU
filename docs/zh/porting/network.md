# Wi-Fi 适配

先完成[平台中断和 DMA](/zh/porting/platform)。确认无线芯片、PCI ID、固件和 board-data 变体。
实现回调前阅读 [Ath12kWifi](/zh/drivers/ath12k-wifi)和 `include/nw_abi.h`。

实现后按[驱动接入步骤](/zh/porting/drivers#build-integration)连接初始化调用、归档配方和 OS ABI，
再执行本页对应的硬件验证。

## 源码与接口 {#source-map}

以下链接固定到已核对的源码版本。使用所选 SoC、组件和 OS 版本核对接口；
链接的设备源码提供板级集成示例。

| 实现部分 | 源码 | 阅读与实现内容 |
| --- | --- | --- |
| 可复用接口 | [nw_abi.h](https://github.com/UniXNU/Ath12kWifi/blob/f6bf561f92cc42761bdd417fce1d53fe1db9477c/include/nw_abi.h#L9) | `lx_platform`、`nw_board`、`nw_wifi_events` 与 station 调用 |
| 工作线程实现 | [nw_wifi.c](https://github.com/UniXNU/Ath12kWifi/blob/f6bf561f92cc42761bdd417fce1d53fe1db9477c/src/nw_wifi.c) | `nw_wifi_start/step/stop` 与事件分发 |
| 硬件集成 | [WifiProbe.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/WifiProbe.cpp) | PCIe、MSI、DMA 分配及固件访问回调 |
| OS 集成 | [WifiNet.cpp](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/package/WifiNet.cpp) | 网络服务、Apple80211 请求和收发所有权 |

## 1. 区分集成层次


阅读[板级源码](https://github.com/UniXNU/UniXNU-sheng/tree/main/package)。
参考实现将 WCN7850 接到 SM8550 PCIe0。组件还包含 QCC2072 和 QCN9274 定义。
选择定义前，核对驱动中的端点硬件版本和固件支持。

## 2. 启动 PCIe 端点

记录控制器与 PHY 地址窗口、通道数、复位顺序、WLAN enable、PERST、参考时钟、稳压器、
互连投票、SMMU stream 和 MSI 路由。参考实现在板级 package 中使用 C++ 常量和表。

1. 检查已供电、已启用时钟的寄存器状态。
2. 执行目标板的电源、时钟、PHY 配置和复位顺序。
3. 训练链路并读取端点 vendor/device ID。
4. 分配并映射 BAR，检查 PCI capability，启用需要的 memory 和 bus-master 操作。
5. 建立端点 DMA 范围，确认分配缓冲区在选定缓存策略下可达。
6. 接入 MSI 并确认中断到达，再依赖中断推进驱动。

**预期结果：** 端点正确、BAR 可读、DMA 可用且中断到达。参考探针用 `sheng-wifi` 选择阶段：
1 检查交接状态，2 启动链路，4 检查端点。当前端点路径在阶段 5 及以上进入可复用协议栈，由协议栈执行 MHI 和固件启动。
在新设备启用前阅读对应阶段源码。

## 3. 提供组件回调

按 `nw_abi.h` 实现 `lx_platform` 的时间、休眠、轮询、日志、内存分配、DMA 分配/映射/同步
和 `fw_get`；实现 `nw_board` 的 BAR、PCI 身份、配置空间访问和 MSI 目标。

参考实现使用 `native_ufs_extra_*` 提供 DMA 内存区，使用 `native_ufs_part_*` 读取固件。
采用其他存储或 DMA 实现的移植，需要提供等效板级服务。
在 `proprietary-files.txt` 中记录固件文件名、board data 和校准数据来源。

调用 `nw_wifi_start`，再由板级工作线程调用 `nw_wifi_step`。事件回调在该线程执行，应及时返回。
停止推进时检查 `nw_wifi_stats`、`nw_wifi_where`、板级 MSI 计数和固件日志。

实现回调时按 `nw_abi.h` 保持所有权：`dma_alloc` 返回清零的 CPU 内存和端点可达的 bus 地址，
`dma_map` 为范围外的缓冲返回 0，`dma_sync` 按传输方向同步缓存。
`fw_get` 按文件名返回数据与长度，保证数据在组件消费期间有效。
先安装 `nw_wifi_events`，再启动工作线程；`nw_wifi_step` 非零时继续推进。
接收回调若要把帧交给异步 OS 路径，应在返回前复制到 OS 拥有的缓冲。
关闭接口时停止新提交，停止工作线程和组件后再释放 BAR、MSI 与 DMA 资源。

**预期结果：** 固件与 QRTR 服务启动，随后扫描产生 BSS 记录。分别记录固件启动和扫描成功。

## 4. 接入 OS 网络接口

按选定 XNU 和无线框架 ABI 适配 `WifiNet.cpp`，将 `nw_wifi_scan`、`nw_wifi_connect`、
`nw_wifi_tx` 以及接收和链路事件接入 OS。提供该 userland 所需的 MAC 身份、信道/监管数据和请求布局。

在完整组件列表中选择 Ath12kWifi。参考实现由 `build-gop-legacy-display.py` 调用
`build-ath12k-wifi.py` 构建组件，并链接 `WifiProbe.cpp` 与 `WifiNet.cpp`。
在组装后的构建树检查：

```sh
rg -n 'struct lx_platform|struct nw_board|nw_wifi_' drivers/Ath12kWifi/include/nw_abi.h
rg -n 'nativewifi|wifi_module_objs|WifiNet|WifiProbe' scripts/build-gop-legacy-display.py
```

按[构建指南](/zh/building)重建内核、payload 和启动镜像。

**预期结果：** 扫描、认证、关联、地址配置、接收和发送分别成功。
在网络记录中写明接入点配置、固件、重连行为和持续传输结果。

## WCN7850 参考实现 {#sheng}

参考实现能加入 WPA2-Personal 网络，通过 DHCP 获得地址并加载网页。
`sheng-wifi=5` 启动 Wi-Fi；`sheng-wifi-aj=0` 让设置应用负责加入网络。

| 方面 | 结论 |
| --- | --- |
| 供电 | 六路 PMU 电源都需要 RPMh 的模式、电压和使能请求。缺少模式请求时有两路不上电，链路无法训练。 |
| PCIe | PCIe0 训练到 Gen2 x1；端点 ID 为 `17cb:1107`。 |
| 中断 | 芯片的 MSI 经 PCIe0 自己的 MSI 接收器送到 SPI 141，工作线程在中断之间睡眠。 |
| 固件 | c7-00108 可以运行；c2-00259 卡在按需分页器中。固件报告的 MAC 为零，由板级用芯片 ID 生成。 |
| 扫描 | 不扫描 6 GHz：其 59 个被动信道会占用大部分扫描时间。 |
| 关联 | 对端条目使用接入点自己的 HT 和 VHT 能力，而不是本机的。加入和四次握手约 100 ms。 |
| 链路 | 5 s 内仍收到帧时忽略固件的 beacon 丢失。VHT MCS 10 和 11 的帧会被丢弃。 |
| 系统 | 系统无法保存网络密码，因此不把该网络视为已知网络。 |

## 下一步

有基带的设备继续[基带与移动网络](/zh/porting/baseband)，其余设备继续 [DSP、音频和电源](/zh/porting/power)。也可返回[驱动清单](/zh/porting/drivers)。
