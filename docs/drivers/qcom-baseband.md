# QcomBaseband

Qualcomm baseband bridge and SC7180 IPA v4.2 data path by **HoshinoYumeka ([@chiba233](https://github.com/chiba233))**.

[Source repository](https://github.com/UniXNU/QcomBaseband). [Adaptation procedure](/porting/baseband).

The component provides QMUX/QRTR and QMI CTL, a SAHARA endpoint, AppleBaseband IOKit services, and IPA/GSI/QMAP code. The board supplies modem boot, firmware, power, DMA, GLINK/QRTR and rmtfs.

`baseband/QcomBaseband.h` defines the transport hooks. `scripts/build-qcom-baseband.py` builds the bridge archive from the selected XNU compile records; `--coachz` adds the SC7180 IPA adapter. Output: `build/qcom-baseband/libQcomBaseband.a`.

The Coachz example displays IMEI/ICCID and registers a valid SIM on LTE roaming with CS/PS attached. Operator and signal bars appear directly after a cold boot; data-port bindings succeed. The ABM receive queue holds up to 1,024 frames per channel. The bridge publishes the card's ICCID/IMSI for carrier-bundle matching. LTE is shown, and the carrier bundle's PRI/GRI files are accepted so CommCenter caches the configuration instead of restarting the baseband. BSP chip-ID/serial queries are answered. Cellular IPv4 web loading works through raw-IP `pdp_ip0` through `pdp_ip3` and the IPA adapter, including after PDP reconnects; IPv6 data, APN editing and long sessions are pending. IPv4/IPv6 state is tracked independently; read-only eSIM queries use a four-entry cache. The eSIM Tape/UIM bridge preserves capabilities across card-status changes, answers legacy initialization and keeps the logical channel through download preparation. Host models pass. eSIM appears in Settings on Coachz with an incomplete page; profile provisioning remains unverified. Wi-Fi-only devices can skip this component.

[Component catalog](/reference/components)
