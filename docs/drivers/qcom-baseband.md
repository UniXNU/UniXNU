# QcomBaseband

Qualcomm baseband bridge and SC7180 IPA v4.2 data path by **HoshinoYumeka ([@chiba233](https://github.com/chiba233))**.

[Source repository](https://github.com/UniXNU/QcomBaseband). [Adaptation procedure](/porting/baseband).

The component provides QMUX/QRTR and QMI CTL, a SAHARA endpoint, AppleBaseband IOKit services, and IPA/GSI/QMAP code. The board supplies modem boot, firmware, power, DMA, GLINK/QRTR and rmtfs.

`baseband/QcomBaseband.h` defines the transport hooks. `scripts/build-qcom-baseband.py` builds the bridge archive from the selected XNU compile records; `--coachz` adds the SC7180 IPA adapter. Output: `build/qcom-baseband/libQcomBaseband.a`.

The Coachz example displays IMEI/ICCID and registers a valid SIM on LTE roaming with CS/PS attached. Operator and signal bars appear after SIM reinsertion; data-port bindings succeed. `pdp_ip` delivery and a working cellular data session remain unfinished. The eSIM Tape/UIM bridge preserves capabilities across card-status changes, answers legacy initialization and keeps the logical channel through download preparation. Host models pass. eSIM appears in Settings on Coachz with an incomplete page; profile provisioning remains unverified. Wi-Fi-only devices can skip this component.

[Component catalog](/reference/components)
