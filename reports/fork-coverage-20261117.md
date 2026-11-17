# Fork source coverage

The [file table](fork-coverage-20261117.csv) compares every branch of the eight zus12873 repository networks corresponding to UniXNU repositories. Each row identifies its upstream main tree entry, fork tree entry, branches, patch and source link. The repository revisions in the table define the comparison snapshot.

| Repository | Branches including main | Distinct file differences | Fork file variants |
| --- | ---: | ---: | ---: |
| Adreno740 | 4 | 12 | 2 |
| AdrenoMetal | 15 | 68 | 43 |
| ArmCpu | 2 | 5 | 5 |
| DarwinBoot | 3 | 9 | 9 |
| UniXNU | 8 | 703 | 93 |
| UniXNU-sheng | 16 | 465 | 93 |
| UniXNU-sm8550-common | 3 | 4 | 0 |
| uefi-sheng | 7 | 21 | 4 |

The [branch table](fork-branches-20261117.csv) identifies all 58 branch revisions. The [complete file table](fork-file-inventory-20261117.csv) lists all 1,287 distinct file differences. The table lists the 249 variants changed by the fork, deduplicated by repository, path and both tree entries. Differences caused exclusively by newer upstream code are recorded in the full inventory.

The integration target is the 8 GiB sheng configuration with Android boot header v0 and the manual Shader Cache application. Main selects development `46e7cc96a284150bdf19b4a6a7890b0a8bc0ef71` with `0063-main-optimizations-on-development-46e7cc96.patch`.

`已合入` identifies merged source with recorded validation. `待设备验证` identifies input and platform sleep behavior awaiting physical validation. Each row links the relevant source and names its current implementation or PR.

The old runtime overlays contain 457 added-function references. Their remaining mappings use shared Directory permission handling for chunks, inline scaled half division, and the restored system-layer chunk reader. The chunk reader reconstructed a 300,000-byte record through the actual SystemLayer implementation and refused a writable chunk. Its device capture retained complete widget and Settings backgrounds and returned to fastboot. The complete macOS CI build passed: [43978179270](https://github.com/UniXNU/UniXNU-sheng/actions/runs/43978179270). Source: [AdrenoMetal #53](https://github.com/UniXNU/AdrenoMetal/pull/53), [UniXNU #290](https://github.com/UniXNU/UniXNU/pull/290).

Generate the complete inventory with:

```sh
python3 scripts/audit-fork-branches.py \
  --repositories /path/to/repository-paths.json --owner zus12873 \
  --fetch --output /path/to/audit
```

The repository-paths file maps repository names to local checkouts. `--review` accepts JSON rows containing `id`, `decision` and `reason`; annotations follow the exact file variant. Output includes `branches.csv`, `files.csv`, `fork-files.csv`, `commits.csv`, `audit.json` and full patches under `diffs/`.


## Runtime policy audit

Run the AdrenoMetal source audit against the selected core, translator and Mesa checkouts:

```sh
python3 /path/to/AdrenoMetal/tools/audit-runtime-fast-paths.py \
  --core /path/to/UniXNU --translator /path/to/metal2vulkan \
  --mesa-source /path/to/mesa --output /path/to/runtime-fast-paths.json
```

`--runtime-policy /path/to/runtime-policy.log` attaches the captured device profile and runtime check results. The report enumerates policy fields, consumer overrides, owning source references, Turnip options and the math vocabulary defined by `Math::float_stems()`, `BinOp::ALL` and `PrecisionNote`. The development `be905fd8` source audit resolved all 25 policy fields and 19 Turnip options.

The driver-condition inventory enumerates every variant of `DriverDeviation`, `DriverWorkaround` and `DriverFact`, with declaration lines and qualified source references. Development `46e7cc96` declares 35 deviations, 28 workarounds and 46 facts. All 26 runtime policy defaults and 19 Turnip options are resolved, including `QueueTurnPolicy::Fair` and the measured view-selection conditions `UniformBufferPerLaneReadsSerialize` and `ExternalUniformReadsSkipACache`.
