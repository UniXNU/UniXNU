# Continuing the umi Wi-Fi driver (QCA6390)

Hand-off notes for the next working session. Hardware bring-up of the Wi-Fi
chip on the Xiaomi Mi 10 (umi, SM8250) under the ios-sweet XNU kernel.

## Where things stand (2026-10-24)

Branch `umi-scanout` on qcom-toolbox/ios-sweet, latest patch **0126**.
Boot arg `sweetwlan=7` gets this far on the phone:

1. PCIe0 link up to the QCA6390 (gen 2 x1).
2. Firmware `amss20.bin` read from the `modem` partition (FAT, long names).
3. Firmware boots: BHI -> SBL -> MHI READY/M0 -> BHIe -> mission mode.
4. MHI channels 20/21 (IPCR) start; the firmware sends a QRTR HELLO.
5. The firmware announces the WLFW service: `service 0x45 instance 0x101 node 7 port 0x1`.

NOTES.md (umi section, top) has the full history of each step.

## Update 2026-10-24 (patches 0127-0130)

Steps 1 and 2 below are done. `bsd/dev/sweet_wlfw.c` runs the whole message table
for `sweetwlan=8`, and on 0130 every step returned result 0, ending with WLAN_MODE
(mission mode); log `research/logs/live-0130.txt`. Differences from the plan:

- the firmware sends FW_INIT_DONE 0x38, not FW_READY 0x21 (both are accepted);
- ath11k sends WLAN_INI 0x2F (enablefwlog) before WLAN_CFG for qca6390;
- WLAN_CFG goes without shadow_reg_v2 (TLV 0x14) until the host has CE rings;
- board id is 0xff, so the board file is `bdwlan.elf`; `sweetwlanbdf=NAME` overrides it;
- the UDP log drops lines under load: trust `SWEET PCIE: stage 8 done, result N`
  (21-32 = step 1-12 failed) and read memory with `tools/sweet-mon.py` when unsure.

0131 adds `bsd/dev/sweet_wlce.c`: copy-engine rings (polled, direct HP/TP writes,
no shadow registers), HTC READY, WMI control connected on endpoint 1, and the
firmware sends SERVICE_AVAILABLE, SERVICE_READY, SERVICE_READY_EXT, _EXT2
(log `research/logs/live-0131.txt`; stage 8 codes 33-38 cover CE/HTC).

