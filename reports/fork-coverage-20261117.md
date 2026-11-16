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

The full inventory contains 58 branches and 1,287 distinct file differences. The table lists the 249 variants changed by the fork, deduplicated by repository, path and both tree entries. Differences caused exclusively by newer upstream code are recorded in the full inventory.

The integration target is the 8 GiB sheng configuration with Android boot header v0 and the manual Shader Cache application. Main's effective Metal runtime patch is `0046-main-optimizations-on-development-555b13d5.patch`. Its half-division implementation already normalizes divisors outside 2^-14 through 2^14, scaling both operands by 1024 or 0.25. The corresponding native-half-division-range acceptance case remains in main.

`待修复后验证` marks platform sleep and dependent code whose resume and dark-wake handling require correction before device validation. `随上游整合核对` marks older complete runtime overlays whose effects must be compared with the effective current overlay and the full development merge. The remaining decisions distinguish current main implementations, selected input changes, independent inspection tools and implementation-based documentation updates.

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

`--runtime-policy /path/to/runtime-policy.log` attaches the captured device profile and runtime check results. The report enumerates policy fields, consumer overrides, owning source references, Turnip options and the math vocabulary defined by `Math::float_stems()`, `BinOp::ALL` and `PrecisionNote`. The development `39dc6585` source audit resolved all 25 policy fields and 19 Turnip options.
