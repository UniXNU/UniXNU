# OnePlus 10 Pro 5G (negroni)

negroni is the OnePlus 10 Pro 5G (NE2213) with the SM8450 SoC. The port below is an independent community project. The UniXNU organization does not maintain it. It runs the iPhone X iOS 16.7.16 userland on an xnu-8796 kernel from the ios-sweet series through Mu-Silicium UEFI and UniXNU/DarwinBoot.

| Repository | Maintainer | State |
| --- | --- | --- |
| [UniXNU-negroni](https://github.com/pawlickerr/UniXNU-negroni) | [pawlickerr](https://github.com/pawlickerr) | iOS 16.7.16 SpringBoard on hardware; CPU-rendered |
| [Mu-Silicum-negroni](https://github.com/pawlickerr/Mu-Silicum-negroni) | [pawlickerr](https://github.com/pawlickerr) | Mu-Silicium UEFI firmware |

## State

| Stage | State |
| --- | --- |
| Boot | the ios-sweet shim starts Mu-Silicium; the UniXNU menu entry is "iOS 16 (negroni-ios XNU)"; the 64 MiB NEGRONIESP payload carries the kernel and ADT |
| Kernel | xnu-8796 from ios-sweet; DarwinBoot enters it in a 3 GiB window |
| Root | iOS 16.7.16 root on UFS, read-write |
| Userland | SpringBoard on 8 cores, with touch, hardware keys and a persistent console log |
| Packages | Sileo and the Procursus bootstrap are installed |
| Display | CPU-rendered, without GPU acceleration |
| Wi-Fi | QCA6490 on PCIe0 not up |

The root image replaces the Android userdata partition. The repository README records the build, flash and boot commands.

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the port and its state; it does not take over maintenance.
