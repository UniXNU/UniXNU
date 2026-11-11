# Xiaomi 14 Pro 23116PN5BC

[YX2748198202-lab/UniXNU-shennong](https://github.com/YX2748198202-lab/UniXNU-shennong)

<div v-pre>

Xiaomi 14 Pro \(23116PN5BC\)。UEFI 菜单稳定（v6）；iPadOS 17.7.11 供体上 XNU 走到 vfs\_mountroot、UFS/SMMU/GPT/SHNGROOT 根卷已真机验证。当前供体 iPhone17,1 iOS 27.0.1（arm64e，XNU 12377.121.6）卡在开 MMU 之前的 trampoline 窗口，持久日志与实机镜像重建见 docs/agent-progress.md。

源记录: [porting.toml](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/porting.toml), `06e6620154860cf388f302e76d41718dfade1489`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `host-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `implemented` |
| [显示](#display) | `implemented` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`host-verified`

组件: `ArmDTPlatform`, `XnuPrelink`.

### 硬件与依赖

- SM8650 / shennong 的 board.toml 身份字段：name=shennong、soc=SM8650、os\_profile=ios-27.0.1-24A446-iphone16pro
- SoC feed 固定为 UniXNU-sm8550-common 的 pin（SM8650 与 SM8550 的 UFS GCC 偏移完全一致）
- 板级 ADT 由 scripts/make-shennong-adt.py 生成，只含 cpu0 与必要属性

### 配置

- board.toml：schema\_version=2；\[kernel\].archives 使用 component: 语法；\[kernel.prelink\].slide=-0x1000000
- defconfig：CONFIG\_XNU\_NATIVE\_UFS=y、CONFIG\_XNU\_BOOT\_PROGRESS=y、CONFIG\_XNU\_ARM\_DT\_PLATFORM=y、CONFIG\_XNU\_SOURCE\_MOCKFS=y、CONFIG\_XNU\_SOURCE\_CORECRYPTO14=y
- payload 的 ADT 在 CI 中被板级树覆盖（mcopy 覆盖 kernel.macho.adt 并回读 sha256 校验）

### 操作步骤

- Actions → kernel → Run workflow；job 内先跑第一遍 bootstrap，再打补丁、重建归档，跑第二遍正式 kernel
- 量取 IOStorageFamily 绑定：scripts/scan-prelink-storage.py --ipsw &lt;IPSW&gt; --device-class j120ap --tree &lt;TREE&gt; --output scripts/prelink-storage-bindings.json
- 按 slide 平移并提交：scripts/apply-prelink-slide.py --bindings … --board board.toml

### 开发经验

- schema\_version 升到 2 后，payload 的 ADT 改由 IPSW 设备树派生，会带回 iPad 的 /cpus，导致 AppleARMCPU 认领失败并 panic；必须用板级 ADT 覆盖
- 绑定表量自原厂 kernelcache，而 prelink 会把每个组件平移 \[kernel.prelink\] slide；不平移时绑定的构造函数落在零字节上
- 量出来的 pin 必须提交回仓库：构建消费的是仓库里的 pin，流水线只在构建后才测量

### 完成条件

- 所有源码 pin 可解析；组件与 patch 顺序在记录中可见；CI 两条 pass 均能产出 kernel.macho 与 payload.img

### 当前范围

- 配置层的真机验证只覆盖到 vfs\_mountroot 与存储栈；显示/输入等子系统的配置尚未开始

### 下一步

- 根窗口发布通过后，为显示与输入补配置项（framebuffer、touch）

### 证据

- `host`: [CI 解析 board.toml、选入全部组件并产出 kernel.macho 与 payload.img](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>Actions kernel run 42003983808</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- Mu-Silicium shennongPkg（不在本仓库）构建的 UEFI 固件卷 SILICIUM\_UEFI.fd，0x300000 字节
- boot image 采用 header v0 + gzip\(BootShim+FD\) + append\_dtb，模板取自本机固定镜像
- DTB 由 FD 内置，不依赖 ABL 的 vendor\_boot

### 配置

- fastboot boot 直接启动 boot image；不写 boot/vendor\_boot 等引导分区
- panic 屏由 payload 内的 BootProgress 组件直接绘制到帧缓冲

### 操作步骤

- python3 scripts/repack-v0-bootimg.py --template Mu-shennong-smp.img --payload payload.img --out Mu-&lt;variant&gt;.img
- usbip 把设备接进 WSL 后：fastboot boot Mu-&lt;variant&gt;.img

### 开发经验

- UEFI v1–v6 的失败点依次是 PmicDxe、UFSDxe（初始化期 UFS Sleep）、SPMIDxe 打偏、电源链连带、菜单二次重绘；修法见 docs/bringup.md
- header v4 在 fastboot boot 场景拿不到 ABL 的 DTB，必须用 v0 + append\_dtb

### 完成条件

- 固件构建、进入 UniXNU、稳定显示菜单、发布帧缓冲并保留内存保留区

### 当前范围

- UEFI 固件不在本仓库，无法由 CI 复现；boot image 组装依赖本机模板

### 下一步

- 把 UEFI 固件的构建输入（shennongPkg 配置与补丁）单独整理并记录到可复现路径

### 证据

- `device`: [UEFI v6 菜单稳定显示 10 秒，logo 清晰](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/bringup.md)
  Command: <code>fastboot boot Mu-shennong-6-pmgr2.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

## CPU 与中断 {#cpu}

`device-verified`

组件: `ArmCpu`.

### 硬件与依赖

- SM8650 CPU 拓扑与 PSCI：架构 timer 19.2 MHz，PSCI method SMC
- AppleARMPlatform.kext 的 AppleARMCPU personality 使用 IONameMatch=cpu（前缀匹配）

### 配置

- 板级 ADT 的 /cpus 只保留 cpu0（state/reg/device\_type/compatible/timebase-frequency），不带 psci 与副核
- payload args 中保留 armcpu-diagnostics=1 便于观察认领结果

### 操作步骤

- 用 scripts/make-shennong-adt.py 生成 10,208 字节 ADT，CI 覆盖到 payload 的 kernel.macho.adt
- fastboot boot 后观察是否越过 AppleARMCPU.cpp:111 并到达 bsd\_init

### 开发经验

- 原厂 iPad 设备树带 cpu0..cpu7 与 psci，AppleARMCPU 会认领并 panic；xpu 单字节补丁只是掩盖，换 ADT 才是根因修复
- sheng-smp=1 只影响副核，改变不了 cpu0 的驱动归属

### 完成条件

- 每个使能的 CPU 到达入口检查点，timer/IPI 在每个 CPU 上工作

### 当前范围

- 目前只验证单核启动；副核上线与 CPU 频率管理尚未开始

### 下一步

- 根卷挂载后为副核补 ADT 节点并验证 IPI

### 证据

- `device`: [换板级 ADT 后 XNU 越过 AppleARMCPU 并停在 vfs\_mountroot](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/STAGE-C-2026-11-04.md)
  Command: <code>fastboot boot Mu-plain.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- DRAM 12 GiB，起始 0x80000000；splash\_region 0xFC400000；FD\_BASE 0xA7100000
- UFS 的 DMA 走 SMMU，stream ID 0x60

### 配置

- UEFI 阶段的帧缓冲与 FD 内存保留区按 docs/hardware.md 的记录处理
- UFS 的 SMMU 上下文由驱动在启动时规划（见 storage 区域的接管补丁）

### 操作步骤

- 用 docs/hardware.md 的地址表核对 panic 屏的 pages/free 计数
- SMMU 侧用 native-ufs-probe=10 观察 smr/s2cr/cbar/sctlr 的读回值

### 开发经验

- XNU 早期内存初始化正常：stage C 的 panic 屏 pages=0xbb6a free=0xb3ef 量级正常
- SMMU 上固件留了独占 SMR（smr=80000060 s2cr=2，translation 开着），规划器需接管该 bank 才能读出磁盘

### 完成条件

- 所有 handoff 区域有归属，每个使能的 DMA 引擎按文档的 cache 策略访问其分配范围

### 当前范围

- 尚未做 XNU 侧的 DMA 一致性压力测试；SMMU 只接管了 UFS 这一个 stream

### 下一步

- 根卷挂载后核对 Data 卷写入的一致性

### 证据

- `device`: [接管 SMMU bank 后 UFS 能读出根卷；panic 屏内存计数正常](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>fastboot boot Mu-ufsr12b.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

## 存储与根卷 {#storage}

`implemented`

组件: `ShengUfs`, `VirtioMmioBlock`, `RamBlock`, `VerifiedRoot`.

### 硬件与依赖

- UFS 控制器 ufshc@1d84000，逻辑块 4096 B，GCC 偏移与 SM8550 完全一致
- 根卷：从 iPadOS 17.7.11 \(21H461\) IPSW 提取 OS 与 Cryptex1,SystemOS，生成 SHNGROOT 卷写入 userdata
- IOStorageFamily 的 190 个 vtable 槽位与 6 个 VerifiedRoot 符号以绝对符号方式绑定

### 配置

- board.toml：\[userdata\] first\_lba=2260480 last\_lba=64049146 lba\_bytes=4096；\[kernel\].archives 含 component:ShengUfs 与 VerifiedRoot 归档
- payload args：native-ufs-probe=12 / native-ufs-root=1 用于分阶段验证；sheng-pmgr=2 常驻
- 根策略：policies/ 存放本板 544 字节签名头与 395 字节公钥，哈希表作为根卷对象 OS.vroot / SystemOS.vroot

### 操作步骤

- 量绑定并按 slide 平移后提交，再构建（否则构造函数落在零字节）
- 写卷：fastboot flash userdata userdata-root.img（sparse，实测 34/34 块）
- 验证：fastboot boot 带 native-ufs-probe=10 时读 GPT 与卷首块；native-ufs-probe=12 时发布并列出介质

### 开发经验

- 固件留下的 UFS SMMU 独占映射需接管（smr=80000060 s2cr=2 → cbar=00010000 sctlr=00000000），补丁在 patches/ufs-smmu-takeover.patch
- 驱动要求 owner 签名策略才发布根窗口：configureVerification 需要 1..16 条策略，本板策略由 scripts/make-root-policy.py 用自建 RSA-3072 密钥生成
- 无验证构建里 validate\(\) 恒返回 false，绕过只会停在 signed window identities；正解是提供真策略
- 策略对象必须按清单偏移落在 4 KiB 对齐处且 image\_bytes 为 4096 倍数，否则驱动分别报 VR\_HASH\_TABLE 与 manifest=4；追加工具一度用 append 模式打开镜像，seek 被忽略导致第二个对象漂移 753,376 字节

### 完成条件

- Host：寄存器/时钟/链路/SMMU 与板级清单一致。Reads：SCSI 容量、GPT、已知块正确，OS/SystemOS 窗口落在 userdata 内。Root：配置的卷挂载且 launchd 启动；写入在重启后仍在

### 当前范围

- 根窗口已发布为 IOMedia（published=2、142 次读取零失败），但 XNU 尚未挂载根卷
- 尚无 Data 卷（/private/var）、无 dyld 缓存、未进入用户态

### 下一步

- 用 native-ufs-root=1 让 XNU 挂载已发布的根窗口

### 证据

- `device`: [根卷可读：magic=474e4853 544f4f52、manifest status=0 windows=2](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>fastboot boot Mu-ufsr12b.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.
- `device`: [两个根窗口发布为 IOMedia：published=2 reads=142 failures=0 media=7，UUID 与策略一致](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>fastboot boot Mu-policy12.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

## 显示 {#display}

`implemented`

### 硬件与依赖

- 1440x3200 DSC cmd 面板，msm\_drm.dsi\_display0=qcom,mdss\_dsi\_n2\_42\_02\_0a\_p2\_dsc\_cmd
- XNU 阶段可用 UEFI GOP 的帧缓冲

### 配置

- panic 屏由 payload 内的组件直接绘制：文字锁在上 52%，标记区在 60%/68%/76%/84%/90%

### 操作步骤

- fastboot boot 任意诊断镜像，观察顶部三色彩条与下方文字/标记是否清晰

### 开发经验

- XNU 自身没有显示驱动，输出走 serial；板级组件直接画帧缓冲才让 panic 可见
- 菜单阶段的 logo 曾导致崩溃（UniXNU 菜单二次重绘），最终把 logo 上限压到 160px

### 完成条件

- 已知画面以正确几何与颜色出现，随后用户态呈现与背光控制可用

### 当前范围

- 只有诊断画面；没有 XNU 显示驱动、没有背光控制、没有用户态呈现

### 下一步

- 根卷挂载后为显示补 DCP/DPU 探针

### 证据

- `device`: [诊断屏可读：stage、HC/SMMU/GPT 字段与 frames 均正常显示](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>fastboot boot Mu-ufsr12.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

## 输入 {#input}

`planned`

### 硬件与依赖

- Synaptics TCM over SPI 触控；电源/音量键走 PMIC 侧
- UEFI 阶段菜单需要输入时曾因指针失效崩溃，最终以单帧路径绕过

### 配置

- 暂未配置：CONFIG\_XNU\_OWNER\_\* 均为 n，输入相关组件未选入 board.toml

### 操作步骤

- 待实现：在 ADT 中补触控节点，选入 ShengHidInput 组件后启动观察 HID 上报

### 开发经验

- 当前阶段没有可用输入通道；UEFI 菜单靠 HasInput=FALSE 规避

### 完成条件

- 触控映射到显示坐标，多点保持稳定 ID，释放事件到达，按键产生预期 HID 报告

### 当前范围

- 完全没有开始

### 下一步

- 显示子系统可用后再接输入

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 750（rev 2770）

### 配置

- 暂未配置：GPU 相关组件与 AGX/Adreno 探针未选入

### 操作步骤

- 待实现：先做 GMU/GPU 寄存器探针，再评估 Metal 客户端

### 开发经验

- 当前没有任何 GPU 提交路径

### 完成条件

- GPU 提交完成，映射/fence 正确，已知图像渲染并被 Metal 客户端呈现

### 当前范围

- 完全没有开始

### 下一步

- 用户态起来后再攻 GPU

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- 板载 Wi-Fi 走 PCIe（本机未做枚举）

### 配置

- 暂未配置

### 操作步骤

- 待实现：先枚举 PCIe，再接对应固件

### 开发经验

- 当前无网络栈

### 完成条件

- Wi-Fi 驱动完成且能收发

### 当前范围

- 完全没有开始

### 下一步

- 用户态起来后再攻网络

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- 未采集音频编解码与 I2S 拓扑

### 配置

- 暂未配置

### 操作步骤

- 待实现：先采集 audio 拓扑再选组件

### 开发经验

- 当前无音频路径

### 完成条件

- 音频通路建立且能播放

### 当前范围

- 完全没有开始

### 下一步

- 用户态起来后再攻音频

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PMGR：AMFI 需要 provider-less ApplePMGRNub；已用 ShengPlatformPower 满足

### 配置

- payload args 常驻 sheng-pmgr=2

### 操作步骤

- 待实现：补齐 regulator/clock 的 PMGR 表

### 开发经验

- ShengPlatformPower 只是让 AMFI 过去的 provider-less nub，不是完整的电源管理

### 完成条件

- 供电域与时钟域按板级表工作，休眠/唤醒可用

### 当前范围

- 只有最小 nub；无完整 PMGR 表

### 下一步

- 挂载完成后补 regulator 表

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`device-verified`

### 硬件与依赖

- CI 产出 kernel.macho 与 192 MiB 的 payload.img FAT 卷
- boot image 需要本机固定模板（设备 /sdcard 已被覆盖，模板改为电脑本地保存）

### 配置

- payload args 由 scripts/patch-payload-args.py 改写 unixnu.toml
- repack-v0-bootimg.py 复用模板前 2,400,256 字节，只替换 payload

### 操作步骤

- 下载 artifact → 取 payload.img → 改参数 → repack-v0-bootimg.py → fastboot boot

### 开发经验

- payload 固定 201,326,592 字节，因此 boot image 长度稳定，便于逐轮对比
- CI 无法直接产出 boot image：模板来自本机 UEFI 固件

### 完成条件

- 内核与 prelink 成功，payload 含全部声明的输入，boot image 匹配 bootloader 格式与大小限制

### 当前范围

- boot image 组装依赖本机模板文件；CI 只到 payload

### 下一步

- 把模板纳入可复现的构建输入后再谈 CI 全自动

### 证据

- `host`: [CI 构建成功：kernel 与 payload 产物 41,973,584 字节](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>Actions kernel run 42003983808</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.
- `device`: [重打包的 boot image 被 bootloader 接受并启动](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>fastboot boot Mu-policy12.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

## 诊断 {#diagnostics}

`device-verified`

组件: `BootProgress`.

### 硬件与依赖

- XNU 无显示驱动，诊断必须直接画帧缓冲
- 驱动内置 native-ufs-probe / native-ufs-diagnostics / native-ufs-root 等启动参数

### 配置

- CONFIG\_XNU\_BOOT\_PROGRESS=y；payload 常驻 boot-progress=2 与 diagnostics=1

### 操作步骤

- 按阶段取参数：probe=10 读盘校验、probe=12 发布并列出介质、root=1 直接挂载；每次只看一个目标

### 开发经验

- 诊断屏是这一阶段最有效的手段：smmu 冲突、绑定地址落在零字节、策略门禁三处都是靠屏幕定位的
- 驱动失败是软失败（只 IOLog），必须靠 panic 报告与 gRootDiagnostic 字段

### 完成条件

- 每个声明的里程碑都有可复现命令、对应的源码/镜像 revision 与可访问的结果

### 当前范围

- 诊断屏只覆盖早期启动；进入用户态后没有串口可用

### 下一步

- 根卷挂载后把诊断通道扩展到 vfs 层

### 证据

- `device`: [probe=12 报告 stage、HC/SMMU/GPT/WINDOWS 字段与 pubPhase](https://github.com/YX2748198202-lab/UniXNU-shennong/blob/06e6620154860cf388f302e76d41718dfade1489/docs/handoff/UFS-E3-2026-11-05.md)
  Command: <code>fastboot boot Mu-ufsr12.img</code>. Revision: `14eaf555283f05334555ca596c56d32069156f3e`.

</div>
