# Main Status

- Device: Xiaomi Mi 10 (umi, Snapdragon 865 / SM8250), running iOS 16.7.16 as an iPhone X (`iPhone10,3` / `D22AP`)

> [!IMPORTANT]
> **This is a bring-up project.** The status below is for reference only and changes often; the details of every
> item (how it works, what was tried, what failed) are in [`NOTES.md`](NOTES.md). Security is off on this build:
> do not put anything personal on the phone.

✅ works · ⚠️ partly works / needs testing · ❌ does not work yet

| Feature | Notes | Status |
|---|---|---|
| 🥾 Boot | Stock bootloader → `fastboot boot` of our shim → XNU | ✅ |
| 🧠 CPU | All 8 cores; clocks follow the load (EPSS governor, 75 °C limit) | ✅ |
| 💾 UFS | Own host driver, HFS+ root in `userdata`, read/write | ✅ |
| 🖥️ Display | 1080×2340 AMOLED, presented as the iPhone X panel | ✅ |
| 🔆 Brightness | Slider, Control Center, auto-brightness, Night Shift | ✅ |
| 👆 Touch | ST FTM5 | ✅ |
| 🔘 Buttons | Power, volume up/down | ✅ |
| 🔋 Battery | Real percentage, voltage, current, charging state | ✅ |
| 🔌 Type-C Charge | Charges; no charger control or fast-charge negotiation from iOS | ⚠️ |
| ⚡ Wireless charge | | ❌ |
| 🔊 Audio | Speaker works (ringtones, system sounds); no microphones, earpiece not used | ⚠️ |
| 🛜 WiFi | 2.4 GHz, open + WPA2-PSK, legacy rates | ⚠️ |
| 🦷 Bluetooth | QCA6390 over UART (921600 baud): scan, connect and pair in Settings, Control Center button, off / on (slow); see the tests below | ⚠️ |
| 📶 Cellular Data | | ❌ |
| 📍 Location | Works through Wi-Fi positioning (Weather shows the city, Maps asks for permission) | ✅ |
| 🛰️ GPS | No GPS receiver driver yet; location comes from Wi-Fi | ❌ |
| 🪵 USB | Device mode (USB Ethernet + kernel log) for development; no host / iTunes | ⚠️ |
| 🧭 Sensor | Ambient light only | ⚠️ |
| 🎆 GPU | Adreno 650 draws the UI (CoreAnimation through Metal / turnip); CPU overhead while animating still high | ✅ |
| 🎬 Video decode | No hardware decoder, videos do not play | ❌ |
| 📷 Camera | | ❌ |
| 🔦 Camera Flash | | ❌ |
| 📳 Vibration motor | | ❌ |
| 🫆 Fingerprint | In-display sensor | ❌ |
| 🔐 Face ID / SEP | | ❌ |
| 💳 NFC | | ❌ |
| 🪪 Activation | Local "Hactivation" path, no Apple servers | ✅ |

# Detailed status

## 🔊 Audio

### Various functions of Audio

| Feature | Notes | Status |
|---|---|---|
| 🎛️ ADSP | Booted by the kernel ~200 s after boot; APR to its AFE / ASM / ADM services | ✅ |
| 🔈 Bottom speaker | TERT_MI2S (SD1) → CS35L41 at I²C 0x40; iOS reaches it through `SweetAudio.driver` + `/dev/sweet-audio` | ✅ |
| 🔔 Ringtones / system sounds | Full ringtones play; the ringer slider preview stops after ~2 s, as on a real iPhone | ✅ |
| 🎵 Music / media apps | No media app session reached the audio system in tests | ⚠️ |
| 📞 Earpiece speaker | CS35L41 at 0x42 is enabled but not used as a separate channel | ⚠️ |
| 🔉 Volume | iOS software volume + our device volume control | ✅ |
| 🎙️ Microphones | Codec / Hawking devices are silent placeholders | ❌ |
| 🎧 Headphones (USB-C) | | ❌ |
| 🦷 Bluetooth audio | | ❌ |
| 📳 Haptics (Actuator) | The device exists for iOS's routing, its data is dropped | ❌ |
| ♻️ ADSP crash recovery | One crash seen (`SFR Init: wdog or kernel error suspected`); audio is gone until a reboot | ❌ |

## 🧭 Sensors

### Various functions of Sensors

| Feature | Notes | Status |
|---|---|---|
| 💡 Ambient light | SLPI firmware booted by the kernel, read through QRTR / SEE; drives auto-brightness | ✅ |
| 🌈 True Tone (color) | The light sensor's color channels are not read | ❌ |
| 📐 Accelerometer | | ❌ |
| 🌀 Gyroscope | | ❌ |
| 🧲 Magnetometer (compass) | | ❌ |
| 👂 Proximity | | ❌ |
| 🌡️ Barometer | | ❌ |
| 🛰️ GPS | | ❌ |

