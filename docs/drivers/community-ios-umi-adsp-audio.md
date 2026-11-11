# SweetAudio

Audio for the Xiaomi Mi 10 (umi, SM8250): ADSP boot, AFE / ASM / ADM over APR, the audio PD over FastRPC and the two CS35L41 amplifiers on tertiary MI2S, reached by iOS through `/dev/sweet-audio` and the `SweetAudio.driver` HAL plug-in.

| Repository | Maintainer | Scope |
| --- | --- | --- |
| [ios-umi](https://github.com/qcom-toolbox/ios-umi) | [qcom-toolbox](https://github.com/qcom-toolbox) | [XNU patches 0215–0232](https://github.com/qcom-toolbox/ios-umi/tree/main/xnu/patches); [SweetAudio.driver](https://github.com/qcom-toolbox/ios-umi/tree/main/phone/sweet-audio) |

## State

Ringtones and system sounds play from the speaker. No microphones; the earpiece is not used. Device page: [Xiaomi Mi 10 — iOS 16](/devices/umi-qcom-toolbox).

## Maintenance

The maintainer owns the repository and its release decisions. UniXNU documentation lists the driver and its state; it does not take over maintenance.
