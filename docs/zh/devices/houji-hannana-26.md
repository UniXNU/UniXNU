# Xiaomi 14 23127PN0CC \(houji\) \(hannana-26\)

[hannana-26/UniXNU-houji-ios27](https://github.com/hannana-26/UniXNU-houji-ios27)

<div v-pre>

Xiaomi 14 23127PN0CC \(houji\)。iOS 27.0.1 \(24A446, arm64e\) 移植,APFS+SHNGROOT 官方路线\(与 sheng 同\)。r46 的 APFS gate 错绑 panic 已修复并实机验证\(c1d3026\);r50 的信任包\(f93a554\)使 launchd exec 成功、dyld 映射 \~930 MB 后死于用户态 SIGSEGV\(Initproc failed to start -- exit reason namespace 2 subcode 0xb\),已闯入 Stage 7。UEFI sheng-log 读取器 v4.1/v4.2 实机验证\(清屏+分页\);\*\*r17 实证窗口头=168B sheng v5 流式环\(CI 用 sheng kit 的 BootLog,本地 v4 副本未编入\),r15/r16/r17 内核均 \~38-48s 静默停止无 panic 屏\*\*;v4.3\(按 msg\_head 游标读真尾部\)已构建待试机\(工程记录在仓库外 D:/yizhishouji/交接文档\_最新.md 与 进度记录\_2026-11-13.md\)。

源记录: [porting.toml](https://github.com/hannana-26/UniXNU-houji-ios27/blob/58363cf3e04a8e25d21d0f7e1dbd587c5c70a8c2/porting.toml), `58363cf3e04a8e25d21d0f7e1dbd587c5c70a8c2`.

本页按设备记录自动生成。

| 部分 | 状态 |
| --- | --- |
| [配置](#configuration) | `device-verified` |
| [固件与启动](#firmware) | `device-verified` |
| [CPU 与中断](#cpu) | `device-verified` |
| [内存与 DMA](#memory) | `implemented` |
| [存储与根卷](#storage) | `device-verified` |
| [显示](#display) | `device-verified` |
| [输入](#input) | `planned` |
| [GPU](#gpu) | `planned` |
| [网络](#network) | `planned` |
| [音频](#audio) | `planned` |
| [电源](#power) | `planned` |
| [镜像组装](#packaging) | `device-verified` |
| [诊断](#diagnostics) | `device-verified` |

## 配置 {#configuration}

`device-verified`

组件: `ArmDTPlatform`, `ArmCpu`, `XnuPrelink`, `DarwinBoot`.

### 硬件与依赖

- SM8650 / houji 的 board.toml 身份:name=houji、soc=SM8650、os\_profile=ios-27.0.1-24A446、kit=sheng\(package/ 作为 kits/sheng 安装\)
- soc\_source=sm8550 临时替代\(SM8650 与 SM8550 的 UFS GCC 偏移一致,shennong 同例;UniXNU-sm8550-common 本地未核实\)
- 本地供体 IPSW 是 iPhone18,2 的 iOS 27.0.1;profile 按 iPhone17,2 处理\(偏差已记录\)
- XnuPrelink fixture:patches/xnuprelink/fileset-houji-24A446-symbols.json,25→189 函数+22 data\(并入 aston d94ap,同 kernelcache sha256 fa07057b\)

### 配置

- board.toml:schema\_version=2;\[kernel\].archives 用 component: 语法 + kit 提供的构建脚本;\[payload\] kernel\_args 带 native-source-storage=1/native-ufs-root=1/native-ufs-diagnostics=1/sheng-log=1
- defconfig=houji\_ios27\_defconfig\(configs/\);config\_fragments=common/sm8550/ios
- \[payload.runtime\] trust\_components=StaticTrustCache、Cryptex1,SystemTrustCache、Cryptex1,AppTrustCache;gpu\_addon=false
- \[payload.adt\] chip\_id=0x8140 未核实;packed\_data\_ramdisk=true\(r1d85a10 教训:非打包种子在 darwinboot 窗口展开触发 EFI\_BAD\_BUFFER\_SIZE\)
- dts:GIC 节点补 AAPL,phandle\(1d51174,XNU 只从 AAPL,phandle 注册中断,peridot marble-milacy 先例\)

### 操作步骤

- CI 主仓 macos.yml:device\_repository=hannana-26/UniXNU-houji-ios27、device\_ref=storage、defconfig=houji\_ios27\_defconfig、steps=kernel payload
- pre\_build 必须:git submodule update --init kits/XnuPrelink;cp $DEVICE\_DIR/patches/xnuprelink/\*.json kits/XnuPrelink/fixtures/\(没有这句 fixture 不进构建,run 43793597183 教训\);brew install ipsw;make-houji-data-seed.py 生成 Data seed
- 构建产物经 scripts/package.sh 校验链;本地自检 gatecheck47.py\(GOT 绑定\)+ chkadt.py\(ADT\)

### 开发经验

- r46 实机 APFS gate 错绑 panic 的根因是 fixture 缺口:把 aston d94ap fixture\(同 kernelcache sha\)并入后 r47 实机验证 panic 消失\(c1d3026\)
- XnuPrelink fixture 按 kernelcache sha256 匹配,不一致不生效;2 条实机验证绑定\(0xab86b04 \_ml\_get\_hwclock、0xb0de1d8 apple\_m2\_property shim\)保留并注记 revisit
- fixture 没拷进 kits/XnuPrelink/fixtures 时构建照常成功但绑定缺失——CI 必须带 cp 步骤
- r49/r50 实证:amfi\_get\_out\_of\_my\_way=1 只旁路 AMFI,内核 exec 签名校验独立存在;必须用 trust bundle\(f93a554\)

### 完成条件

- 所有源码 pin 可解析\(unixnu.lock\);组件与 patch 顺序在记录中可见;CI 产出 kernel.macho 与 payload.img;实机 r50 走到用户态 exec

### 当前范围

- chip\_id 0x8140、DTB 来源\(ROM 215/设备 212\)、UNIQUE\_CHIP\_ID 未核实/未设置;\[userdata\] first\_lba/last\_lba 仍是占位 0\(内核运行时读 GPT\)

### 下一步

- r50 稳定后 revisit 两条实机验证绑定\(0xb0de1d8、0xab86b04\);补 chip\_id 与 UNIQUE\_CHIP\_ID 核实

### 证据

- `device`: [r47:gate panic 消失;r50:launchd exec 成功进入 dyld](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r47/r50%20%E5%90%84%E8%8A%82%29)
  Command: <code>fastboot boot boot-houji-r47-probe.img / boot-houji-r50-probe.img</code>. Revision: `c1d302624bd52066d5a3698e3db0be316d649d67`.
- `host`: [CI 产出 kernel.macho+payload.img,fileset\_match 逐条验 original\_sha256 全过](https://github.com/hannana-26/UniXNU/actions/runs/43797480096)
  Command: <code>gh workflow run macos.yml -R hannana-26/UniXNU …(交接文档 §6 完整命令)</code>. Revision: `f93a55480962cb72604c877b52fcc15ef78d65fe`.

## 固件与启动 {#firmware}

`device-verified`

### 硬件与依赖

- Mu-Silicium houjif 树\(WSL /root/uefi-asm,不在本仓库\)构建的 UEFI;UEFI 内嵌 UniXNULib\(Main/Menu/Ui/ShengLog 等\)
- boot image:ANDROID 头\(mkbootimg header\_version=4,本地 repack\)+ gzip 内核段\(BootShim+FD\)+ 追加 DTB;DTB 来自 ROM 215 与设备 212 的偏差已记录;OEM DXE 来自 OnePlus 13R\(偏差\)
- UEFI 诊断探针 ShengLog.c 目前在 D:/yizhishouji/work/ShengLog.c\(v4 草稿\),未进设备仓库\(纲领三★例外:探针类\)

### 配置

- fastboot boot 临时启动;不刷 boot/vendor\_boot
- \[bootimg.image\] base/offsets/pagesize=4096;board.toml 记 header\_version=0,本地 repack 实际用 v4+追加 DTB\(差异在 findings\)
- panic 屏由 payload 内 entry-probe\(xnu-panic-screen.c\)渲染;\[payload\] panic\_screen=false 时靠探针

### 操作步骤

- WSL:/root/uvenv/bin/python3 build\_uefi.py -d houjif -r DEBUG;产物 Mu-houjif-0.img 经 mk15.py 与 payload-r50 组装成 boot-houji-r15-shlog4.img
- 试机前后用 work/uefiid.py\(内嵌 UEFI kernel 段 sha\)、work/verifyboot.py\(payload 尾哈希+字符串\)、work/lzmapeek.py\(FV LZMA 解压字符串\)三道校验

### 开发经验

- r47-r50 四轮实机:UEFI 菜单/自动启动/panic 屏渲染稳定\(406x720 录屏\)
- OEM UFS 驱动每次外部块读打印一轮失败转储并直接画帧缓冲\(多块重叠、盖写控制台文本\);UEFI 直读存储不在官方流程内,是本仓补的新空缺;v4.2 改先读完→ClearScreen→再打印规避盖屏
- r14-dump 内嵌 UEFI 的构建无法从当前树复现\(sha 8a3b26d3 vs DEBUG 296eb18f/RELEASE b3dfc635\)——历史产物构建未钉版;已建立三道校验流程补救
- UniXNULog 只走 DEBUG+串口,手机不可见;上屏只能 Print\(ConOut\),而官方 UI 图形模式绝不经 ConOut——Print 在本机固件的上屏性以 v2 实机\(v2 两个头行上屏\)为准,仍属脆弱通路
- r16 实机\(r15 残留\):候选命中 dev6、头 ver4/148B/win8192 布局实证;msgbuf 尾=CoreAnalyticsHub 周期噪声\(handleNagTimerExpiry/messageClients,内核串比对确认\)非死因;头行 2 数值被录屏分辨率墙卡住\(疑 state=2/up≈32s 未定论\);\*\*r15/r16 内核 \~45-58s 静默停止、无 panic flush\(state=5 缺席\)、无 panic 屏,r16 菜单后黑屏 \~48s 自动重启——死因未知,QEMU A/B\(r14 296eb18f vs r17\)待做\*\*
- 工程教训:v4.2 曾因 \*Msg 未初始化\(UB\)被 LTO 静默删除整个打印分支——镜像校验必须含字符串级检查\(verify42.py\),构建通过≠内容正确

### 完成条件

- 固件构建、进入 UniXNU、稳定显示菜单、panic 屏可读;sheng-log 窗口读写链路的写侧\(内核\)已实机工作\(r50 有槽写入\);读侧 v4.1 实机读出 r15 残留\(r16 轮\),v4.2 打印版待试机

### 当前范围

- UEFI 固件树不在本仓库无法 CI 复现;OEM UFS 驱动行为不可假设\(每次读刷屏,1MiB 读疑似被拒\);录屏 406x720 是日志转写的分辨率硬墙\(单帧最锐利+逐行放大为上限\)

### 下一步

- r17\(v4.2 先读后印\)试机读出干净日志;QEMU A/B 查 r15/r16 静默停止;读回日志后把读取器等价改动评估落进设备仓库

### 证据

- `device`: [r14-dump\(UEFI v3+payload-r50\)完整走完:菜单→panic,读取器零输出\(判据缺陷,离线已复现\)](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r14%20%E5%A4%8D%E7%9B%98%29)
  Command: <code>fastboot boot boot-houji-r14-dump.img</code>. Revision: `c1d302624bd52066d5a3698e3db0be316d649d67`.
- `device`: [r16\(UEFI v4.1 f71e7ba1\):候选探测 dev0..6 未命中+1 台回退扫描+dev6 命中 HEADER at -32 MiB\(ver4/148B/win8192\);msg 尾=噪声对;菜单后黑屏无 panic 屏,\~48s 自动重启](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r16%2C%202026-11-16%2019:40%29)
  Command: <code>fastboot boot boot-houji-r16-shlog4b.img(用户已确认)</code>. Revision: `0ab48686ba49b673d9e3bfacfb4e6e930dd621c7`.
- `host`: [v4.2\(先读后印+ClearScreen+分页\)构建校验全过:verifyboot payload-r50 吻合、UEFI 段 c0d3e226、verify42 七串 FOUND;报废件 r17-shlog4c 361b2f84\(\*Msg 未初始化致 LTO 删 msg 分支\)留档未试机](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r17%20%E6%9E%84%E5%BB%BA%E6%A0%A1%E9%AA%8C%29)
  Command: <code>build_uefi.py -d houjif -r DEBUG &amp;&amp; mk17.py &amp;&amp; verifyboot/uefiid/verify42</code>. Revision: `097820e3980f8e8af3727e30a2711817bbf8f485`.
- `device`: [r17\(v4.2 92408d14\):清屏机制实证成功;头块读清=\*\*168B sheng v5 头\(NOTE 168\!=148\)+ state=2 writing/up=38s/written=28;槽仅 \#slot 28 t=38s tag=\(28B,普查组件在 houji 被 stub\)\*\*——payload 的 BootLog 来自 sheng kit\(v5 流式环\),本地 v4 副本不是编进内核的那份;v4.x 按 v4 线性取尾在环上取到任意旧区段](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r17%2C%202026-11-17%2008:25%29)
  Command: <code>fastboot boot boot-houji-r17-shlog4c2.img(用户已确认)</code>. Revision: `097820e3980f8e8af3727e30a2711817bbf8f485`.
- `host`: [v4.3\(v5 流式环感知:解析 msg\_mode/msg\_head,按游标读真尾部\)构建校验全过:UEFI 7f1d9773、verify43 八串 FOUND;待试机读 r17 残留的真尾部](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r18%20%E6%9E%84%E5%BB%BA%E6%A0%A1%E9%AA%8C%29)
  Command: <code>build_uefi.py -d houjif -r DEBUG &amp;&amp; mk18.py &amp;&amp; verifyboot/uefiid/verify43</code>. Revision: `bd578b39d65c4fb132f6c2fc658cefdc67f262bd`.
- `device`: [r18\(v4.3\):\*\*8 台大设备候选+末尾 64MiB 扫描全部 no header,读取器快速退出\*\*;dev 0 几何损坏\(bs=4096, \*\*974192 MiB≈951GiB 垃圾值\*\*\)+tz\_armv8\_smc\_call 成片失败——静默复位后 UEFI 侧 UFS 几何劣化,窗口数据大概率仍完好](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r18%2C%202026-11-17%2008:40%29)
  Command: <code>fastboot boot boot-houji-r18-shlog4d.img(用户已确认)</code>. Revision: `bd578b39d65c4fb132f6c2fc658cefdc67f262bd`.
- `host`: [v4.4\(GPT 驱动定位:借 aston RootLayout.h 只读解析器,读 GPT→打印分区表→userdata/最大尾部分区直探窗口头,Media-&gt;LastBlock 只做兜底,&gt;1TiB 几何跳过扫描\)构建校验全过:UEFI 927b1296;待试机](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r19%20%E6%9E%84%E5%BB%BA%E6%A0%A1%E9%AA%8C%29)
  Command: <code>build_uefi.py -d houjif -r DEBUG &amp;&amp; mk19.py &amp;&amp; verifyboot/uefiid/verify43</code>. Revision: `c774d8afb3fec9e26b4b376c28989994b439b34f`.
- `device`: [r19\(v4.4 6184d467\)已 fastboot boot\(08:46,用户确认\),录屏已拍但视频尚未分析——GPT 分区表打印是本轮核心诊断\(窗口在不在介质上一目了然\);视频路径由用户在新会话提供\(微信 temp\)](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r19%2C%202026-11-17%2008:48%29)
  Command: <code>fastboot boot boot-houji-r19-shlog4e.img(用户已确认)</code>. Revision: `c774d8afb3fec9e26b4b376c28989994b439b34f`.

## CPU 与中断 {#cpu}

`device-verified`

组件: `ArmCpu`.

### 硬件与依赖

- SM8650 CPU 拓扑与 PSCI\(架构 timer,PSCI method SMC,与 shennong 同 SoC\)
- AppleARMPlatform 的 AppleARMCPU personality 按 IONameMatch=cpu 前缀认领

### 配置

- payload args:cpus=1、armcpu-diagnostics=1;\[payload.adt\] kernel-ctrr-to-be-enabled=0\(SM8650 无 CTRR,vermeer/aston/sheng 同\)

### 操作步骤

- fastboot boot 后经 panic 屏/日志观察 AppleARMCPU 认领与 bsd\_init 推进

### 开发经验

- 单核下 XNU 从内核入口一路走到用户态 exec\(r50\):CPU 认领、timer、IPI 无阻塞
- 副核未启用\(cpus=1\)

### 完成条件

- 启用的 CPU 到达入口检查点,timer/IPI 工作

### 当前范围

- 只验证单核;副核上线与频率管理未开始

### 下一步

- launchd SIGSEGV 定位后再评估副核

### 证据

- `device`: [r50 launchd exec 成功\(用户态\),说明 cpu0/timer 链路可用](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%C2%A73)
  Command: <code>fastboot boot boot-houji-r50-probe.img</code>. Revision: `f93a55480962cb72604c877b52fcc15ef78d65fe`.

## 内存与 DMA {#memory}

`implemented`

### 硬件与依赖

- DRAM:2 GiB 连续窗口 0x8c0000000 附近\(lonlzi houji UEFI HighRAM 先例,作者自述,须等于 DTS memory 节点\);dram\_size=0x80000000
- r19:8 GiB owned\_memory\_size 溢出 XNU 16 页 bootstrap 表\(start\_first\_cpu 自环\),回落 = dram\_size

### 配置

- \[payload\] dram\_size=0x80000000;\[payload.adt\] owned\_memory\_size=0x80000000;DarwinBoot 窗口 2 GiB

### 操作步骤

- panic 屏 pages/free 计数核对内存状态\(r50:dyld 映射 \~930 MB 后 Free=0x34bef\)

### 开发经验

- panic 屏计数与预期量级一致;未出现内存类 panic
- packed\_data\_ramdisk=true 避免 8 GiB 种子展开越窗\(r1d85a10\)

### 完成条件

- handoff 区域有归属;DarwinBoot/内核/DarwinBoot 窗口边界未越界

### 当前范围

- 未做 DMA 一致性压力测试;SMMU 侧未单独审计

### 下一步

- Data 卷持久化\(persistent\_data\)评估时补内存审计

### 证据

- `device`: [panic 屏 pages=0x786? Free=0x34bef,数值合理](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r14%20panic%20%E5%B1%8F%20OCR%29)
  Command: <code>fastboot boot boot-houji-r14-dump.img</code>. Revision: `c1d302624bd52066d5a3698e3db0be316d649d67`.

## 存储与根卷 {#storage}

`device-verified`

组件: `ShengUfs`, `RamBlock`, `VerifiedRoot`, `VirtioMmioBlock`.

### 硬件与依赖

- UFS LUN0,4096 字节逻辑块;根卷=官方 IPSW 的 iOS 系统卷按 SHNGROOT 组装后整写 Android userdata 分区\(build/userdata-r1/userdata-root.img,15.25 GiB,已刷\)
- 根策略:iPhone17,2 24A446 OS/SystemOS 窗口的 544 字节签名头+公钥\(scripts/policies/ios-27.0.1-24A446,aston 同镜像 owner 策略\)
- Data:RAM seed\(make-houji-data-seed.py,packed\_data\_ramdisk=true\)

### 配置

- board.toml \[userdata\]:partition=userdata、lba\_bytes=4096、first\_lba/last\_lba 占位 0\(内核运行时读 GPT\);windows=OS/Cryptex1,SystemOS
- payload args:native-source-storage=1、native-ufs-root=1、native-ufs-diagnostics=1、sheng-log=1\(日志窗口=userdata 尾 8192\*4KiB\)

### 操作步骤

- 写卷:fastboot flash userdata userdata-root.img\(sparse 分块,不覆盖,新产物新编号\)
- 验证:host 侧 work/uuid47.py 读 userdata-root.img\(卷 UUID=E3F4AED0-4454-4D5B-833C-E27E99C4F67B,卷名 Rave24A446.D94OS,SHNGROOT v2 manifest 四窗 sha256 与 profile 一致\);实机 fastboot boot 看 A 挂载行与 \[cryptex os\] 阶段
- 日志读回:UEFI ShengLog 读取器\(见 diagnostics\)

### 开发经验

- r46 APFS gate 错绑 panic 已修\(c1d3026\)且 r47 实机验证;r50 信任包后 launchd exec 存活、dyld 映射 \~930 MB——SHNGROOT 挂载链路实机成立
- OS 卷 UUID 就是实卷 UUID,不是 cupid 拷贝错\(uuid47.py 关闭待核实 1\)
- 内核信任包\(f93a554\)是 exec 签名校验的必要条件,AMFI 旁路不够\(r48/r49 实证\)
- sheng-log 写侧在真机工作:槽环/头按 2s 轮写\(BootLog.c v4=148B 头\);读侧 v1-v3 读取器未读到\(v3 判据缺陷,离线复现;待 v4 按头直读\)

### 完成条件

- Host:GPT/卷/manifest 校验过。Reads:SCSI 容量、GPT、OS/SystemOS 窗口落在 userdata 内。Root:配置卷挂载且 launchd 启动\(r50\)
- 持久化:RAM seed,重启不保\(见 limits\)

### 当前范围

- 无持久 Data 分区\(persistent\_data=false\);first\_lba/last\_lba 占位;userdata 不可回 HyperOS\(alien 格式化风险\);launchd SIGSEGV 未定位

### 下一步

- UEFI v4 按头直读读回日志定位 SIGSEGV;之后评估 Data 持久化与 first\_lba/last\_lba 实测回填

### 证据

- `device`: [launchd exec 存活,dyld 映射后 SIGSEGV\(namespace 2 subcode 0xb\)——根卷挂载与 exec 链路实机成立](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r50%20%E8%A1%8C%29)
  Command: <code>fastboot boot boot-houji-r50-probe.img</code>. Revision: `f93a55480962cb72604c877b52fcc15ef78d65fe`.
- `host`: [OS 卷 UUID/卷名/SHNGROOT v2 manifest 逐字节校验一致](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28uuid47%20%E6%A0%A1%E9%AA%8C%2C%202026-11-16%29)
  Command: <code>wsl python3 work/uuid47.py build/userdata-r1/userdata-root.img</code>. Revision: `f93a55480962cb72604c877b52fcc15ef78d65fe`.

## 显示 {#display}

`device-verified`

### 硬件与依赖

- 面板经 UEFI GOP 工作\(菜单/panic 屏均可见,录屏 406x720\)
- XNU 自身无显示驱动;panic 屏由 entry-probe\(xnu-panic-screen.c\)直接画帧缓冲

### 配置

- \[payload\] panic\_screen=false\(本内核 panic padding 不匹配,r12/r13 教训\);panic 屏由探针渲染;serial=3 只走串口\(手机无串口线\)

### 操作步骤

- 录屏→work/fr47.py 抽帧→OCR\(ocr3.py/ocr46.py\)或 zoom14.py 放大裁剪直接读图

### 开发经验

- panic 屏是本阶段最有效诊断面:r47-r50 的死点全部由屏读出
- 内核 printf 不上屏\(serial=3\);OEM 驱动直接画帧缓冲会与控制台文本互相盖写
- 无触摸:菜单靠定时自动启动\(UuXNU 菜单 Esc 可停\)

### 完成条件

- 已知画面以正确几何与颜色出现

### 当前范围

- 无 XNU 显示驱动、无背光控制、无用户态呈现;无触摸输入

### 下一步

- launchd 死因定位后再攻显示驱动

### 证据

- `device`: [r50/r14 panic 屏文本完整可读\(Initproc failed to start -- exit reason namespace 2 subcode 0xb\)](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r14%20OCR%29)
  Command: <code>fastboot boot + 录屏抽帧</code>. Revision: `c1d302624bd52066d5a3698e3db0be316d649d67`.

## 输入 {#input}

`planned`

### 硬件与依赖

- 触控未开始;遗留:STI device path 待查

### 配置

- 暂未配置

### 操作步骤

- 待实现

### 开发经验

- 当前无输入通道;菜单以定时自动启动规避

### 完成条件

- 触控映射到显示坐标,多点稳定,按键产生 HID 报告

### 当前范围

- 完全没有开始

### 下一步

- 显示子系统可用后再接

### 证据

按下一步操作收集证据。

## GPU {#gpu}

`planned`

### 硬件与依赖

- Adreno 750;\[payload.runtime\] gpu\_addon=false,houji GPU addon 未配置

### 配置

- 暂未配置:GPU addon/AGX 探针未选

### 操作步骤

- 待实现

### 开发经验

- 信任包只含原始 caches,无 GPU addon 成员

### 完成条件

- GPU 提交完成,Metal 客户端呈现

### 当前范围

- 完全没有开始

### 下一步

- 用户态稳定后再攻 GPU

### 证据

按下一步操作收集证据。

## 网络 {#network}

`planned`

### 硬件与依赖

- 板载 Wi-Fi 走 PCIe,未枚举

### 配置

- 暂未配置

### 操作步骤

- 待实现

### 开发经验

- 当前无网络栈

### 完成条件

- 扫描/关联/收发通过

### 当前范围

- 完全没有开始

### 下一步

- 用户态稳定后再攻网络

### 证据

按下一步操作收集证据。

## 音频 {#audio}

`planned`

### 硬件与依赖

- 音频编解码/I2S 拓扑未采集

### 配置

- 暂未配置

### 操作步骤

- 待实现

### 开发经验

- 当前无音频路径

### 完成条件

- 声道路由可用

### 当前范围

- 完全没有开始

### 下一步

- 用户态稳定后再攻音频

### 证据

按下一步操作收集证据。

## 电源 {#power}

`planned`

### 硬件与依赖

- PMGR/电池/充电拓扑未采集;sheng-pmgr 类板级参数未启用

### 配置

- 暂未配置

### 操作步骤

- 待实现

### 开发经验

- 当前无电源管理路径

### 完成条件

- 供电/时钟域按板级表工作

### 当前范围

- 完全没有开始

### 下一步

- 挂载完成后补 regulator 表

### 证据

按下一步操作收集证据。

## 镜像组装 {#packaging}

`device-verified`

### 硬件与依赖

- CI 主仓 macos.yml 产出 kernel.macho 与 payload.img\(payload-rXX 目录同序\);boot image 由本地 repack\(work/mk15.py\)用 UEFI 模板+payload 组装
- payload 必须带完整 pre\_build\(submodule init + fixture 拷贝 + brew ipsw + data seed\),device\_ref=storage\(master 停在 r45 时代\)

### 配置

- \[bootimg.image\] base=0x80000000 kernel\_offset=0x8000 pagesize=4096;本地 repack 用 header\_version=4+追加 DTB\(board.toml 记 0,差异见 findings\)
- 产物不覆盖:boot-houji-rN-&lt;tag&gt;.img 新编号,payload-rXX 目录同序

### 操作步骤

- gh workflow run macos.yml\(完整命令见交接文档 §6\)→ dlart.sh 下载 → mk15.py 打包 → verifyboot.py/uefiid.py/lzmapeek.py 校验 → fastboot boot\(等用户'开始'\)

### 开发经验

- 连试三次 CI 才成功:43793597183 缺 pre\_build、43795594697 缺 brew ipsw,43797480096 成功——pre\_build 必须整段携带
- 仓库 Actions 被禁\(HTTP 422\)时 Actions 页有绿色按钮自助恢复\(fork 常规开关\)
- r14-dump 的 UEFI 构建不可从当前树复现\(8a3b26d3≠DEBUG 296eb18f≠RELEASE b3dfc635\)——历史产物未钉版;已建立三道校验

### 完成条件

- 内核与 prelink 成功;payload 含全部声明输入;boot image 被 bootloader 接受并启动\(r47-r50/r14 五轮\)

### 当前范围

- boot image 组装依赖本机 UEFI 模板;CI 只到 payload

### 下一步

- 把 UEFI 构建输入\(houjif 树\)纳入可复现路径;ShengLog 等价改动评估落仓库

### 证据

- `host`: [CI kernel+payload 成功,产物组装后 r50 实机启动](https://github.com/hannana-26/UniXNU/actions/runs/43797480096)
  Command: <code>gh workflow run macos.yml -R hannana-26/UniXNU -f device_ref=storage …</code>. Revision: `f93a55480962cb72604c877b52fcc15ef78d65fe`.
- `device`: [sha256 1f8fe334…96d4 实机完整走完菜单→panic](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r14-dump%20%E9%95%9C%E5%83%8F%29)
  Command: <code>fastboot boot boot-houji-r14-dump.img</code>. Revision: `c1d302624bd52066d5a3698e3db0be316d649d67`.

## 诊断 {#diagnostics}

`device-verified`

组件: `BootProgress`.

### 硬件与依赖

- XNU 无串口输出\(serial=3\),诊断靠 panic 屏与 sheng-log 窗口
- sheng-log 窗口:userdata 尾 8192\*4KiB;头=块 0\(v4=148B:magic/version/header\_bytes/boot\_id/first\_lba/window/msg/slot 字段/tag/export/diag\);msg buffer=块 1..32\(128KiB,每轮重写,盘上 oldest-first 线性\);槽=块 33 起每槽 16 块,LogPeriodMs=2000,槽序号取模 slot\_count;头每轮最后写\(slots\_written 是提交点\)
- 外部工具链:work/sym.py\(符号化\)、fsent.py、dis46.py、fr47.py/ocr3.py/ocr46.py、zoom14.py、verifyboot.py/uefiid.py/lzmapeek.py、test\_shlog4.py

### 配置

- payload args:sheng-log=1、native-ufs-diagnostics=1;panic 屏由 entry-probe 渲染
- logfs 记录\(houji-logfs=1,默认关\):houji-logfs-period=N\(默认 5 轮≈10s\)、houji-logfs-recovery=1\(首次成功提交后写 BCB boot-recovery 并 PSCI 复位回 recovery\);写窗口仅 logfs/misc 两个整分区,由 RootCommands.h 门控,无 houji-logfs 参数的启动不碰这两个分区

### 操作步骤

- panic 轮:录屏→抽帧→OCR/放大→sym.py 符号化→fsent.py→dis46.py→四源扫描→动手
- 日志读回轮:UEFI ShengLog 读取器\(当前 v4 草稿:按头直读;四源扫描已定 IoAlign 对齐分配/4096 魔数对齐/version 分段门控三处修订\)

### 开发经验

- v3 读取器判据缺陷\(可打印率采样 4096B 与整个 Run\*85 比较,Run&gt;4818B 必拒\)导致零命中,离线复现于 work/test\_shlog4.py;msg buffer 盘上线性\(写入端 copy\_msgbuf 旋转紧缩\),'环形尾部最新'假设不成立
- 四源扫描交叉验证:头有 148B\(houji/shennong\)/156B\(fuxi crash\_\*变体\)/168B\(sheng v5,msg\_mode=1 流式环\)三形态——读取器必须按 header\_bytes+version 分段门控,魔数必须 4KiB 对齐
- r47-r50 的 panic 死点全部由 panic 屏符号化定位;符号化链路稳定
- r14-dump 产物考古:v3 确实在镜像并运行\(lzmapeek 解 FV 字符串\),零输出与判据缺陷一致;其构建不可复现\(流程缺口,已建三道校验\)
- 2026-11-17:r19 panic 无 fault 行的原因已核实——本内核 CONFIG\_XNU\_BOOT\_PROGRESS 关闭\(r50 kernel.macho 无 \_boot\_progress\_user\_abort\),且上游 boot\_progress\_critical\_exit 不覆盖 initproc
- 2026-11-17:对比 aston\(同 24A446 kernelcache、同 SoC 家族、已进 SpringBoard\),houji 的设备补丁序列缺 aston 的 zzzz-sheng-ipados27-bringup.patch;其中 47 位 TTBR0\(arm64e PAC 位置\)、4 KiB 内核上的 16 KiB dyld fixup 页拼装、Darwin 26 posix\_spawnattr 布局、lockdown\_mode 名称,均直接关系 launchd 在共享缓存映射后的用户态崩溃。上游 UniXNU patches/xnu-12377 无 T0SZ\_USER/16 KiB fixup 实现\(已 grep 核实\)
- 2026-11-17:zzyd + zzzz 整份照搬 aston\(不裁剪\),本地对 xnu ac9718fb 全序列 git apply 通过\(work/patchtest.sh\);外部符号均在补丁内定义或 weak
- 不加大内存\(sheng/aston 同为 dram\_size 2 GiB\);BootLog v4/v5 漂移延后
- 2026-11-17 r20/r21 实机:同一 r20 镜像两次结果不同\(第1次无蓝条、约 114 秒复位;第2次有蓝条后 120 秒不动、无 panic 屏\);r21\(去掉 47 位 TTBR0/16-bit ASID\)仍无蓝条、约 108 秒复位。无蓝条=内核第一条指令未执行,与早期 TCR 改动无关\(r21 已去掉\);有蓝条后卡死未被 r21 验证。启动结果呈好/坏交替,疑似开机状态相关\(推测\)。证据:build/bootimg-r1/r20c.mp4、r21raw.mp4、进度记录 2026-11-17。r21 补丁 houji-no-ttbr0-47.patch\(f014411\)
- 2026-11-17 纲领四②补扫 lonzzi/hannana-houji\(未动手机,仅评估\):其 logfs 日志管线实机验证\(r22/r26/r138,约 41 秒自动返回\)。实现:内核侧 HoujiUfsRead.cpp 的 saveNativeLog/writeLogBlock\(SCSI WRITE 10 写 16 个固定 LBA\)/flushLog\(SYNC CACHE\)/setRecoveryBoot\(misc LBA1024 BCB RMW 写 boot-recovery 864 字节\)/logTrialReset\(PSCI 0x84000009\),加自包含头 HoujiLogFile.h\(FAT12 校验+64KiB XNULOG.BIN 预留 16 簇+HJXNU001 头:run UUID+CRC32\)/HoujiLogCommit.h/HoujiRecoveryRecord.h/HoujiGptCheck.h/HoujiTableCrc32.h;host 侧 tools/capture-recovery-logs.py\(ADB 读整分区,按 UUID/CRC 校验解码\)。关键差异:其读回走 OrangeFox ADB 不经 UEFI——本机 UEFI 读取器看不到 userdata LUN 的读回断点由此绕开。移植成本:借其头文件\(&lt;40KB,无分配无 IO,红线低\)+给 NativeUfs 加 logfs LBA 目标写路径\(GPT 找 logfs 基址\)+BootLog 挂检查点保存,约 400-600 行,CI 一轮;host 脚本直接复用。前置条件与红线:①一次性准备=logfs 里预建 XNULOG.BIN\(lonzi r21 从原厂 logfs 备份重建 FAT\),对我们=动 userdata 以外分区,违反红线 1 字面,必须用户批准+先只读备份 logfs 全分区;②需确认本机 recovery 是否 OrangeFox\(BCB 自动返回的前提\);③已知局限:保存发生在内核检查点,无蓝条模式\(内核未执行\)拿不到日志,该模式仍缺 UEFI 侧证据;lonzzi 自述最后检查点未必含硬复位前最后一条指令
- 2026-11-17 logfs 写侧落地\(仅构建,未上机\):package/HoujiLogFsCore.h 为内核与 host 共用的自包含核心\(FAT12 校验/HJXNU001 记录头/header-last 提交事务/BCB 页,移植自 lonzzi BSD-2-Clause-Patent 头,块地址改为分区相对\);BootLog.c houji\_logfs 节按 houji-logfs 参数每 N 轮把 msgbuf 尾+横幅提交进 logfs 的 XNULOG.BIN\(数据页先写、头页最后写、SYNC CACHE、逐字节回读\),recovery 参数在首次成功提交后对 misc 做 BCB RMW\(保留 864 字节外的原内容\)+PSCI SYSTEM\_RESET;NativeUfs.cpp/RootCommands.h 加 logfs/misc 两个整分区写窗口\(GPT 名字查找,LUN0,与 store/log 窗互斥,hostInWindow 收口\)。与 lonzzi 常量差异:pristine 文件=64KiB 零,CRC 0xd7978eeb\(lonzi 的 0xabbe97d5 是其预写内容\);8.3 名为 XNULOG  两空格 BIN。host 侧 scripts/logfs-fat.py\(扫/建/解/自测\)与 scripts/check-logfs-core.c\(gcc 自测\)与本核共享同一判据,均 PASS\(CRC32 对 zlib 一致\);scripts/capture-logfs-recovery.py 只读抓取\(双读一致门\)。待办:真机 logfs 备份+scan 确认几何与 69..84 簇空闲后才能 build;本机 recovery 形态未确认
- 2026-11-18 纲领四四源扫描\(logfs 一次性准备/读回子系统,4 子代理并行只读,33 仓\):头条=logfs 出厂即 FAT12,lonlzi 从未重建——原厂 sda13/8MiB vfat\(Android 挂载,六个 64KiB 原厂 UefiLog;lonzzi archive/docs/log-capture.md:72-118\),几何 4096B 扇区/4KiB 簇/双 FAT/根目录 512 项/totsec 1280\(卷 5MiB\)/media 0xF8 与我们 HoujiLogFsCore.h+logfs-fat.py 判据逐字段一致;原厂 UEFI uefiplat.cfg 即有 SpecialLogPartition=LOGFS。lonzzi 准备=root adb 里 remount rw 借内核 FAT 分配器新建 XnuLog.bin\(现场分配簇 69..84=LBA 4170..4185 后固化,O\_DIRECT 双读校验;内核只写 16 数据块 WRITE\(10\),永不碰 FAT/目录,实机 r25\);读回=capture-recovery-logs.py 前后 SHA 绑定+FAT12 硬校验+HJXNU001 双 CRC\(实机 r237\)。路线②最强先例=lonlzi LogFsTest.h+UfsLogWriteGuard.h\(UEFI 连原厂 PartitionDxe→FAT 卷建文件→写→逐字节读回 CRC→LBA 写门仅 logfs 8MiB,houji 实机 r22/r25/r26 全 PASS\);官方 EnhancedFatDxe 可读写既有 FAT12 但无 Format\(UEFI 不能格式化裸分区\);fastboot flash 单分区写回有 lonlzi install-native-root.py 成例可套 logfs;aston 有 TWRP 写分区模板\(先备份/分片哈希/整区读回,实机\)与路线②安全栏清单\(boot-arg 门控+拒绝条件+写入限界+GPT CRC 前后比对\),且 aston 明文非 userdata 分区只读/不改 GPT/不自动建 FS=路线②零先例背书;路线①载体:lonlzi rescue 实为烧 recovery\_a\(AVB test key 重签,先备份 37 分区\)而非 fastboot boot 临时引导\(该环节未验证\),make-rescue-ramdisk.py 需自备社区 OrangeFox 基盘\(镜像不入库\);shennong\(同 SoC 14 Pro\)有 TWRP 3.7.1\_16 root adb 实机存在证据\(YX-lab docs\)。已扫无可借鉴:全 33 仓无 UEFI/内核建卷/mkfs 实现、无内核 flag 门控一次性建卷先例、2026-11-16 以来零 log/logfs/recovery 相关新提交。决策含义:准备语义修正=在出厂 FAT12 内预分配 XNULOG.BIN\(非建卷\),原厂文件占 69..84 则换链;写入载体待 r26 几何证据后与用户定\(a fastboot flash logfs 需红线批准且毁原厂文件/b root adb FAT 分配需 recovery 载体/c UEFI 文件 API 写借 lonlzi/d 裸块门控写无先例最后考虑\)
- 2026-11-19 纲领四补扫\(panic 显示子系统,服务 r53\):①官方=UniXNU-official scripts/xnu-panic-screen.c\(sha16 54B950A7,9283B,work/entry-probe.py ROOT 硬编码指向它\)+entry-probe 注入机制=panic cave 代码+\_panic 首指令跳转+\_panic\_trap\_to\_debugger funnel 跳转,padding 非全零即拒绝;②同设备=Kizashi3-houji panic-screen.c\(980CA102\)带 boot\_log\_panic\_flush 集成\(其 :41 注释=board log panic writer 落盘\),lonzzi/hannana 无 panic 探针脚本;③同代=YX-shennong 版最大\(68A1A7C6,17204B 自研扩展\),peridot 与 official 同版,fuxi/社区为同上游副本;④aston 版\(62E3D38E\)与 sheng 同版,aston/sheng BootLog.c 均有 boot\_log\_panic\_flush\(sheng:2954/aston:2032\)但其 panic-screen.c 均不直接调用;houji 自家 BootLog.c:2141 注释声明该函数由 panic screen 调用,57377b5\(11-15\)引入且为 06dfcba\(r25 CI\)祖先=r25 内核含此符号。借鉴决策:r53 用 official 版\(r50 实机验证纯上屏\);Kizashi3 带落盘变体留作屏幕不可读时的 r54 增强,本轮不加\(一轮一类改动+panic 路径不新增未测 UFS 依赖\)
- 2026-11-19 r53 打包\(build-only,未碰手机\):底版=orig21.macho\(当日完整性实锤:CI 44056541697 payload 现场抽取+ioname 补丁→sha256 71997ab1…30ea 与 orig21 逐字节一致\);gatecheck47 PASS;entry-probe --no-reset --no-stage2 --panic-screen\(panic 屏 0xa4f 字节@0xfffffff00ad83560,funnel@0xfffffff00ab69d48\);字节差证明=r51 内核\(b486d76d…\)vs r53 内核仅 2220 字节变化聚三区=\_panic 跳转\(0x3b65d48\)+panic 屏代码区\(0x3d7f560-0x3d7ffad,跨度 0xa4e\)+funnel 跳转\(0x4442dcc\),blue-bar cave/ENTRY\_VA 与 r51 全同;payload-r53 args 原样\(houji-logfs=1 houji-logfs-period=1 无 recovery,断言过\)+trustcache 在;镜像 boot-houji-r53-panic-logfs.img sha256 c761bc60…b860a2\(30142464B\);脚本 work/mk53.sh+mk53.py\(mk51 惯例\)
- 2026-11-19 r53 上机\(08:34:11 OKAY\):读取器读旧 r51 记录\(run 1eb85f0d…/47866B/CRC 5FD424A6\)并回放;菜单 t110、内核 t≈113 起跑;seg2 t0-26 屏幕全黑\(用户确认无文字无条带\),t≈27-28.5 未触碰自行复位→MI→原厂 recovery。与 r51 冻死 35 分钟不同,唯一已证变量=panic 屏补丁。代码自查:①BootLog 看门狗仅 sheng-autoreset 布防\(BootLog.c:2182,r53 无此参\)→排除;②官方 panic 屏实为'清下 7/8 屏\(0 填充\)→画字→写 mark→park\(wfe\)',无主动复位→复位非其所为;'清屏后画字前故障'=黑屏无字,与现象一致\(候选解释,推测未确认\);复位机制未确认。原视频已被微信临时目录清理丢失,3s 抽帧图 r53a/r53b 仍在

### 完成条件

- 每个里程碑有可复现命令、revision 与可访问结果;sheng-log 写侧实机工作\(r50 有槽\),读侧 v4 待试机

### 当前范围

- 读取器上屏通路\(Print/ConOut\)在本机固件的稳定性存疑\(官方 UI 图形模式不走 ConOut\);UEFI 探针未进设备仓库\(纲领三★例外\)

### 下一步

- 先申请只读红线放宽,用 fastboot reboot fastboot + fastboot fetch 读回 userdata 尾部日志窗��\(取 r20 第2次卡死的日志\);再批量试 r22a/b/c\(对照、sheng 检查点补丁整包、去 UEFI 读取器\),见 docs/handoff-2026-11-17.md §5
- UEFI 日志读取器线冻结\(r14-r19 无产出\);只有当 panic 文本不足以定位时才重启
- 2026-11-18:实机照片判读——本机 recovery=原厂 Xiaomi HyperOS Recovery\(非 OrangeFox\),logfs 读回端\(OrangeFox root adb\)前提不成立;OrangeFox/TWRP 官方均无 houji;lonzzi 用社区原 houji OrangeFox 修改版\(镜像不入库\)。候选:①找 houji 第三方 recovery 用 fastboot boot 临时引导\(不刷分区\);②UEFI/内核 flag 门控一次性准备 logfs\(无备份即写,需用户接受风险\);③读回端改 ShengLog UEFI 直读 logfs 记录。BCB 自动返回对原厂 recovery 无用,回收流程改为 r25 启动→手动回 fastboot→fastboot boot 临时镜像→adb 只读抓取
- 2026-11-18 四源扫描修正路线语义:logfs 出厂即 FAT12→准备=既有 FAT 内预分配 XNULOG.BIN\(非建卷;整卷重建仅在 r26 判 FAT12 无效时考虑\);写入载体按机制成熟度 a\)fastboot flash logfs\(host logfs-fat.py 造镜像,lonlzi flash 成例,需红线批准+用户接受毁原厂文件\) b\)root adb recovery FAT 分配\(lonlzi 全套脚本,需先解决载体\) c\)UEFI 文件 API 写\(lonlzi LogFsTest 实机先例,借进固件\) d\)裸块门控写\(无先例,须复刻 aston 安全栏,最后\);先决条件=r26 上机拿到本机 logfs 几何/目录/69..84 占用证据
- 2026-11-18 r26 实机判读定案:出厂 FAT12 有效、11 个原厂文件占簇 2..178,预留窗 69..84 被 UefiLog4@66..81+UefiLo\~3@82..97 占用→内核恒惰性。写入载体二选一交用户:W=整卷重建\(fastboot flash logfs 合成镜像,需红线批准+用户接受原厂 11 文件丢失,零代码改动,当轮可完成\)或 K=共存换链\(常量 69→首个空闲簇 \~179,借 lonlzi LogFsTest 式 UEFI 一次性建文件+内核 CI+三处判据同步,保留原厂文件,工程量一轮以上\)。等用户选择
- 2026-11-18 10:14 用户选 W 并两次确认\(载体+完整命令\)后执行:scripts/logfs-synth.py 合成 8MiB 全分区镜像\(sha256 aa029801e30ed2795b11b52420b85f6180b2476ded984e8b773824787168075f,自测链全绿:fat selftest PASS/scan=valid/decode=pristine d7978eeb\);getvar partition-size:logfs=0x800000 与镜像一致;fastboot flash logfs OKAY 0.25s——bootloader 接受 logfs 写入。工厂 11 文件已清除\(用户知情接受,不可恢复\)。验证启动待做:读取器应报 record pristine+allocation ready;若内核跑过 10s 首提交则 BCB+复位回 recovery\(houji-logfs-recovery=1\)
- 2026-11-18 10:16 验证启动实机\(r26 同镜像\):\*\*BCB 自动回 recovery 触发成功=日志通道激活\*\*——内核执行到 logfs writer、open 校验对合成新卷通过、首提交事务成功、BCB 写 boot-recovery、PSCI 复位回原厂 recovery\(t87 帧=主菜单,视频 89.7s 帧 r27f\)。XNULOG.BIN 现存该次启动内核日志\(横幅+msgbuf 尾\)。行为面:此后内核跑起来的每轮 boot 留记录并自动回 recovery;无蓝条坏模式无提交无 BCB=静默复位→两模式可区分。待办:回 fastboot 再 boot 读取器读回首份内核日志\(OCR 横幅+尾页\),然后逐轮日志复现好坏交替。【更正】上述'channel 激活'为推断非实证:该段判读由无图像输入模型作出,事后用 OCR 复核仅证实 r27 时间线\(UniXNU 菜单 t59→暗屏→MI 开机画面 t65-80→原厂 recovery 菜单 t83+\),并未见读取器 logfs 判词;是否发生内核首提交/BCB 写入须读回 XNULOG.BIN 才算证实。另:11:25 用户反馈 VolDown+电源进不了 fastboot,OCR 显示手机反复出 MI 开机画面\(约每 9s,非黑屏\),'电池低'说法无依据
- 2026-11-18 13:05 读回启动实机\(12:05:06 r26 同镜像,60fps 密集差分带 OCR r29d1/r29d2\)——\*\*日志通道端到端实证成立\*\*:①shlog-logfs: FAT12 allocation: valid\(合成卷通过全部校验\);②目录列表=OEM 栈已在簇 2..68 重建 UefiLog 系文件\(start 2/18?/34/50/66 各 65536B\)+XNULOG.BIN@start 69 size 65536,预分配 FAT 链使 OEM 首适配自动绕开 69..84\(UefiLog4@66 的链 66,67,68→85..97\)无重叠→共存自动成立;③\*\*record OK: run f1a7ede7…\(32hex OCR 未辨全\), 14614 bytes, payload CRC …\(未辨全\)\*\*=10:16 启动内核首提交实锤\(11:40 更正事项闭环\),内核每轮启动后 \~3-5s 即完成首轮提交并 BCB 复位回 recovery\(解释 r25/r26 时代看不到 panic 屏:recovery 参数下 panic 阶段被首提交复位抢先\);④banner\(1600B\)=\#HJXLOG … slots=0 state=2 msg=14561;⑤尾页=内核日志文本:Darwin Kernel Version 25.5.0… root:xnu-12377…\(内核横幅\)、vm\_page\_bootstrap: 493228 free pages、Interrupt-controller: failed to find the interrupt-controller\(早期告警\)、SourceStorage: Data disk started\(SourceStorage.cpp:80,grep 实证\)、大量 '… READ … return value of -22'\(-22=EINVAL,打印点不在本地仓库,应在 xnu 树\)——首份内核日志\(启动后前几秒全量\)已到手,是解释好坏交替的第一手材料;⑥本 boot 结局:菜单 t113→内核 \~t115→MI 画面 t119-125→recovery t128\(本次内核仅活 \~4-5s,大概率未做第二次提交,盘上记录仍=10:16 那条\)。待办:深挖 14614B 日志全文\(OCR/继续差分\),锁定 -22 失败点与 interrupt-controller 缺失的关系;暂不再 boot,避免覆盖记录
- 2026-11-18 15:14 尾页深挖完成\(r29d2 带 PNG 重识别\)+ \*\*-22 归属更正\*\*:①尾页=内核日志正文,时间线 \[2019.283632\]\(入口\)→\[2019.543060\]版权/Darwin 25.5.0 root:xnu-12377→vm\_page\_bootstrap 493228 free pages→\*\*IOCPUInterruptController: not registry member at registerService\*\*\(异常点,待评估\)→cpu\_start/clock/ktriage→\*\*APFS kext 加载\(apfs-3280.2.1\)\*\*→NativeUfs 固件上电\(context bank 70\)→\[2019.975055\] SourceStorage: UFS started→\[2019.980659\] Data disk started→\[2019.981139\] NativeUfs: published …→首提交 msg=14561:\*\*内核 0.7s 内走到数据盘发布\*\*,此为 r25/r26 recovery=1 下能看到的全部;②'UFS READ with return value of -22'/'error\_log: 130/280' 无内核时间戳、串不在 r25 payload/r47 内核/UEFI 树任意二进制中\(grep 实证\)→\*\*判定为 OEM UEFI 驱动在读取器 Stall 停屏期间的周期性重试刷屏,非内核临终日志\*\*\(更正 13:05 条的初步解读\);③BootLog.c:1996-2030 语义定案:首提交在首个 tick\(\~2s\),周期默认 5 轮,recovery=1 且 commits==1 即 BCB 复位→recovery=1 下 panic 阶段永远看不到;④据此打包两轮镜像\(args-only 本地重打,内核不动,无 CI\):\*\*r51=boot-houji-r51-logfs-norecovery.img sha256 862376453443bf7f85f4fce8e3836fdbf62e5053eff377cffe8e766443be0c54\*\*\(args=houji-logfs=1 houji-logfs-period=1,去 recovery→不复位,每 2s 提交,内核跑到自然死点,panic 屏恢复可见\)与 \*\*r52=boot-houji-r52-logfs-reader.img sha256 51312beb0b634cc64df6c3fa5ef806729ab0b047efc90498d36d05d6e8b03448\*\*\(args 去 houji-logfs→内核惰性,读取器读回不覆盖\)。待用户批准:r51 上机采集→r52 读回→OCR 拿死前日志
- 2026-11-18 20:05 r51/r52 双轮实机完成\(用户各确认一次\):\*\*r51 采集轮\(18:40:51 boot\)内核跑了 \~60 秒后卡死\*\*——用户实观'绿蓝条一直不变'\(18:43 起卡 \~35 分钟\);\*\*r52 读回轮\(19:23:16 boot\)读取器实证:\`record OK: run 1eb85f0d5c00…\(32hex\), 47866 bytes, payload CRC 5FD424A6\`,FAT12 valid,目录不变\(OEM 五件@2/18/34/50/66 + XNULOG.BIN@69\)\*\*;横幅行\(diff-band OCR t45.00\):\*\*\#HJXLOG t=60s rounds=31 slots=30 state=2 msg=47810\*\*——31 轮×2s=62s≈60s,内核跑了 60 秒\(日志 14561→47810 字节增长 3 倍\)后 writer 仍活着\(state=2\)但整机卡死=\*\*第三模式'绿蓝条卡死'的卡点在 \~60s,且死点日志已落盘\*\*;横幅段\(\[28591.04-144873\],单调基跳到 28591\):interrupt-controller 找不到、cpu-debug-interface 找不到、Darwin 25.5.0 root:xnu-12377 \(17:09:53 UTC 2025\)、pmap\_startup0 Init/release 88461 micros、\*\*vm\_page\_bootstrap: 493229 free pages, 31059 wired\*\*\(老记录 493228→本次 493229,差 1 页=不同 boot 实锤\)、'39 maps, 128 entries and 16 nodes'、gIOKitPageableFixed/compressor 等;\*\*尾页\(卡死点最后 \~4.8KB 日志\)OCR 进行中\*\*,结果待落;另:r51 视频\(406x720\)菜单后画面 OCR 全空=小分辨率下 panic 屏不可读,本轮靠 4K 片段+差分带 OCR 补齐;4K 9.8s 片段\(菜单→黑\)确认倒计时归零后无绿蓝条入镜\(与用户口述'一直绿蓝条'合并理解=bars 在其后出现并冻结\)
- 2026-11-18 20:20 \*\*r52 尾页解码完成:绿蓝条卡死模式的死点定位\(实锤\)\*\*——尾页\(最后 \~4.8KB,即卡死前日志\)剥出:\*\*①内核自己的提交日志线\*\*:\`HOUJI LOGFS: commit 26 bytes=43140 t=50s / commit 27 bytes=43701 t=52s / commit 28 bytes=44254 t=54s / commit 29 bytes=44807 t=56s / commit 30 bytes=45360 t=58s\`\(BootLog.c:2029 的 IOLog 原文,每 2s 一条、字节数递增,与横幅 rounds=31/msg=47810 完全自洽\);\*\*②卡死前的最后内核活动\(t=\[28651.5-666\],=内核 uptime 60.5-60.6s\)\*\*:\`CoreAnalyticsHub::handleMsgTimerExpiry\(IOtimerEventSource\)::838: messageClients of 1 available event\(s\)\`\(IOKit 定时器每秒活跃=内核活着\)→\*\*\`launchd \(1\) triggered …\`\*\*\(launchd pid 1\!\)→\*\*\`DYLD shared region in VM map 0xe9424b674adf967\`\*\*→\`slide\_Info\_page… start-0x4a74000 end-0x4a98000 version=5\`\(dyld 共享缓存 slide info 页\)→'…debuggers, this increases memory footprint almost…'——\*\*内核跑完了整套启动\(0.7s 发布→60s 内挂载+launchd exec\),冻结点=launchd/dyld 共享缓存映射阶段\*\*;③r52 读回轮本身正常\(record OK 47866B CRC 5FD424A6,读回不覆盖\);④与 r50 同阶段对照:r50 在同一阶段 panic\('Initproc failed to start' namespace 2 subcode 0xb,dyld 映射共享缓存 \~930MB 时 SIGSEGV\)且有 panic 屏;r51 payload 无 panic-screen,冻结时无 panic 文本上屏→'冻结发生在 panic 渲染前还是 panic 本体挂死'\*\*未确认\*\*;⑤结论:\*\*好坏交替之三'绿蓝条卡死' = 内核 60s 冻结于 launchd/dyld 阶段\(推测与 r50 SIGSEGV 同族\),死点日志已完整取证\*\*——下一步\(等用户\):A 复跑 r51 验证 60s 冻结可复现;B 打一版 panic-screen+logfs 的镜像抓 panic 原文;C 回归 r50 线的 dyld 阶段调试
- 2026-11-19 用户定 B,r53 已打包待上机:预期=前 60s 与 r51 全同\(UEFI→绿条→蓝条→logfs 每 2s 提交\),\~60s 起 A\)panic 屏出字=冻结即 panic\(录像 OCR 原文→sym.py 符号化\)或 B\)同款静默冻结=panic 未发生或渲染前挂死\(真挂死线,查调度/看门狗\);无 recovery=1 不自动复位,冻结后强制关机回 fastboot,再 boot r52\(只读\)读回最后记录\(state=2,死前 ≤2s\);boot 前等用户'开始'+录像确认\(红线 2\)
- 2026-11-19 10:36-11:05 读回定案:①盘上记录仍=旧 r51 记录\(run 1eb85f0d…/47866B/CRC 5FD424A6\)→r53 内核零提交;②r51 死点精确化:DYLD 行\[28651.665815\]后 0.21s 有 sheng-peek/fat\(page\_size=0x4000,pageIndex=1\)/chain\[0..11\]/sheng-sign\(首次 PAC 签名\)至\[28651.879148\]戛然而止——死在 zzzz 的 dyld 共享缓存 chained-fixup 修补流程内\(16K 页 on 4K 内核\),修正 11-18 'DYLD 行即死';③r53=坏模式实锤\(bars53.py 条带检测\):菜单 t110\(蓝=UI\)→绿条 t113-119→t122 消失→灰屏→复位=菜单引导+58s,无内核蓝条,四次坏模式\(r20/r21/r26/r53\)复位均在引导+55-60s=确定性定时器,与好模式 r51 冻结不复位是两个现象;④交付链复核:payload-r53 仅内核差 2220B/三区,zzzz 与 aston 逐字节一致且 aston 无新提交,同 kernelcache 已进 SpringBoard→fixup 死点 houji 特异,上游无现成修复
- 2026-11-19 11:05 下一步:r53 重试\(同镜像零构建,好坏交替赌好模式\)→好模式 60.8s fixup 死点处 panic 屏应出字+frames=定案死因;坏模式则再掷。读回视频 build/bootimg-r10/r52read.mp4+r52c 抽帧;r53 原视频已失,以 r53a/r53b 抽帧图与 bars53.py 为准
- 2026-11-19 11:58 r53 重试=好模式\(实锤,bars53.py:菜单 t116→t119 绿+蓝条同现并卡至视频尾 t257\);\*\*panic 屏出字\(实锤,t185 起画字,t191 清晰稳定 66 秒+,park 生效无复位\)\*\*,全分辨率帧 r53e/。死因链符号化\(sym.py,frames 修正公式=低47位\|0xffffff8000000000\):launchd 执行 dyld 共享缓存代码\(用户 pc=0x1806fb140\)同步异常 SIGSEGV→\_fleh/\_sleh\_synchronous→\_handle\_user\_abort→\[4帧未解=信号投递\]→\_ast\_taken\_user→\_bsd\_ast→\_postsig\_locked→\_exit\_with\_reason\(namespace 2 subcode 0xb\)→\_proc\_prepareexit\(.cold.2\)→panic\('Initproc failed to start'\)→panic 屏。\*\*r51 静默冻死=同一 panic 升级实锤\*\*\(同基座同时机,无屏无消息落盘\);死因与 r50 同型\(dyld mapping SIGSEGV\)。panic 原文与 17 帧见进度记录 12:20 节;panic 帧 OCR 用 ocrimg.py 全分辨率投票
- 2026-11-19 12:25 下一步\(C 线,需 CI 重建\):①提高 zzzz 调试打印上限\(chain 12→更多+按页\),②对照 aston 同 kernelcache 进 SpringBoard 的配置差异\(slide/TCR/PAC/16K fixup 页拼装\)定位 dyld 缓存坏页成因;坏模式成因与 4 未解帧符号挂起
- 2026-11-19 12:55 复核修正\(Sonnet,OCR 四帧一致=实锤\):panic 首行字段=pc 0x1806fb140/far 0x481e719ed30/esr 0x92000004\(L0 转换错误,用户态数据异常\)/指令 f9400268=ldr x8,\[x19\];即 launchd 在共享缓存内从垃圾指针 x19=0x481e719ed30 读数据崩。far 43 位宽吻合 chained rebase target 宽度=推测:数据槽存了未正确解码的 chained 原始值\(未验证\)。撤回 16K 拼装/slide/TCR/PAC 过度推断,r51=同一 panic 降为高度一致。零上机下一步:取 24A446 dyld 共享缓存反汇编偏移 0x6fb140 核对并定位函数与槽来源,再对照 zzzz 修补范围
- 2026-11-19 13:25 缓存静态分析定论\(零上机,实锤\):提取 24A446 dyld 共享缓存\(ipsw+apfs-fuse\);全缓存扫描指令字定位真崩溃点=libobjc realizeClassWithoutSwift+48\(0x18041b140\):\`mov x19,x0\`\(cls\)→\`ldr x8,\[x19\]\` 故障,far=x19=0x481e719ed30=垃圾类指针\(43 位,chained 槽字段宽度\);launchd ObjC 类实现解引用坏类指针→SIGSEGV→initproc panic。12:55 的 pc=CoreFoundation 判读作废\(OCR 巧合\);调用者尾部=NSURL removeCachedResourceValueForKey\(前缀未确认\)。死因=内核侧 fixup 修补产出坏类指针槽;与 aston 的差异聚焦 slide/修补基准。下一步=读回 r53-retry 盘上记录看 sheng-chain 尾部定肇事槽\(需用户开始+录像\);后备 C 线提高 chain cap
- 2026-11-19 13:40 读回 r53rb\(实锤\):r53-retry 记录=run e1253a7e…/45322B/CRC C728…,比 r51\(47866B\)短 2544B=缺尾;显示页序止于 commit29\(kernel t=56s\),DYLD/launchd/sheng- 页不在盘上\(logfs 写入早停 \~4.8s 于死亡\)——肇事槽信息不在盘上。自动引导=r51 代内核:好模式→boot+60.8s 死亡→条带冻结 100s 到视频尾\(用户证词\),r51 型冻死首次完整拍摄。\*\*关键换算:缓存用户态基址=0x100000000\(unslid=userVA+0x80000000\)\*\*,fixup 页 unslid=0x180741000\(子缓存.01 \_\_TEXT 区\);panic pc/ret 换算全吻合。下一步\(零上机\):解析缓存 fixup 元数据枚举 0x180741000 页全链,与 chain\[0..11\] 对账定位 \#12+ 肇事槽;不足则 C 线
- 2026-11-19 14:00 纲领四扫描定论\(实锤\):官方 UniXNU-sheng 有补丁 vmwait-dyld-pager-source-release.patch——4K 内核组装 16K fixup 页的源页 busy 自等死锁修复\(block hint 0x16,不可中断\),描述与 r51 冻死逐字吻合;官方 series 中紧跟 zzzz,我们 series 缺失。一因两症:死锁\(r51 型冻死\)或非驻留幸存后产物损坏→垃圾类指针\(r53-retry realizeClassWithoutSwift\)。签名守卫差异经 superboyyy/hakios 论证排除\(标准 PAC 后端 key=0 须签名\)。C 线方案:复制 vmwait 补丁进 series\(zzzz 后\)+chain cap 12→64+保留 panic 屏,CI 重建 r55

### 证据

- `device`: [v3 试机零输出+判据缺陷离线复现;panic 屏符号化链路多轮验证](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r14%20%E5%A4%8D%E7%9B%98%29)
  Command: <code>fastboot boot boot-houji-r14-dump.img;wsl python3 work/test_shlog4.py</code>. Revision: `c1d302624bd52066d5a3698e3db0be316d649d67`.
- `host`: [HoujiLogFsCore.h 自测全过\(CRC32=zlib 校验值/FAT12 往返+篡改 5 例/记录头往返+篡改/提交事务含失败路径/BCB 字节\);builder 自测 build→validate→模拟提交→decode 往返 PASS;capture 脚本 py\_compile 过](https://github.com/hannana-26/UniXNU-houji-ios27/blob/58363cf3e04a8e25d21d0f7e1dbd587c5c70a8c2/scripts/check-logfs-core.c)
  Command: <code>gcc -Wall -O2 -o t scripts/check-logfs-core.c -I package &amp;&amp; ./t;python3 scripts/logfs-fat.py selftest</code>. Revision: `3e34f56cd4975353a58115c8a119962c5b7e706e`.
- `host`: [CI 44056541697 内核\(含 logfs 写侧+args\)打包成功:args 含 houji-logfs=1/houji-logfs-recovery=1 断言过,ADT window 0x80000000,UEFI=Mu-houjif-r14 DEBUG 296eb18f,lzmapeek 内核解压含 SHLOG001;verifyboot 的 r2/r50 白名单未含 r25 属工具陈旧;CI 复盘:44050491474 失败根因=weak\_defaults 生成的 BootLogDefaults.c 继承 include 后全静态未用,已用 \_\_attribute\_\_\(\(unused\)\) 修复\(06dfcba\)](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r25%20%E9%95%9C%E5%83%8F%29)
  Command: <code>gh workflow run macos.yml -R hannana-26/UniXNU -f device_repository=hannana-26/UniXNU-houji-ios27 -f device_ref=storage -f defconfig=houji_ios27_defconfig -f steps='kernel payload' -f pre_build=…(交接文档 §6);bash work/mk25.sh 44056541697;verifyboot/uefiid/lzmapeek</code>. Revision: `42b04347ebe16e034ae7b98f430ff45d5ea9b417`.
- `device`: [r26 实机\(09:33:11,0.913s\):读取器 v4.5 首份 logfs 几何证据——dev 0 GPT 正常\(part 22..32: blackbox/oops/rawdump/opconfig/abuconfig/rescue/va-bootsys\_a\_b/va-persist/super/userdata 965361MiB\),logfs 分区 first LBA 4096\(base 16777216=16MiB 偏移\);出厂 FAT12 有效,11 个原厂目录项全 64KiB\(UefiLog3@2/UefiLog2@10或18/UefiLog1@34/UefiLog0@50/UefiLog4@66/UefiLo\~3@82/OTHER\_\~1@98/另一项@114/UefiLo\~1@130/UefiLo\~2@146/UefiLo\~4@163\),簇 69..84 被占\(UefiLog4@66..81+UefiLo\~3@82..97\);allocation 判词=native log FAT chain changed\(v4.5 判据=XNULOG.BIN 目录项+69..84 成链,源码 ShengLog.c:377-458\)→内核 houji\_logfs 恒惰性零写入\(与设计一致\);本轮启动=无蓝条静默复位模式\(菜单 \~53-64s,绿条 \~66-95s 消失,灰屏 95-123s,复位 \~123s=boot 后约 59s\),好坏交替又一样本\(坏\);dev 0 几何本轮正常 974192MiB\(64 chunks 0 read fails,r18 垃圾几何未复现\);logfs-fat.py build 对真备份会拒绝\(69..84 busy,SOP 预判情形\),整卷重建镜像须合成生成](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r26%20%E5%87%A0%E4%BD%95%E8%AF%81%E6%8D%AE%2C%202026-11-18%29)
  Command: <code>fastboot boot boot-houji-r26-logfs-uefi.img(用户确认);wsl fr47.py 抽帧+zoom14.py 放大判读</code>. Revision: `6a407ecfee6b9968bf53d10244c159af0d44939a`.
- `host`: [r53 打包成功\(build-only\):r25 CI 内核\(orig21 完整性实锤 71997ab1…\)+gatecheck47 PASS+entry-probe panic 屏注入 0xa4f 字节;字节差证明 vs r51 内核仅 panic 屏三区共 2220B\(\_panic 跳转/代码区 0xa4e 跨度/funnel 跳转\);args=houji-logfs=1 houji-logfs-period=1 无 recovery 断言过;payload sha 60953d22…;四源扫描与借鉴决策见 findings 2026-11-19](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r53%20%E9%95%9C%E5%83%8F%29)
  Command: <code>wsl bash /mnt/d/yizhishouji/work/mk53.sh(orig21 校验→gatecheck→entry-probe --no-reset --no-stage2 --panic-screen→args 断言→mk53.py);entry-probe/panic-screen.c=UniXNU-official(r50 同款)</code>. Revision: `6c03b689eaad6b02ce4027cd761000e58e46e551`.
- `host`: [C 线 r55 打包全绿:vmwait-dyld-pager-source-release.patch 入 series\(zzzz 后\)+诊断上限提升\(chain 64/mwl 8/sign 4/fixup 16\);主仓 macos.yml run 44469861649\(设备仓 package.yml=未启用模板已废弃\);CI 内核 ee175ed9→gatecheck PASS→panic 屏注入\(0xa4f@0xfffffff00ad83560\)→args 本地重写为 r51 系\(logfs=1 period=1,去掉 CI board.toml 遗留 recovery=1\)→boot-houji-r55-vmwait-logfs.img 30142464B d93314bb…;预期=越过 60.8s 冻死点或 chain 64 条新打印定位肇事槽](https://github.com/hannana-26/UniXNU-houji-ios27/blob/storage/docs/handoff-2026-11-19.md%20%28r55%20%E9%95%9C%E5%83%8F%29)
  Command: <code>gh workflow run macos.yml -R hannana-26/UniXNU -f device_repository=hannana-26/UniXNU-houji-ios27 -f device_ref=storage -f defconfig=houji_ios27_defconfig -f steps='kernel payload' -f pre_build=…(交接文档 §6);bash work/mk55.sh(CI 内核 gatecheck→panic 屏→args 重写→mk55.py)</code>. Revision: `6f80ae61a13e623f848f9b493b29050f32cb0103`.

</div>
