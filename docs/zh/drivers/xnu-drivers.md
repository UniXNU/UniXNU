# XNU 驱动

UniXNU 的 XNU 驱动是编译进内核的 C++ IOKit 类。内核把驱动作为静态库链接，并通过 `KernelConfigTables.cpp` 中的 personality 启动它。

## 源码布局

```
drivers/MyDriver/
  MyDriver.cpp
  MyDriver.h
  Info.plist
```

`Info.plist` 记录 personality 供参考。内核使用编译进 `iokit/KernelConfigTables.cpp` 的 personality。

## 驱动类

```cpp
#include <IOKit/IOService.h>
#include <IOKit/IOLib.h>
#include <libkern/c++/OSData.h>

class MyDriver : public IOService {
  OSDeclareDefaultStructors(MyDriver)

public:
  bool start(IOService *provider) override;
  void stop(IOService *provider) override;
  bool probe(IOService *provider, SInt32 *score) override;
};

OSDefineMetaClassAndStructors(MyDriver, IOService)

bool MyDriver::probe(IOService *provider, SInt32 *score)
{
  if (!super::probe(provider, score)) {
    return false;
  }
  *score = 1000;
  return true;
}

bool MyDriver::start(IOService *provider)
{
  if (!super::start(provider)) {
    return false;
  }

  OSData *reg = OSDynamicCast(OSData, provider->getProperty("reg"));
  if (reg == nullptr || reg->getLength() != 4 * sizeof(uint32_t)) {
    IOLog("MyDriver: provider has no usable reg property\n");
    return false;
  }

  registerService();
  IOLog("MyDriver: started\n");
  return true;
}

void MyDriver::stop(IOService *provider)
{
  IOLog("MyDriver: stopped\n");
  super::stop(provider);
}
```

`start()` 获取 provider，读取属性，分配资源，安装中断处理并调用 `registerService()`。

## 按内核 ABI 编译

驱动必须使用与 XNU 相同的编译参数。内核构建把每个目标文件的完整命令记录在 `.cpo.json`：

```
build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json
```

构建脚本读取记录，替换源码和输出路径，加入驱动 include 路径，然后运行编译器：

```python
import json, subprocess
from pathlib import Path

record = json.loads(Path(
  "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json"
).read_text())

command = []
i = 0
while i < len(record["arguments"]):
  value = record["arguments"][i]
  if value == record["file"]:
    command.append("drivers/MyDriver/MyDriver.cpp")
  elif value == "-o":
    command += ["-o", "build/my-driver/MyDriver.o"]
    i += 1
  elif value == "-Xclang" and record["arguments"][i + 1].startswith("-W"):
    i += 1
  elif not value.startswith("-W"):
    command.append(value)
  i += 1

command += ["-Wall", "-Wextra", "-Werror", "-I", "build/my-driver"]
subprocess.run(command, cwd=record["directory"], check=True)
```

目标文件必须满足：

| 字段 | 值 |
| --- | --- |
| Magic | `0xfeedfacf` |
| CPU type | `0x0100000c`（ARM64） |
| File type | `1`（MH_OBJECT） |
| Subtype | `0` |
| Build version | platform `2`（iOS），minimum `0x110000`（17.0） |

编译记录包含使这些值匹配内核的参数。

## 静态库

```sh
xcrun ar rcs build/my-driver/libMyDriver.a build/my-driver/MyDriver.o
```

把构建脚本加入 `board.toml` 的 `[kernel] archives`。`unixnu build kernel` 在链接内核前运行它。

## 链接进内核

在 `scripts/build-xnu-4k-baseline.sh` 中加入：

```sh
if [ "${XNU_MY_DRIVER:-0}" = 1 ]; then
  MY_DRIVER_ARCHIVE=$ROOT/build/my-driver/libMyDriver.a
  test -f "$MY_DRIVER_ARCHIVE"
  KERNEL_EXTRA_ARCHIVES="$KERNEL_EXTRA_ARCHIVES -Wl,-force_load,$MY_DRIVER_ARCHIVE"
  KERNEL_ARCHIVE_DEPENDENCIES="$KERNEL_ARCHIVE_DEPENDENCIES $MY_DRIVER_ARCHIVE"
fi
```

`-force_load` 保留每个目标文件，包括链接器会丢弃的类。把静态库加入 `KERNEL_ARCHIVE_DEPENDENCIES`，库变化时会重新链接内核。

在 defconfig 中启用：

```
CONFIG_XNU_MY_DRIVER=y
```

## 加入 personality

通过补丁把匹配字典加入 `iokit/KernelConfigTables.cpp`：

