# Sm8550Platform

Start with the [adaptation procedure](/porting/gpu) for board inputs, source changes, build integration and verification order.

SM8550 GPU platform operations: the GMU, the GPU SMMU and the RPMh command database the GPU and its power rails read.

[Source repository](https://github.com/UniXNU/UniXNU-sm8550-common).

The kit is board code, not a driver: the SoC repository supplies it and a board selects it when it enables the Adreno 740 accelerator. The GMU part brings the graphics management unit up and holds its rails; the SMMU part gives the GPU its own stage 1 translation domain; the command database part answers RPMh resource lookups by name.

## Requirements

| Requirement | Meaning |
| --- | --- |
| SoC SM8550 | The register map and the RPMh resource names are the board's own |
| GPU firmware | The GMU and the GPU microcode come from the firmware files the board provisions |
| `ArmSmmu4K` | The SMMU part programs a stage 1 context through the SMMU kit |
| `AdrenoFirmware` | The firmware loader that hands the GMU its images |

Select it in the board configuration:

```toml
[components]
include = ["Sm8550Platform", "Adreno740", "AdrenoMetal", "AdrenoFirmware", "ArmSmmu4K"]
```

The component is built into the kernel as part of the board package (`build_stage = "embedded"`). It produces no separate archive or bundle.

## Sources

| File | Contents |
| --- | --- |
| `ShengGmu.c` | GMU start, halt, memory windows, interrupt and the keepalive vote |
| `ShengGpuSmmu.c` | The GPU's SMMU context, its stage 1 tables and the fault handler |
| `ShengGmuCommandDb.c` | The RPMh command database: resource lookup by name, level and vote |

## Verification

The kit is verified through the drivers that use it: [Adreno 740](/drivers/adreno740) and [Adreno Metal](/drivers/adreno-metal) on a board that reaches the GPU. Record the GMU start result, the SMMU context and the resource votes in the board's `porting.toml` GPU area.

## Integration

```sh
./unixnu build kernel -D ../UniXNU-sheng
```

[Component catalog](/reference/components)
