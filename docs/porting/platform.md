# Platform, memory and OS services

Start with a [resolved device repository](/porting/steps). Read the
[device-tree bindings](/porting/device-tree), [matching rules](/drivers/device-tree-matching),
[ArmDTPlatform](/drivers/arm-dt-platform) and [ArmCpu](/drivers/arm-cpu).

Use [driver build integration](/porting/drivers#build-integration) to connect
initialization, archive recipes and the OS ABI, then run this page's hardware checks.

## Sources and interfaces {#source-map}

These links identify reviewed source revisions. Match interfaces to the selected
SoC, component and OS versions. The linked device sources provide board integration
examples.

| Implementation | Source | What to read and implement |
| --- | --- | --- |
| Platform matching | [ArmDTPlatform.cpp](https://github.com/UniXNU/ArmDTPlatform/blob/417ff95d6a6e8607ddea9309ec45c3bfd4a67c60/ArmDTPlatform.cpp#L33) | `ArmDTPlatform`: ADT root, child nubs and NVRAM publication |
| CPU and interrupts | [ArmCpu.cpp](https://github.com/UniXNU/ArmCpu/blob/9066b53bbc82e92a98ec44a11dd50fd13eaf1a1b/ArmCpu.cpp#L48) | `ArmCpu`: CPU registration, timer/GIC setup, secondary entry and IPI delivery |
| DMA translation | [ArmSmmu4K.h](https://github.com/UniXNU/ArmSmmu4K/blob/8bb168ad058c28d5c04f179ba407875eacba7ef3/ArmSmmu4K.h), [ArmSmmu4KContext.h](https://github.com/UniXNU/ArmSmmu4K/blob/8bb168ad058c28d5c04f179ba407875eacba7ef3/ArmSmmu4KContext.h) | Table allocation, mappings and context programming; match the target SMMU generation |

## 1. Describe CPU and interrupt resources

Record CPU MPIDR affinities, boot CPU, enabled cores, PSCI method, GIC revision,
distributor/redistributor ranges and stride, timer frequency and interrupt specifiers.
Put shared topology in the SoC DTSI and board enablement in the board DTS.

From the main checkout, compile the target board DTS with the checked-out SoC
include directory. Set the two paths first:

```sh
SOC_DTS=/path/to/UniXNU-soc-common/dts
BOARD_DTS=/path/to/UniXNU-device/dts/board.dts
dtc -I dts -O dtb -i "$SOC_DTS" -o /tmp/board-hardware.dtb "$BOARD_DTS"
dtc -I dtb -O dts /tmp/board-hardware.dtb
```

Inspect `reg`, `ranges`, phandles, interrupt providers and disabled nodes.
Generate the OS properties through [ADT conversion](/porting/device-tree). Trace
each property to its platform-source consumer and match name, byte order and width.

**Expected result:** the platform expert publishes the intended nubs, the boot
CPU receives timer interrupts, and each enabled secondary CPU reaches its entry
and receives IPIs. On another GIC or PSCI interface, review ArmCpu's implementation
before enabling additional cores.

### Efficiency and performance clusters {#clusters}

On a SoC with two core types, tag every CPU node in the board DTS with
`unixnu,cluster-type = "E"` or `"P"`. The ADT then carries each CPU's
`cluster-type`, and a scheduler patch runs XNU's Edge scheduler with one E and
one P cluster. The SM8550 reference:

| Input | Reference value |
| --- | --- |
| E cluster | cpu0 to cpu2 (Cortex-A510) |
| P cluster | cpu3 to cpu7 (Cortex-A715, A710 and X3) |
| DTS | [`dts/sheng.dts`](https://github.com/UniXNU/UniXNU-sheng/blob/main/dts/sheng.dts) |
| Scheduler patch | [`patches/xnu/zzyf-sheng-amp.patch`](https://github.com/UniXNU/UniXNU-sheng/blob/main/patches/xnu/zzyf-sheng-amp.patch) |

The patch keeps UI threads on the P cluster. Check the result with the CPU
governor's per-domain busy share: UI work should load the P domains.

## 2. Account for memory and DMA

Compare firmware RAM, secure carveouts, framebuffer, DSP/GPU firmware, payload
and kernel allocations. The hardware DTS uses a contiguous handoff RAM range;
the loader's owned-memory request has its own size and alignment constraints.
Keep both consistent with the actual UEFI memory map.

For each DMA device, record address width, physical-to-IOVA mapping, SMMU
instance/stream/context ownership and cache policy. Read [ArmSmmu4K](/drivers/arm-smmu4k)
where its translation model matches the target. GPU, UFS, SPI and PCIe may use
different streams and allocation policies. Trace the consumer's MMIO and mapping inputs to DTS properties or board constants.

**Expected result:** every handoff allocation has a defined owner, and each
peripheral can access its allocated DMA range before it submits work.
Continue with [UFS adaptation](/porting/ufs) for the storage controller.

## 3. Connect block and OS services {#block-and-os-services}

| Component | Adaptation work | Expected observation |
| --- | --- | --- |
| [RamBlock](/drivers/ram-block) | Match dense/packed Data format and ADT placeholders. Implement the `native_ufs_store` persistence callbacks for the target storage policy | Data mounts; writes and restart behavior match the selected persistence mode |
| [VirtioMmioBlock](/drivers/virtio-mmio-block) | Supply a VirtIO MMIO device, queues, DMA and interrupt routing; qualify storage ABI bindings | Capacity and reads are correct before mounting root |
| [VerifiedRoot](/drivers/verified-root) | Supply the selected image's owner policy and trust inputs; connect the storage policy archive | Policy validation succeeds for the intended image |
| [SoftwareAES](/drivers/software-aes) | Match XNU AES helpers and IOCryptoAcceleratorFamily ABI; build its bindings for the OS profile | The crypto service publishes and required volume operations complete |
| [AppleKeyStoreState](/drivers/apple-key-store-state) | Qualify selectors and state callbacks against the OS; connect initialization and event callers | Required state queries and notifications complete |
| [XnuPrelink](/drivers/xnu-prelink) | Select matching XNU, original kernelcache, archive bindings and patch order | Prelink resolves the selected drivers and produces the kernel |
| [DarwinBoot](/drivers/darwin-boot) | Include the loader in firmware or payload; provide Mach-O, ADT and selected sidecars | Loader validates the inputs and reports kernel handoff |
| [ShengPreflight](/drivers/sheng-preflight) | Read its board checks, then write checks for the target's firmware and memory layout | Target-specific firmware inputs pass their checks |

Use [prelink](/concepts/prelink), [integrity policy](/concepts/security),
[payload](/concepts/payload) and [userdata](/guide/userdata) for the required
artifacts. Keep root UUID, partition geometry, Data persistence and log allocation
in the device configuration. The OS profile supplies its version-specific ABI.

## 4. Check the assembled selection

From the main checkout:

```sh
./unixnu status --json
./unixnu build kernel
```

Inspect dependency order, configuration fragments and patch series before the
build. Each selected archive needs its OS inputs and initialization caller.
The [kernel guide](/guide/build-kernel) describes build outputs and failures.

Record source/build evidence separately from device results in the
[porting record](/porting/records). Next, complete [storage](/porting/ufs), then
[display and brightness](/porting/display).
