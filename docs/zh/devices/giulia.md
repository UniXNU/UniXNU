# 一加 Ace 5（giulia）

搭载 SM8650 的社区设备移植。当前状态依据下方固定版本的维护者记录。

| 仓库 | 维护者 |
| --- | --- |
| [UniXNU-OnePlus-Ace5](https://github.com/tycykp/UniXNU-OnePlus-Ace5) | [tycykp](https://github.com/tycykp) |

## 当前状态

iOS 16 / Darwin 22 移植已进入 Hello 和设置界面，覆盖完整 1264x2780 面板，触控坐标正确。CPU0、原生 UFS、HFSX 根卷、`launchd` 和 USB CDC 日志可用。精简按键构建已验证物理电源键和音量键。

Wi-Fi 已到达 PCIe、BHI/BHIE、AMSS 和 QMI 资源请求，实机在 firmware-ready 之前的 QMP open 处停止。仓库包含 GPU 准备服务和音频运行时代码，GPU 执行器、无线联网及音频播放待实机验证。

## 来源

- [README: tycykp/UniXNU-OnePlus-Ace5](https://github.com/tycykp/UniXNU-OnePlus-Ace5/blob/aaa100d19f6fb14e5897a7e496edf7838d4d4e9f/README.md)

## 使用此移植

1. 阅读上方仓库的构建说明和固定版本记录，准备对应的固件、系统镜像和板级输入。
2. 按该仓库的命令构建，通用配置见[构建与启动](/zh/building)。
3. 按[启动验证顺序](/zh/porting/bring-up)逐项验证，通过[日志抓取](/zh/porting/log-capture)保存结果。
4. 更新[移植记录](/zh/porting/records)，记录实际使用的源码版本及最后确认的阶段。
