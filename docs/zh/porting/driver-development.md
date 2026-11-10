# 开发驱动

[组件目录](/zh/reference/components)中没有适用于该硬件的实现时，编写新驱动。先定义它的
[接口边界](/zh/porting/drivers)。构建示例在 `./unixnu tree` 报告的组装目录中执行。

## 1. 选择层次 {#layer}

| 需求 | 层次 | 构建产物 | 加载方 |
| --- | --- | --- | --- |
| XNU 之前的显示、输入或存储 | UEFI 驱动 | EDK II `.efi` | 固件 dispatch、`unixnu.toml` 的 `[[driver]]` 或 kit |
| XNU 内的平台、CPU、存储、显示、GPU 或其他服务 | 内置 XNU 驱动 | 链接进内核的静态归档 | 内核启动时 |
| 由外部加载器验证并注入的 bundle | Kext 包 | `.kext` | 接受 kext 请求的加载器。随附的 DarwinBoot 启动预链接内核 |

## 2. 匹配 provider {#matching}

`ArmDTPlatform` 为 ADT 中每个 `arm-io` 子节点发布一个 `IOPlatformDevice` nub。
驱动通过 IOKit personality 绑定：

| 键 | 含义 |
| --- | --- |
| `IOClass` | 驱动类 |
| `IOProviderClass` | provider 类：SoC 设备用 `IOPlatformDevice`，`/product` 和 `/buttons` 用 `IOPlatformExpertDevice`，全局服务用 `IOResources` |
| `IONameMatch` | provider 名称或某个 `compatible` 值 |
| `IOPropertyMatch` | 精确匹配的 provider 属性值 |
| `IOResourceMatch` | probe 前必须存在的资源，例如 `IOBSD` |
| `IOProbeScore` | 分数高者先 probe |
| `IOMatchCategory` | 允许第二个驱动匹配同一 provider |

内置驱动的 personality 通过补丁加入 `iokit/KernelConfigTables.cpp`，并由驱动的内核开关控制：

```c
#if defined(XNU_MY_DRIVER) && XNU_MY_DRIVER
    "   ,{"
    "     'IOClass'         = MyDriver;"
    "     'IOProviderClass' = IOPlatformDevice;"
    "     'IONameMatch'     = 'vendor,my-device';"
    "     'IOProbeScore'    = 1000:32;"
    "   }"
#endif
```

节点的 `compatible` 和 `unixnu,adt-name` 来自板级 DTS，见[设备树](/zh/porting/device-tree)。
格式 2 的 `reg` 属性是一组小端 u64 地址与大小对。

## 3. 编写驱动类 {#driver-class}

```cpp
class MyDriver : public IOService {
  OSDeclareDefaultStructors(MyDriver)
public:
  IOService *probe(IOService *provider, SInt32 *score) override;
  bool start(IOService *provider) override;
  void stop(IOService *provider) override;
};
OSDefineMetaClassAndStructors(MyDriver, IOService)

bool MyDriver::start(IOService *provider)
{
  if (!IOService::start(provider)) return false;
  OSData *reg = OSDynamicCast(OSData, provider->getProperty("reg"));
  if (reg == nullptr || reg->getLength() != 2 * sizeof(uint64_t)) return false;
  registerService();
  return true;
}
```

`start()` 读取 provider 属性，映射寄存器，通过设备的 SMMU 上下文分配 DMA 缓冲，
安装中断源并调用 `registerService()`。`start()` 失败时释放已取得的资源并返回 `false`。

## 4. 按内核 ABI 编译 {#compile-against-the-kernel-abi}

内核构建把每个目标文件的完整编译命令记录在 `.cpo.json` 文件中，例如：

```
build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json
```

驱动配方读取一条记录，替换源文件和输出路径，加入自己的 include 路径后运行编译器。
生成的目标文件与所选内核的架构、平台和部署版本一致。继承或调用原始 kernelcache 中的类时，
还需要该构建的类布局、虚方法槽位和符号绑定，并按所选 OS profile 的 kernelcache 核对。
每个 OS profile 各有一份。

## 5. 链接进内核 {#link-into-the-kernel}

1. 把目标文件归档，例如 `build/my-driver/libMyDriver.a`。
2. 把配方放进设备仓库的 `scripts/`，按依赖顺序加入 `[kernel] archives`，并设置
   `CONFIG_XNU_BUILD_ARCHIVES=y`。
3. 在 defconfig 中把归档加入内核链接：

   ```
   CONFIG_XNU_EXTRA_LD_ARCHIVES="-Wl,-force_load,{tree}/build/my-driver/libMyDriver.a"
   ```

   `-force_load` 保留全部目标文件，包括没有被引用的类。
4. 启用控制 personality 的开关：在 defconfig 中设置 `CONFIG_XNU_<NAME>=y`，由
   `scripts/build-xnu-4k-baseline.sh` 读取，并以 `-DXNU_<NAME>=1` 传给
   `KernelConfigTables.cpo`，见[构建内核](/zh/guide/build-kernel)。
   板级主动启动的服务改为由板级初始化调用。
5. 从主仓库运行 `./unixnu build kernel`，检查 `logs/` 下的归档日志和预链接报告。

可复用的驱动应成为组件：建立仓库并在 `components.toml` 中加入条目，写明 `build`、
`outputs`、依赖和 OS ABI，再用 `component:<ID>` 选择。

## 6. 添加 UEFI 驱动 {#uefi-driver}

UEFI 驱动是带 INF 的 EDK II 模块，并列入 DSC。

| 位置 | 构建 | 加载 |
| --- | --- | --- |
| 固件卷 | 把 INF 加入固件 DSC 和 FDF，再运行 `./unixnu build firmware` | 固件 dispatch |
| Payload | 构建独立 `.efi` | `unixnu.toml` 或 kit 中的 `[[driver]]`，见[启动配置](/zh/reference/boot-configuration) |

驱动以 load options 的形式收到其 `[[driver]]` 条目的 `args`。`connect = true`
在驱动启动后对每个 handle 执行 `ConnectController`。DSC 和 FDF 的写法见
[固件集成](/zh/porting/uefi-firmware)。

## 7. 验证 {#verify}

| 检查 | 方法 |
| --- | --- |
| 编译 | 在记录的编译选项之上加 `-Wall -Wextra -Werror` |
| 归档 | `llvm-ar t` 和 `llvm-nm --defined-only` 显示目标文件和启动符号 |
| 主机逻辑 | 把与硬件无关的函数编译为主机测试 |
| 设备 | 启动后通过[日志抓取](/zh/porting/log-capture)读取驱动的启动日志行 |

把结果写入 [porting.toml](/zh/porting/records) 的对应范围，再回到[适配顺序](/zh/porting/drivers)。