0132: WMI_INIT (qca6390 resource config, no host memory: SERVICE_READY asks for
none) is answered by WMI_READY status 0, but the MAC address in it is zero (no
MAC in the chip's OTP). 0133: hw mode DBS, 2.4 GHz channel list, STA vdev
(02:00:5e:77:ee:10), passive scan: it completes and beacons from nearby access
points arrive as WMI_MGMT_RX. 0134: active scan (probe requests answered). The
firmware's regulatory country is "CN" (Xiaomi default). 0135: HTT connected
(version 3.90) and the country set to world "00" (user's choice). 0136:
`bsd/dev/sweet_wldp.c` sets up the SoC data-path rings (ath11k_dp_alloc; table from
`tools/ath11k-gen-dp.py`); all readbacks match and the firmware keeps working.
Next: RXDMA rings per MAC with HTT SRING_SETUP, RX buffers, RX filter; then
association. After each boot, `tools/umi-usbnet.sh` sets up the USB network.
0137-0139: receive DMA rings + HTT SRING_SETUP, monitor-status filter and reaping.
0140: the phone associates with an open network named on the boot line
(`sweetwlanssid=NAME`, `_` = space; keep the name out of git). Next: the data path
(TCL transmit, REO receive), then DHCP/ping and an IOKit network interface.

## What to do next

### Step 1: apply the saved IPCR changes

`research/ipcr-wlfw-wip.diff` (local file, not in git) applies to the kernel
source tree after patch 0126. It changes `bsd/dev/sweet_ipcr.c`:

- the send buffer moves to block offset `0xf000` and grows to 8 KiB;
- each send waits for its completion event;
- received packets go into a queue, handled by `sweet_ipcr_service(ms)`;
- QRTR data packets are answered with RESUME_TX when asked, and payloads
  for our port `0x4001` go to `sweet_wlfw_rx()`;
- `sweet_ipcr_send(qmi, len)` sends one QMI message to the WLFW service.

It references `sweet_wlfw_rx()`, so it only links once Step 2 exists.

### Step 2: write `bsd/dev/sweet_wlfw.c`

A small QMI client, following Linux `drivers/net/wireless/ath/ath11k/qmi.c`
for "qca6390 hw2.0". Write it in several small edits rather than one large
file. QMI framing: 1-byte type (0 request, 2 response, 4 indication), u16
transaction id, u16 message id, u16 length, then TLVs (u8 type, u16 length,
value). Responses carry TLV 0x02 = {u16 result, u16 error}.

Message order:

| # | Message | ID | Fields (TLV type: value) |
| --- | --- | --- | --- |
| 1 | IND_REGISTER | 0x20 | 0x10 fw_ready 1, 0x15 client_id 0x4b4e454c, 0x16 request_mem 1, 0x17 fw_mem_ready 1, 0x18 fw_init_done 1, 0x1B cal_done 1 (each u8 except client_id u32) |
| 2 | HOST_CAP | 0x34 | 0x10 num_clients u32 1, 0x13 nm_modem u8 0x1e, 0x14 bdf_support 1, 0x16 m3_support 1, 0x17 m3_cache_support 1, 0x1A cal_done 0, 0x1C mem_cfg_mode 0 |
| 3 | wait REQUEST_MEM indication | 0x35 | TLV 0x01: u8 count, then per segment u32 size, u32 type, u8 cfg count, cfg[] {u64 offset, u32 size, u8 flag} |
| 4 | RESPOND_MEM | 0x36 | TLV 0x01: u8 count, then per segment u64 addr, u32 size, u32 type, u8 restore 0 |
| 5 | wait FW_MEM_READY indication | 0x37 | |
| 6 | CAP | 0x24 | no fields; log the response (board id, chip id, firmware version) |
| 7 | BDF_DOWNLOAD | 0x25 | board file `bdwlan.e*` / `bdwlan.elf` in 6 KiB segments |
| 8 | M3_INFO | 0x3C | address and size of `m3.bin` copied into low RAM |
| 9 | wait FW_READY indication | 0x21 | |
| 10 | WLAN_CFG then WLAN_MODE | 0x23, 0x22 | copy-engine configuration, then mission mode |

Firmware memory for step 4: low RAM that the kernel does not manage, for
example `0xd1000000`, 16 MiB, mapped with `ml_io_map_unmappable(pa, size, 0x6)`
(the arm I/O submap is only 8 MiB). Log the requested sizes first.

Add the file to `bsd/conf/files` (`bsd/dev/sweet_wlfw.c standard`) and call
`sweet_wlfw_run()` from `sweet_wlan_fw_boot()` for `stage >= 8`, after
`sweet_ipcr_start()` succeeds.

Start with steps 1-5 only and test; then CAP; then the rest.

## Build and test loop

- Kernel source tree: `$TMPDIR/sweetwork/t-sweet` (git, one commit per patch).
- Compile check: `XNU_CC_OBJDIR=$TMPDIR/sweetwork/obj python3 $TMPDIR/sweetwork/xcc.py $TMPDIR/sweetwork/log/run.log $TMPDIR/sweetwork/bt bsd/dev/FILE.c --per-file`
  (copy changed files into `$TMPDIR/sweetwork/bt/xnu/bsd/dev/` first).
- Patch: `git format-patch -1 --stdout HEAD > xnu/patches/01NN-name.patch`, check the
  series with `bash $TMPDIR/sweetwork/apply.sh xnu/patches $TMPDIR/sweetwork/chk`.
- Commit, push `umi-scanout`, `gh workflow run xnu.yml --ref umi-scanout`, download the
  artifact to `xnu/out-01NN`.
- Boot image + boot from TWRP: the helper `SWEET_TOOLBIN=$HOME/ios-sweet-port/toolbin tools/umi-dev-boot.sh K TAG ARGS` does
  `tools/mkpayload.py` + `BOARD=umi shim/build.sh` + `fastboot boot`; boot args used:
  `sweetusb=2 sweetwlan=8 sweetwlandelay=90` on top of the base line in
  `tools/umi-boot-image.sh`.
- Always use `ANDROID_SERIAL=${UMI_SERIAL}` / `fastboot -s ${UMI_SERIAL}` (a second phone is attached).
- USB network: after each boot the user runs
  `sudo ifconfig en8 inet 192.168.7.1 netmask 255.255.255.0 alias`.
- Live log: `nc -ul 5140 >> research/logs/live-01NN.txt` (only one listener).
- Re-run the Wi-Fi bring-up without rebooting: `python3 tools/sweet-mon.py 'wlan 8'`;
  register reads: `python3 tools/sweet-mon.py 'r 0xADDR N'`.

## Later

- `/arm-io/wlan` ADT node (topaz `tools/mkadt.py`, branch `topaz`): needed before
  launchd starts `wifid`.
- Copy engines / HTC / WMI (ath11k), then topaz patch 0900 (Apple80211 interface for wifid).
- Wallpaper: depends on GPU rendering (topaz uses Mesa freedreno on Adreno 610);
  umi would need Adreno 650 support first.
