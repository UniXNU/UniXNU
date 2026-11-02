# Device porting records

Format 2 device repositories maintain `porting.toml`. Maintainers and agents
update this record throughout development. The documentation site generates
device pages from its pinned source snapshots.

## Procedure {#procedure}

1. Create the record from `examples/device/porting.toml`, or edit the existing device record. Match its identity to `board.toml`.
2. Fill each [required area](#required-areas) using the [record fields](#record-format). Include selected components, board-package code, inputs and ordered operations.
3. Assign a [completion level](#completion-levels) supported by the source, host or device evidence. Record missing inputs and the next concrete action.
4. Run the checker in [Change workflow](#change-workflow). Resolve the reported identity, coverage and evidence errors.
5. Publish the device commit and follow [Publishing and reuse](#publishing-and-reuse). Confirm the generated page links to the published revision.

## Required areas

Each area records inputs, configuration, procedure, development findings,
completion criteria, current limits, next action, and evidence.

| Area | Required technical detail |
| --- | --- |
| Configuration | SoC and OS profiles, source pins, component choices, array replacements, defconfig and patch order |
| Firmware and boot | Boot format, firmware revision, PSCI, framebuffer and memory handoff |
| CPU and interrupts | CPU affinities, enabled cores, GIC ranges, timer rate, interrupts and IPIs |
| Memory and DMA | DRAM, reservations, address translation, DMA widths, cache policy and SMMU ownership |
| Storage and root | Host, PHY, clocks, resets, power, SMMU stream, DMA, LUNs, GPT, root and persistent Data |
| Display | Controller or GOP, panel, stride, format, timing, backlight and presentation |
| Input | Bus, sensor protocol, pins, interrupts, firmware, contact IDs and coordinate mapping |
| GPU | GPU/GMU generation, firmware, votes, SMMU, submission, fences, frontend ABI and presentation |
| Network | Bus, firmware, interrupts, DMA, OS interface, association and packet transfer |
| Audio | DSP, codec, clocks, firmware services, routes and playback/capture |
| Power | Regulators, clocks, battery units, firmware ownership and supported transitions |
| Image assembly | XNU and IPSW versions, ABI inputs, patch order, ADT, payload and boot-image format |
| Diagnostics | Log transport, checkpoints, recovery, commands and image/source revisions |

Add areas for other peripherals. Every selected component and its catalog
dependencies belong to an area. Use `not-applicable` with a reason in `limits`
for a function outside the board's scope. Use `planned` for unfinished work.

## Record format

Copy `examples/device/porting.toml`. Its device name, SoC and OS profile must
match `board.toml`. The record itself uses format 1, so its `schema_version`
stays `1` while `board.toml` uses `schema_version = 2`. Each `[[area]]` contains:

| Field | Content |
| --- | --- |
| `id` | Stable area identifier |
| `status` | Completion level from the table below |
| `components` | Canonical component IDs, including dependencies |
| `paths` | Repository-relative file patterns owned by this area |
| `inputs` | Hardware resources, external inputs and dependencies |
| `configuration` | Actual TOML keys, DTS properties and kernel flags |
| `procedure` | Ordered operations and commands |
| `findings` | Observation, established cause, implementation decision and conditions for reuse |
| `completion` | Observable result required at each milestone |
| `limits` | Current implementation scope and unresolved inputs |
| `next_action` | Concrete next measurement or implementation step |
| `evidence` | Source, host or device records with references and results |

Write findings as technical facts. For example: an idle UFS AHB clock branch
can report `CLK_OFF` while hardware gating is enabled, so the probe checks
branch enable and gating together. Link the implementation or captured register
record. When the cause is unknown, record the symptom and the next measurement.

## Completion levels

| Status | Required evidence |
| --- | --- |
| `planned` | Required inputs and next action |
| `implemented` | Source reference and implementation scope |
| `host-verified` | Host command, full source commit, result and accessible log |
| `device-verified` | Device command, full source commit, result and accessible log identifying the device, firmware and image |
| `not-applicable` | Scope explanation in `limits`, with an empty component list |

Each evidence entry has `kind`, `reference`, and `result`. Host and device
entries also have `command` and a full 40-character `revision`. References use
HTTPS or a committed file relative to the device repository. Store large logs
as linked release or CI artifacts. Record unavailable inputs in `limits` and
the measurement needed to resolve them in `next_action`.

## Change workflow

1. Read the device record and the relevant common guide before implementation.
2. Identify the affected areas and their existing components.
3. Update the implementation and each affected area's findings or evidence.
4. Update configuration, procedure and completion criteria when the interface changes.
5. Run the record checker and the existing checks for the changed implementation.
6. Submit code and documentation in separate commits in the same pull request.
7. Publish the device change. The catalog workflow refreshes its source revision and generated page.

```sh
python3 scripts/porting-record.py check --device ../UniXNU-sheng
python3 scripts/porting-record.py check --device ../UniXNU-sheng --base origin/main
```

Run the second command on the proposed device branch. It compares committed
changes against the base. Every changed code path needs an owning area;
each matching area needs updated findings or evidence. Markdown edits use the
documentation review workflow. `porting.toml` is the authoritative device record.

The device template includes `.github/workflows/porting-record.yml`. Official
device branches require its `Porting record` check. Reviewers verify hardware
facts, evidence quality, component reuse and the stated completion level.

## Publishing and reuse {#publishing-and-reuse}

Complete the [repository publication steps](/porting/device-repository#publish),
including the `unixnu` GitHub topic.

The [catalog workflow](https://github.com/UniXNU/UniXNU/actions/workflows/sync-devices.yml)
runs at 00:00 and 12:00 UTC. It searches public repositories in the UniXNU
organization, with the `unixnu` topic, or with UniXNU in their name or description.
It reads root `board.toml` and `porting.toml` files at a fixed commit.

`board.toml` uses `schema_version = 2`; the record uses `schema_version = 1`.
The workflow checks identity, required areas, component coverage and evidence.
Valid records generate English and Chinese pages, the device index and navigation.
Format 2 pages with missing or invalid records link to the repository and identify
the required record work. Existing legacy pages keep their authored content.
New legacy entries contain a repository link.

`devices.toml` stores repository identities, routes and source revisions.
`docs/.vitepress/device-records/` stores the source records. Site builds render
these committed snapshots. Both languages use the same record text. Write the
record in concise English. Site sources and deployment remain in UniXNU.

To request a scan immediately:

```sh
gh workflow run sync-devices.yml --repo UniXNU/UniXNU
```

To scan locally, sign in with `gh auth login` or set `GITHUB_TOKEN`, then run
from the UniXNU checkout:

```sh
python3 scripts/sync-devices.py
npm --prefix docs run build
```

The workflow builds the site before committing generated changes and publishing
that commit through the Docs workflow. Source errors appear in the workflow
summary. Correct the device record and publish it before the next scan.

For a local preview:

```sh
python3 scripts/porting-record.py site --local sheng=../UniXNU-sheng
cd docs
npx vitepress build
```

Move a reusable procedure into the relevant common guide after checking its
hardware and ABI assumptions. Keep the device's values and evidence in its
record, and link the guide from that section. The README carries the device's
scope, dependencies, build entry points and link to this record. `AGENTS.md`
points to the same required reading.

- [UFS porting](/porting/ufs)
- [Device repository](/porting/device-repository)
- [Bring-up order](/porting/bring-up)

Use the [driver adaptation checklist](/porting/drivers) to fill the procedure and completion criteria for display, brightness, input, GPU, Wi-Fi, DSP, audio and power.
