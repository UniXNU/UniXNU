# 补丁参考

格式 2 按 `[kernel] patch_series` 声明顺序应用配置层和组件补丁。`unixnu status --json` 显示最终序列。补丁后的 XNU 源码保存在目标独立的 `tree/.cache/xnu-work/`。

补丁按名称顺序应用 `patches/xnu/*.patch` 和 `kits/XnuPrelink/patches/*.patch`。后置补丁 `zzw-*`、`zzy-*` 和 `zzz-*` 最后应用。

## 构建与工具链

| 补丁 | 作用 |
| --- | --- |
| `apple-only-cpu-tunables` | 仅在 `APPLE_ARM64_ARCH_FAMILY` 应用 Apple CPU tunables |
| `cxx-flag-dependencies` | Makefile 模板把 `CFLAGS` 传给 C++ 目标 |
| `external-archive-dependencies` | 外部静态库变化时重新链接内核 |
| `kernel-sdk-root` | 分离 `KERNEL_SDKROOT` 与 `SDKROOT` 并加入 include 路径 |
| `local-availability` | 允许 `XNU_AVAILABILITY_PL` 指向本地 `availability.pl` |
| `public-entitlements-header` | 加入浏览器 entitlement 名称并使用 `CoreEntitlements` |
| `source-machine-layer` | 加入 `CONFIG_APPLE_AMCC` 并调整 BCM2837 配置和文件列表 |
| `disabled-deferred-reclaim` | 去掉破坏构建的未使用参数 |
| `published-freezer-condition` | 修正 freezer 默认值的预处理条件 |

## 平台与 CPU

| 补丁 | 作用 |
| --- | --- |
| `architectural-timer-entry` | 启用原生架构定时器时跳过 BCM2837 定时器路由 |
| `armvirt-platform-personality` | 加入 `ArmCpu`、`ArmVirtPlatform` 和 `ArmDTPlatform` personality |
| `native-smp-secondary` | `MAX_CPUS` 提高到 8，BCM2837 secondary CPU 使用 MPIDR Affinity1 |
| `native-arm-pan` | 设置 `XNU_NATIVE_PAN` 时启用 ARMv8.1 PAN |
| `native-dt-panic-region` | 从设备树读取并校验 panic 日志区域 |

## 4 KiB 页

| 补丁 | 作用 |
| --- | --- |
| `native-4k-bootstrap-capacity` | 为 4 KiB 映射调整 bootstrap 页表池，并在溢出前停止 |
| `native-4k-user-abi` | 为用户 map、commpage 和 shared region 设置 4 KiB shift |
| `native-4k-signature-hash-cache` | 从已验证 16 KiB 块派生 4 KiB 代码签名哈希 |
| `pgz-aligned-validation` | 对齐检查前解码 PGZ 地址 |
| `zzx-pmap-sync-64bit-pa` | 用 `ptoa()` 保留 4 GiB 以上物理地址 |
| `non-apple-pmap-field` | 匹配非 PAC pmap 字段布局 |
| `non-apple-iommu-bootstrap` | 保护 UAT 和 SART bootstrap 及 PPL 代码 |
| `non-apple-cache-monitor` | 保护 monitor enable 并导出 cache clean 符号 |

## 安全与 owner root

| 补丁 | 作用 |
| --- | --- |
| `native-trust-cache-runtime` | 在 BCM2837 初始化 trust cache 运行时 |
| `source-corecrypto14-bootstrap` | 早期启动时注册源码 corecrypto |
| `source-pthread-bootstrap` | 早期启动时注册源码 pthread |
| `native-aes-personality` | 加入 AES、VirtIO 块、VirtIO 控制台、RAM 块和 UFS personality |
| `offline-owner-root-crypto-probe` | 设置 `offline-owner-root-check` 时启动 verified root 探针 |
| `offline-owner-root-binding-audit` | 比较挂载根设备和 verified root 设备 |
| `offline-owner-boot-manifest` | 从根和 cache 设备发布 owner 启动 manifest 哈希 |
| `offline-owner-cache-carrier` | 选择 owner dyld cache 载体并校验设备和路径 |
| `offline-owner-systemos-mount` | 挂载 SystemOS cryptex 并用 owner cache 组合根 |
| `offline-owner-z-air-init` | 初始化 owner root 的 Z air 路径 |
| `offline-legacy-start` | 在 `IOKitBSDInit` 后启动 legacy display 探针 |
| `offline-component-load-probes` | 加载 APFS、IOGPU 和 mobile graphics 组件并记录检查点 |
| `offline-native-gpu-broker` | DTrace 初始化后发布离线 GPU broker |
| `sheng-platform-power` | 日历初始化前运行板级 PMGR 集成 |

## 图形与显示

| 补丁 | 作用 |
| --- | --- |
| `offline-native-gpu-broker` | 启动离线 GPU broker |
| `zzy-native-gpu-addon-mount` | 为 GPU addon 内容和启动任务挂载只读 union 视图 |
| `zzw-native-adreno-sandbox-grant` | 让 Adreno740 在 `NativeSandboxGrantProcess` 中指定 render server，并使其 user client 通过沙箱打开 |
| `native-aes-personality` | 注册存储和控制台 personality |

## 诊断

| 补丁 | 作用 |
| --- | --- |
| `offline-pgz-alignment-probe` | 加入 PGZ 分配探针和检查点 |
| `native-work-interval-trace` | 记录最近的 work interval 结果供启动进度页显示 |
| `native-quiet-managed-page-report` | 关闭 GPU buffer 和 scanout mapping 上的 DEVELOPMENT managed page 报告 |
| `zzz-boot-progress` | 在内核启动路径加入启动进度检查点 |

## 行为修复

| 补丁 | 作用 |
| --- | --- |
| `native-priv-work-interval` | 在策略评估前授予 `PRIV_WORK_INTERVAL` |
| `native-work-interval-soft-fail` | 被拒绝的 CA client work interval 软失败 |
| `native-union-getattrlistbulk` | 批量目录读取继续到 union 下层目录 |
| `native-union-statfs-fsid` | 对覆盖在根卷上的 union，`statfs64` 报告根卷的文件系统编号 |
| `null-root-media` | 处理 `IOService::setRootMedia` 的空 root |
| `published-freezer-condition` | 修正 freezer 默认条件 |

## Mockfs

| 补丁 | 作用 |
| --- | --- |
| `mockfs-intermediate-lookup` | 允许非最后分量的查找 |
| `mockfs-memory-device-width` | legacy ioctl 无法表达 64 位地址时使用设备路径 |
| `mockfs-statfs` | 实现 `vfs_getattr` |
| `mockfs-typed-allocation` | `kalloc_type` 和 `kfree_type` 使用结构体类型 |
| `mockfs-test-file` | 在测试文件系统中加入 `launchd` 和 `probe.bin` |

## 预链接补丁

`kits/XnuPrelink/patches/`：

| 补丁 | 作用 |
| --- | --- |
| `xnu-10063.141.1-security-init.patch` | 加入早期安全初始化入口 |
| `xnu-10063.141.1-sparse-index.patch` | 加入稀疏预链接索引 ABI |

## 新增补丁

1. 编辑 `.cache/xnu-work`。
2. 用 `git diff` 生成补丁。
3. 以正确的顺序命名并放入 `patches/xnu/`。
4. 重新构建内核。

依赖其他补丁的补丁排在其后。修改 `zzy` 或 `zzz` 区域的补丁排在其前。

## 下一步

- [源码与补丁](/zh/xnu/source-and-patches)
- [4 KiB 页表](/zh/xnu/four-k-page-tables)
- [构建内核](/zh/guide/build-kernel)
