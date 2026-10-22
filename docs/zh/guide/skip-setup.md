# Skip Setup

全新的 Data 种子首次启动会进入 Setup。负载可以在写镜像前把 Setup 标记为完成，让设备直接进入 SpringBoard。

## 命令

```sh
./unixnu build payload \
  --data-ramdisk data.dbr \
  --skip-setup \
  --trust-cache trustcache.img \
  --unique-chip-id <hex>
```

`--skip-setup` 需要 `--data-ramdisk`。负载步骤读取板级文件中的 `[payload] skip_setup_tool`，并在种子副本上运行。

```toml
[payload]
skip_setup_tool = "scripts/seed-data-skip-setup.py"
skip_setup_args = ["--no-auto-dim"]
```

`skip_setup_args` 可选，接在两个路径参数之后传给工具。原始种子保持不变。负载使用修改后的副本作为 `Payloads/scratch-data.img`。

平板存储大于种子时，先用 `scripts/seed-data-grow.py` 增长种子。负载编辑增长后的种子并保留其大小。

## 工具修改的内容

`scripts/seed-data-skip-setup.py` 展开打包的 APFS Data 种子，以读写方式挂载，把偏好合入 `/private/var/mobile/Library/Preferences`，然后重新打包。

| 偏好文件 | 值 |
| --- | --- |
| `com.apple.purplebuddy` | `SetupDone = true`、`SetupFinishedAllSteps = true`、`SetupVersion = 11`、`daemonizeNeedsToRun = false` |
| `com.apple.purplebuddy.notbackedup` | 所有 mini-buddy 标志设为 `false`：diagnostics、HSA2、keychain sync、Mesa、payment、standard、silent ICDP |
| `com.apple.managedconfiguration.notbackedup` | `LockdownActivationIndicatesCloudConfigurationAvailable = false` |
| `com.apple.springboard` | `BKNoWatchdogs = true`、`FBLaunchWatchdogExceptions = { com.apple.purplebuddy: 100 }`、`MCForceShowCloudConfigurationUI = false` |
| `com.apple.migration` | `LastSystemVersion = 21H461`、`DMUserDataDisposition = { SyntheticDidUpgrade = false, buildVersion = 21H461 }` |

`--no-auto-dim` 还会在 `com.apple.springboard` 里设置 `SBDisableAutoDim`、`SBDontDimOrLockOnAC` 和 `SBDisableIdleSleep`，与 UniXNU-qemu 的根文件系统构建脚本相同。没有按键或空闲计时不可用的板子，否则会在 SpringBoard 启动约 30 秒后关闭屏幕并让系统休眠。

工具还会在 `/private/var/containers` 下创建目录：

```
Bundle
Data/System
Shared/SystemGroup
Temp
```

卷 UUID 保持不变。修改后再次检查 APFS 容器 magic。

## 构建版本

脚本设置：

```python
BUILD, VERSION = '21H461', '17.7.11'
```

板级目标换成其他 iOS build 时，同时更新这两个值。`LastSystemVersion` 和 `DMUserDataDisposition.buildVersion` 必须与 IPSW 一致。

## 设备树

使用 `--ipad-identity` 时，ADT 会加入四个 `/chosen` 属性：

| 属性 | 值 |
| --- | --- |
| `certificate-production-status` | `0` |
| `effective-production-status-ap` | `0` |
| `certificate-security-mode` | `1` |
| `effective-security-mode-sep` | `1` |

这些属性描述一个 dev-fused、未 demote 的板子。`mobileactivationd` 通过 MobileGestalt 读取它们，在没有激活记录时走原生激活路径。其他身份属性和缓存答案见 [MobileGestalt 身份](/zh/guide/mobilegestalt)。

## 任务

Setup 依赖的服务在这个平台上不运行。板级文件用启动参数停掉它们：

```
sheng-disable-jobs=com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.iconservices.iconservicesagent
```

`com.apple.CommCenter` 是蜂窝服务。列表是板级配置。保留用户态需要的服务，移除阻塞首次启动的服务。

## 输出

负载目录包含：

```
out/<board>/payload/data-skip-setup-<hash>.dbr
out/<board>/payload/payload.img
out/<board>/payload/payload.json
```

`payload.json` 记录：

| 字段 | 含义 |
| --- | --- |
| `data_ramdisk_sha256` | 修改后种子的哈希 |
| `skip_setup` | `true` |
| `payload_sha256` | 负载镜像哈希 |

修改后的种子按原始种子和 `skip_setup_args` 的哈希缓存。换一个种子或换一组参数会生成新文件。

## 验证

1. 用 `--skip-setup` 构建负载。
2. 检查 `payload.json` 的 `"skip_setup": true`。
3. 启动镜像。
4. 日志到达 SpringBoard，不再停留在 Setup 页面。

参考实现是本仓库的 `scripts/seed-data-skip-setup.py`。sheng 移植记录了使用这些改动的首次硬件启动。

## 下一步

- [启动镜像](/zh/guide/boot)
- [userdata 镜像](/zh/guide/userdata)
- [启动负载](/zh/concepts/payload)
