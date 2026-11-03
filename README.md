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

> **Migration notice:** Update your device repository for shared SoC support and canonical component names. Follow the [migration guide](https://unixnu.com/porting/migration).

An independent project to run iOS and macOS on non-Apple ARM64 hardware through UEFI. Like OpenCore, UniXNU is a general UEFI environment and driver loading system: it loads the drivers a device needs and boots the OS through a common UEFI layer.

UniXNU provides shared build tools, ARM64 support, OS profiles and reusable components for ports across SoCs and devices. SoC repositories supply common platform support, and device repositories supply board configuration and hardware integration.

**🎉 News:** Adreno740 and AdrenoMetal implement GPU acceleration for A740/SM8550. See the [Adreno 740 driver documentation](https://unixnu.com/drivers/adreno740).

Documentation: [unixnu.com](https://unixnu.com). Start with [Port a device](https://unixnu.com/porting/) or [Build and boot](https://unixnu.com/building).

## Repositories

| Repository | Contents |
| --- | --- |
| [UniXNU](https://github.com/UniXNU/UniXNU) | Build tools, component catalog, ARM64 support, OS profiles, UEFI package, documentation |
| [UniXNU-sm8550-common](https://github.com/UniXNU/UniXNU-sm8550-common) | Shared SM8550 support |
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | Xiaomi Pad 6S Pro |
| [uefi-sheng](https://github.com/UniXNU/uefi-sheng) | UEFI firmware for the Xiaomi Pad 6S Pro |

Clone with `--recurse-submodules`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

BSD-2-Clause-Patent. See [LICENSE](LICENSE).
