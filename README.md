<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.svg">
    <img alt="UniXNU" src="assets/logo-light.svg" width="200">
  </picture>
</p>

<p align="center">
  <a href="https://unixnu.com"><img alt="Documentation" src="https://img.shields.io/badge/docs-unixnu.com-2A5BD7?logo=readthedocs&logoColor=white"></a>
  <a href="https://t.me/unixnu"><img alt="Telegram" src="https://img.shields.io/badge/Telegram-@unixnu-26A5E4?logo=telegram&logoColor=white"></a>
  <a href="https://qun.qq.com/universal-share/share?ac=1&authKey=Pubz23DOCY76nxjlGuSms2zesk4jRvas4zrXJRYk7omf7CprXbGQigLEI%2BCoYR8D&busi_data=eyJncm91cENvZGUiOiIxMTI2MTE2NzU5IiwidG9rZW4iOiJwSHJsUDN1UnN2Vi8yM210TjJRbzBIcERmcUpyOS9lb0hHVVpadWdvVFdScVpSYUFLT1YzTk5TWC9mN2xWYmtIIiwidWluIjoiMzE1MTEwOTc0MSJ9&data=_cJgr-jX9yJ2-GXwVjRN5FOhDyk5B-HAfIk5LSunbW_XkkmKqNXbpH33wzP93J0p9DI1fbjgBUrUfTVhwDcxjg&svctype=4&tempid=h5_group_info"><img alt="QQ Group" src="https://img.shields.io/badge/QQ%20Group-join-12B7F5?logo=qq&logoColor=white"></a>
  <a href="https://x.com/unixnu"><img alt="X" src="https://img.shields.io/badge/X-@unixnu-000000?logo=x&logoColor=white"></a>
</p>

<p align="center">
  English | <a href="README.zh-CN.md">简体中文</a>
</p>

# UniXNU

🎉 **News:** The native Metal GPU driver is now fully working on the Xiaomi Pad 6S Pro (sheng). The render server composites the system UI through the Adreno 740, and listed processes get their own Metal devices. See the [Adreno 740 driver documentation](https://unixnu.com/drivers/native-adreno).

An independent project to run iOS and macOS on non-Apple ARM64 hardware through UEFI.

## Documentation

The documentation is at [unixnu.com](https://unixnu.com). It covers the boot chain, the build driver, device porting, driver development, the 4 KiB XNU page patches, boot arguments and per-device notes.

- [Overview](https://unixnu.com/guide/overview)
- [Build](https://unixnu.com/building)
- [Boot the image](https://unixnu.com/guide/boot)
- [Debugging and logs](https://unixnu.com/guide/debugging)
- [Porting](https://unixnu.com/porting/)
- [Drivers](https://unixnu.com/drivers/overview)
- [XNU and 4 KiB pages](https://unixnu.com/xnu/four-k-page-tables)
- [Devices](https://unixnu.com/devices/)

## Repositories

| Repository | Contents |
| --- | --- |
| [UniXNU](https://github.com/UniXNU/UniXNU) | Build driver, UEFI boot manager, module submodules and patches |
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | Device repository for the Xiaomi Pad 6S Pro |
| [uefi-sheng](https://github.com/UniXNU/uefi-sheng) | UEFI firmware port for the Xiaomi Pad 6S Pro |

Drivers and kits are independent public repositories under the UniXNU organization, included as submodules. Clone with `--recurse-submodules`, or run `git submodule update --init --recursive`.

Device repositories use the same layout as this repository. Their modules override modules with the same name, and their `package/` becomes a kit in the build tree.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the repository scope, the development workflow, the commit format and the documentation rules.

## Private blobs

Do not add Apple IPSW files, kernelcaches, disk images, trust caches, Data seeds or vendor firmware to this repository. Keep them in a local cache or external storage.

## License

BSD-2-Clause-Patent. See [LICENSE](LICENSE).