## 🪵 USB

### Various functions of USB

| Feature | Notes | Status |
|---|---|---|
| 🧪 Device mode (ECM) | USB Ethernet with the live kernel log (UDP 5140) and a kernel file server | ✅ |
| 💻 iTunes / Finder sync | | ❌ |
| 🪵 USB-Host (OTG) | | ❌ |

## 🎆 GPU

### Various functions of GPU

| Feature | Notes | Status |
|---|---|---|
| ⚙️ Power-up | GMU / RPMh, zap shader authenticated by TrustZone | ✅ |
| 🧾 Command streams | The command processor runs our streams | ✅ |
| 🎨 Metal | Over Mesa's turnip (`sweetmtl`), fence interrupts; a per-submit command walk still costs CPU | ✅ |
| 🖼️ CoreAnimation on the GPU | Composites through Metal on the GPU and scans out directly; only the App Library background blur still glitches; backboardd median ~20 % of a core, more when animating | ✅ |

## 🧠 CPU and performance

### Various functions of CPU

| Feature | Notes | Status |
|---|---|---|
| 🧩 SMP | 4× A55, 3× A77, 1× A77 prime via PSCI | ✅ |
| 📈 Frequency scaling | EPSS governor (kernel 0238): load-following per cluster, thermal cap at 75 °C, touch boost; idle at 288 / 710 / 844 MHz | ✅ |
| 🔥 Idle CPU load | High; the fixes [ios-s9](https://github.com/syncmodz/ios-s9) describes are still to check here (see below) | ⚠️ |
| 🎯 Thread placement | UI / render threads (priority ≥ 46 and realtime) kept on the A77s (kernel 0248, `sweetbig`): backboardd + SpringBoard 93 % on big cores, starts on a slow core with a big one idle 245 → 26 per 10 s | ✅ |

## 🌄 Future Development

> [!NOTE]
> Roughly in priority order. Each item gets a `NOTES.md` entry when work starts.

* **Sensors**: accelerometer, gyroscope, magnetometer, proximity, barometer through the SLPI; True Tone color channels
* **Camera**: the camera stack (CAMSS / ISP / sensors) and the flash
* **Bluetooth: still to test** (working since 2026-11-04, kernel 0234-0237 + `/usr/local/lib/libsweet-bt.dylib`):
  * Pairing kept after a reboot (apollo needed a file system sync for it, their xnu 0144)
  * Music to headphones (A2DP): smooth or stuttering at 921600 baud
  * Calls / microphone over Bluetooth (HFP) and headphone buttons (AVRCP)
  * Off / on in Control Center and Settings: it comes back, but slowly (bluetoothd: "stack is busy")
  * A boot with kernel 0237 alone (Bluetooth 1 s after UFS by default, no `sweetbtdelay=1` on the line)
  * BLE devices (watch, tracker, keyboard) and a second device paired at the same time
* **CPU frequency scaling, next steps**: memory bus (DDR) voting with the load (apollo's 0153 `sweet_rpmh_ddr_set`); a CPU budget for runaway background processes (apollo's 0160); an idle-temperature comparison against the bootloader's clocks (`sweetcpufreq=0`)
* **CPU load**, the fixes ios-s9 describes (`xnu/patches/0092`-`0094` there, idle CPU 460 % → ~50 %), to check and
  redo here: the securityd retry storm; `BTAudioHALPlugin.driver` polling a daemon that is not running; the touch
  polling thread on the fast ones (render / UI threads on the big cores: done, 0248); ad daemons (removed from launchd.plist
  2026-11-04); `driverkitd` killed and
  respawned every 10 s
* **fairplayd**: `fairplayd.H2` is out of launchd's job list (that unblocked location on 2026-10-31); still to do:
  put `CoreLocationMigrator` back, check `fairplaydeviceidentityd`, and make it part of the image build
* **Audio**: microphones, the earpiece as the second channel, an earlier ADSP start, ADSP restart after a crash,
  haptics on the Actuator
* **Video**: hardware decode (VideoToolbox / AVD)
* **GPU**: drop the per-submit cache walk (make Turnip's write-combined command memory coherent without it), less CPU per frame
* **Wi-Fi**: 5 GHz, HT / VHT rates, WPA3
* **Cellular**, **GPS**, **Fingerprint**, **Face ID / SEP**, **NFC**, **Wireless charging**
