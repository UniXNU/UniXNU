# 完整性与启动策略

UniXNU 保留原始 Apple 安全组件，并提供它们检查的输入。源码内核加入这些组件所需的平台代码，启动负载提供描述设备的 trust cache 和设备树属性。

## 输入

| 输入 | 提供方 |
| --- | --- |
| trust cache 包 | `--trust-cache FILE` |
| trust cache 哈希 | `[payload] trust_cache_sha256` |
| 平台种子 | `--unique-chip-id HEX` |
| 设备树身份 | 格式 2 的带类型 `[adt]` 表；格式 1 的板级脚本 |
| PMGR 集成 | 需要时使用 `XNU_SHENG_PMGR` |
| 根策略 | `XNU_VERIFIED_ROOT_PROBE`、`XNU_OWNER_ROOT_AUDIT`、`XNU_OWNER_ROOT_TRUST` |

## trust cache

DarwinBoot 校验 trust cache 包结构，并把它复制到内核窗口。ADT 的 `/chosen/memory-map/TrustCache` 占位符接收地址和大小。

补丁 `native-trust-cache-runtime` 在 `BCM2837` 上初始化运行时 trust cache 路径。原始 AppleImage4 和 AMFI 组件按缓存校验代码。

负载步骤只接受 SHA-256 位于 `[payload] trust_cache_sha256` 的 trust cache 包。

## 4 KiB 下的代码签名

原始 CodeDirectory 使用 16 KiB 哈希页。4 KiB 内核校验 4 KiB 页。补丁 `native-4k-signature-hash-cache`：

1. 通过 `vn_rdwr` 读取每个原始 16 KiB 块。
2. 用原始 CodeDirectory 哈希校验该块。
3. 从已验证块派生每个 4 KiB 页的哈希。
4. 把派生哈希存入只读内核内存。
5. 让 `cs_validate_page` 使用派生表。

只有原始 16 KiB 哈希匹配后，块才会发布。校验失败的块不产生派生表，页校验返回 `CS_VALIDATE_TAINTED`。

## AMFI 策略

ADT 属性 `/chosen/amfi-only-platform-code` 让 AMFI 保持在平台代码策略。`[kernel.prelink] early_security_init` 在指定地址运行原始 `AppleMobileFileIntegrity` 初始化器。

`offline-owner-root-*` 补丁为首次启动加入 owner root 检查：

| 补丁 | 功能 |
| --- | --- |
| `offline-owner-root-binding-audit` | 用启动 manifest 检查根绑定 |
| `offline-owner-root-crypto-probe` | 检查 owner crypto provider |
| `offline-owner-boot-manifest` | 记录启动 manifest 哈希 |
| `offline-owner-cache-carrier` | 选择代码签名缓存载体 |
| `offline-owner-systemos-mount` | 挂载 SystemOS cryptex |
| `offline-owner-z-air-init` | 初始化 owner root 的 Z air 路径 |

## 用户应用安装

sheng 的 iPadOS 27.0.1（24A446）运行环境将
[AppSync Unified](https://github.com/akemin-dayo/AppSync) 的安装验证与
FrontBoard 启动处理机制应用于所有用户应用包。没有应用名单、bundle ID 白名单或
构建时的可执行文件哈希登记；新增应用和更新版本均无需重新构建启动镜像。

保留当前 Data seed 和固件输入，从 UniXNU 目录构建一次：

```sh
./unixnu build kernel payload -D ../UniXNU-sheng
./unixnu bootimg -D ../UniXNU-sheng
```

启动此镜像后，将 IPA 传入设备，通过 MobileInstallation 安装，例如：

```sh
/usr/libexec/unixnu-appinst /path/on/device/Example.ipa
```

无签名、伪签名和证书过期的包均在设备端处理。安装 hook 先调用原始验证器；
验证拒绝时，用在 installd 进程内运行的内置 ldid 库在安装副本中自动修复签名，保留 entitlements，重建资源封套、
移除过期 provisioning profile，再次验证。原始 IPA 保持不变。

安装 hook 启用原生 ad-hoc 路径，关闭预加载 trust cache 哈希和在线授权要求，
并跳过 provisioning profile ID 验证。FrontBoard 信任用户应用包。范围按位置判断：
Data 上 `/private/var/` 或 `/var/` 下的 `.app` 目录树，覆盖安装暂存目录、嵌套框架和
应用扩展。系统路径沿用原生处理。

`sheng-appsync-user-trust.patch` 在 XNU 加载这些目录内代码的签名时自动登记
CodeDirectory 哈希，时机在签名结构验证之后、原始 AMFI 签名回调之前。
它使用 owner 启动模块已有的 engineering trust cache 接口，在运行时锁下去重，
信任条目保留到本次启动结束。重启后，应用映射代码时会重新登记。
启动 payload 仍包含运行库和系统程序副本的信任哈希，用户应用不再是构建输入。
进入 trust cache 后，AMFI 会把这些可执行文件报告为平台二进制；exec 为用户 `.app`
的主可执行文件清除这一身份，应用以普通第三方进程运行。

`payload.runtime.appsync = true` 选择此功能；`--kernel-arg appsync=0` 同时禁用
挂载和自动信任登记。每次启动最多分配 65536 个动态模块，登记失败会报错。
自动签名后仍会校验签名结构、资源和可执行页面哈希。不提供 FairPlay 解密或
App Store 账户授权；应用仍须兼容目标 iOS 环境。

`runtime/appsync-service.json` 记录 `scope = "all-user-bundles"` 及运行库文件哈希。
主机测试覆盖未登记应用、版本更新、嵌套包、并发登记、关闭功能和失败后的资源释放，
并验证无签名代码、伪签名及过期证书、资源与 profile 修复和 entitlements 保留。
在 sheng 上，无签名的 arm64 应用可通过 USB 安装、启动，并在重启后保留。源码和测试说明见 `scripts/appsync/README.md`。

## GPU client 授权

Adreno740 在加速器服务上发布 `NativeSandboxGrantProcess`。补丁 `zzw-native-adreno-sandbox-grant` 把打开进程的名称与该属性比较，指定进程可以绕过 `mac_iokit_check_open_service` 和 `mac_iokit_check_open` 打开 user client。render server 就是该指定进程。

## verified root

`kits/VerifiedRoot` 提供签名的策略包。verified block 驱动按策略校验每次读取。策略可以按容量用 `--verified-root-bundle` 选择。

| 工具 | 功能 |
| --- | --- |
| `verified_root.c` | 策略解析和读取校验 |
| `xnu_crypto.c` | XNU crypto 适配 |
| `manifest.py` | 策略包构建 |
| `verify_image.py` | 镜像校验 |

## 存储完整性

`VirtioMmioBlock` 和 `RamBlock` 共用 verified block 策略。构建脚本检查两个传输层导入相同的原始存储绑定，并检查编译对象与记录哈希一致。

## 报告

负载报告记录：

| 字段 | 含义 |
| --- | --- |
| `kernel_sha256` | 输入内核 |
| `payload_kernel_sha256` | 负载中的内核，经过可选 panic 屏幕补丁 |
| `adt_sha256` | ADT sidecar |
| `trust_cache_sha256` | trust cache 包 |
| `data_ramdisk_sha256` | Data 种子 |
| `payload_sha256` | 负载镜像 |

启动管理器日志记录暂存的 kext、安装的 ACPI 表和注入的驱动。

## 下一步

- [启动负载](/zh/concepts/payload)
- [补丁参考](/zh/xnu/patch-reference)
- [启动参数](/zh/xnu/boot-arguments)
