# DroidVM 客户机（Gunyah 上的 crosvm）

DroidVM 目标把 UniXNU 作为客户机运行在高通手机 Gunyah hypervisor 上的 crosvm 中。下面的移植是独立的社区项目，UniXNU 组织不维护它。

| 仓库 | 维护者 | 状态 |
| --- | --- | --- |
| [UniXNU-droidvm](https://github.com/Droid-VM/UniXNU-droidvm) | [Droid-VM](https://github.com/Droid-VM) | 内核构建、verified root、锁屏和主屏幕 |

## 状态

| 阶段 | 状态 |
| --- | --- |
| 内核构建 | 在 macOS 27 和 Xcode 27.1 上完成 |
| UEFI 到 XNU | 在 SM8650 和 SM8850 上工作，4 KiB 页 |
| 根 | 原始 OS 和 SystemOS 镜像在只读 virtio-mmio 磁盘上通过校验 |
| 桌面 | 启动约一分钟后到锁屏，按 Home 后到主屏幕；SM8650 上 CPU 呈现，widget、Safari 和壁纸 overlay 通过 Metal 绘制 |
| Data | SM8650 上通过 store 磁盘持久化 |
| 输入 | 触控屏和 Home 通过 virtio-input |
| 网络 | en0 通过 virtio-mmio 上的 virtio-net，桥接到手机 Wi-Fi；SM8650 上 DHCP IPv4 和 IPv6 工作 |
| Keychain | 条目通过 AppleKeyStore 的 wrap 和 unwrap 存储；bluetoothd 运行 |
| GPU | 通过 crosvm `--droidvm-gpu` 在手机主机的 KGSL 上运行 NativeAdreno；widget 渲染器、图标、Safari 和壁纸 overlay 通过 Metal 插件绘制。每个客户机进程使用自己的 KGSL context，单个客户端故障不会拖垮 render server；完整 GPU 应用尚未验证 |

[BigfootACA/unixnu-droidvm-ci](https://github.com/BigfootACA/unixnu-droidvm-ci) 为 QEMU/KVM 和 DroidVM 目标提供 CI 构建。

## 维护

维护者拥有仓库和发布决定。UniXNU 文档记录移植及其状态，不接管维护。