```c
#if defined(XNU_MY_DRIVER) && XNU_MY_DRIVER
    "   ,{"
    "     'IOClass'         = MyDriver;"
    "     'IOProviderClass' = IOPlatformDevice;"
    "     'IONameMatch'     = 'my-device';"
    "     'IOProbeScore'    = 1000:32;"
    "   }"
#endif
```

构建脚本把 `-DXNU_MY_DRIVER=1` 传给 `KernelConfigTables.cpo`：

```sh
EXTRA_MAKE_ARGS+=("KernelConfigTables.cpo_CFLAGS_ADD=-DXNU_MY_DRIVER=$MY_DRIVER")
```

personality 是内核 IOKit 配置表中的属性列表字符串。`IOClass` 是 C++ 类名，`IOProviderClass` 是 provider 类，`IONameMatch` 匹配 provider 名称或 `compatible` 值，`IOProbeScore` 决定多个候选的顺序。

## Provider 属性

ADT 节点在平台专家匹配后成为 `IOPlatformDevice` nub。常用属性：

| 属性 | 编码 | 用途 |
| --- | --- | --- |
| `reg` | 32 位或 64 位 cell | 寄存器窗口 |
| `interrupts` | 32 位 cell | 中断号 |
| `compatible` | 字符串列表 | 驱动匹配 |
| `name` | 字符串 | 节点名 |
| `clock-frequency` | 32 位 | 输入时钟 |
| `power-domains` | phandle | 电源依赖 |

`provider->getProperty("reg")` 返回 `OSData`，地址和大小 cell 数量来自父节点。

## 内存

| API | 用途 |
| --- | --- |
| `IOMalloc`、`IOFree` | 内核虚拟内存 |
| `IOMallocContiguous` | 物理连续内存 |
| `IOBufferMemoryDescriptor` | 带物理地址的 DMA 缓冲 |
| `IODMACommand` | 为设备映射缓冲 |

DMA 缓冲必须通过设备的 IOMMU 或 SMMU 上下文映射。`ArmSmmu4K` kit 提供 4 KiB SMMU 表。

## 中断

使用 provider 或平台的中断事件源：

```cpp
IOInterruptEventSource *source = IOInterruptEventSource::interruptEventSource(
  this, OSMemberFunctionCast(IOInterruptEventSource::Action,
  this, &MyDriver::handleInterrupt), provider, 0);

if (source == nullptr || !workLoop->addEventSource(source)) {
  return false;
}
source->enable();
```

Provider 需要发布中断控制器或中断资源。通用 ARM64 平台上 `ArmCpu` 提供 GIC 路径。

## 设备树资源

平台专家为每个 `arm-io` 子节点发布 nub。服务 `arm-io` 范围以下设备的驱动从板级常量取得物理地址。

匹配 `/product` 或 `/buttons` 的驱动使用 `IOPlatformExpertDevice` 作为 provider。

## 运行时行为

| 阶段 | 调用 |
| --- | --- |
| 匹配 | `probe()` |
| 启动 | `start()` |
| 发布 | `registerService()` |
| 停止 | `stop()` |

`start()` 失败的驱动释放资源并返回 `false`。

## 测试

| 测试 | 方法 |
| --- | --- |
| 编译 | 按记录参数使用 `-Wall -Wextra -Werror` |
| 对象 ABI | 检查 magic、CPU type、file type、subtype、build version |
| 主机逻辑 | 抽出纯函数并编译主机测试 |
| 内核启动 | QEMU 启用驱动并读取启动进度日志 |
| 硬件 | 启动设备并读取驱动日志 |

## 参考驱动

| 驱动 | 展示内容 |
| --- | --- |
| `ArmDTPlatform` | 平台专家和设备 nub |
| `ArmCpu` | CPU、GIC 和定时器 |
| `NativeUfs` | 存储、SMMU 和命令队列 |
| `NativeAES` | 带原始 ABI 的加速器子类 |
| `NativeAdreno` | GPU 电源、GMU 固件、原生 4 KiB SMMU、ring 和 user client |
| `NativeMetal` | Metal API 前端和到 Turnip 的 metal2vulkan 翻译 |

Adreno 路径见 [Adreno 740 驱动](/zh/drivers/native-adreno)。

## 完整示例

[Novatek 触控驱动](/zh/drivers/native-novatek-touch)展示完整结构：纯处理核心、总线接口后的控制器协议、带来源的板级常量、分阶段探针和 HID 发布。

## 下一步

- [kext 包](/zh/drivers/kexts)
- [设备树匹配](/zh/drivers/device-tree-matching)
- [构建内核](/zh/guide/build-kernel)
