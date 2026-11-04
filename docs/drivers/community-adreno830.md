# Adreno830

Adreno 830 (Gen8) kernel GPU driver for the OnePlus 13T (PKX110, SM8750), started from Adreno740 `5c8c145`. It brings up the GMU, CP and SMMU and serves the accelerator interfaces that AdrenoMetal, metal2vulkan and Turnip use.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [Adreno830](https://github.com/Shad0w23333/Adreno830) | [Shad0w23333](https://github.com/Shad0w23333) | Adreno 830 kernel GPU driver for the OnePlus 13T (PKX110, SM8750). Its board inputs are in the device repository [Shad0w23333/UniXNU-Pagani_SM8750](https://github.com/Shad0w23333/UniXNU-Pagani_SM8750). |

## State

OnePlus 13T, iPadOS 17.7.11 (21H461), 2026-10-30 to 2026-11-01: the driver runs the desktop through Metal on hardware; system apps, widgets and Control Center render. Host tests: 45 passed, 1 skipped. See [docs/PROGRESS.md](https://github.com/Shad0w23333/Adreno830/blob/main/docs/PROGRESS.md).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
