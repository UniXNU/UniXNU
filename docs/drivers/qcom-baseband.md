# QcomBaseband

Qualcomm baseband bridge and SC7180 IPA v4.2 data path by **HoshinoYumeka ([@chiba233](https://github.com/chiba233))**.

[Source repository](https://github.com/UniXNU/QcomBaseband). [Adaptation procedure](/porting/baseband).

The component provides QMUX/QRTR and QMI CTL, a SAHARA endpoint, AppleBaseband IOKit services, and IPA/GSI/QMAP code. The board supplies modem boot, firmware, power, DMA, GLINK/QRTR and rmtfs.

`baseband/QcomBaseband.h` defines the transport hooks. `scripts/build-qcom-baseband.py` builds the bridge archive from the selected XNU compile records; `--coachz` adds the SC7180 IPA adapter. Output: `build/qcom-baseband/libQcomBaseband.a`.

The Coachz example reaches ABM startup and SIM recognition. ICCID, network registration, `pdp_ip` delivery and eSIM remain unfinished. Wi-Fi-only devices can skip this component.

[Component catalog](/reference/components)
