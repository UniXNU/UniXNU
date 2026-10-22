import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  lang: 'en-US',
  title: 'UniXNU',
  description: 'Run iOS and macOS on non-Apple ARM64 hardware through UEFI.',
  cleanUrls: true,
  lastUpdated: true,
  locales: {
    root: {
      label: 'English',
      lang: 'en-US',
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      themeConfig: {
        nav: [
          { text: '指南', link: '/zh/guide/overview', activeMatch: '^/zh/(guide/|building)' },
          { text: '移植', link: '/zh/porting/', activeMatch: '^/zh/porting/' },
          { text: '驱动', link: '/zh/drivers/overview', activeMatch: '^/zh/drivers/' },
          { text: 'XNU', link: '/zh/xnu/source-and-patches', activeMatch: '^/zh/xnu/' },
          { text: '设备', link: '/zh/devices/', activeMatch: '^/zh/devices/' },
          { text: '参考', link: '/zh/reference/cli', activeMatch: '^/zh/reference/' },
          { text: '参与贡献', link: '/zh/contributing/documentation', activeMatch: '^/zh/contributing/' },
          { text: 'GitHub', link: 'https://github.com/UniXNU/UniXNU', target: '_blank', rel: 'noopener' },
        ],
        sidebar: {
          '/zh/guide/': [
            {
              text: '指南',
              items: [
                { text: '总览', link: '/zh/guide/overview' },
                { text: '构建环境', link: '/zh/guide/requirements' },
                { text: '构建', link: '/zh/building' },
                { text: '构建内核', link: '/zh/guide/build-kernel' },
                { text: '启动镜像', link: '/zh/guide/boot' },
                { text: '调试与日志', link: '/zh/guide/debugging' },
                { text: '跳过 Setup', link: '/zh/guide/skip-setup' },
                { text: 'MobileGestalt 身份', link: '/zh/guide/mobilegestalt' },
                { text: 'userdata 镜像', link: '/zh/guide/userdata' },
              ],
            },
          ],
          '/zh/building': [
            {
              text: '指南',
              items: [
                { text: '总览', link: '/zh/guide/overview' },
                { text: '构建环境', link: '/zh/guide/requirements' },
                { text: '构建', link: '/zh/building' },
                { text: '构建内核', link: '/zh/guide/build-kernel' },
                { text: '启动镜像', link: '/zh/guide/boot' },
                { text: '调试与日志', link: '/zh/guide/debugging' },
                { text: '跳过 Setup', link: '/zh/guide/skip-setup' },
                { text: 'MobileGestalt 身份', link: '/zh/guide/mobilegestalt' },
                { text: 'userdata 镜像', link: '/zh/guide/userdata' },
              ],
            },
          ],
          '/zh/concepts/': [
            {
              text: '原理',
              items: [
                { text: '启动链', link: '/zh/concepts/boot-chain' },
                { text: '启动负载', link: '/zh/concepts/payload' },
                { text: '内核预链接', link: '/zh/concepts/prelink' },
                { text: 'userdata 布局', link: '/zh/concepts/userdata' },
                { text: '完整性与启动策略', link: '/zh/concepts/security' },
              ],
            },
          ],
          '/zh/porting/': [
            {
              text: '移植',
              items: [
                { text: '移植总览', link: '/zh/porting/' },
                { text: '设备仓库', link: '/zh/porting/device-repository' },
                { text: 'UEFI 固件', link: '/zh/porting/uefi-firmware' },
                { text: '设备树', link: '/zh/porting/device-tree' },
                { text: 'bring-up 顺序', link: '/zh/porting/bring-up' },
                { text: '双系统分区', link: '/zh/porting/dual-system-partition' },
              ],
            },
          ],
          '/zh/drivers/': [
            {
              text: '驱动',
              items: [
                { text: '驱动分层', link: '/zh/drivers/overview' },
                { text: 'UEFI 驱动', link: '/zh/drivers/uefi-drivers' },
                { text: 'XNU 驱动', link: '/zh/drivers/xnu-drivers' },
                { text: 'Adreno 740 驱动', link: '/zh/drivers/native-adreno' },
                { text: 'Novatek 触控驱动', link: '/zh/drivers/native-novatek-touch' },
                { text: 'kext 包', link: '/zh/drivers/kexts' },
                { text: '设备树匹配', link: '/zh/drivers/device-tree-matching' },
              ],
            },
          ],
          '/zh/xnu/': [
            {
              text: 'XNU',
              items: [
                { text: '源码与补丁', link: '/zh/xnu/source-and-patches' },
                { text: '4 KiB 页表', link: '/zh/xnu/four-k-page-tables' },
                { text: '补丁参考', link: '/zh/xnu/patch-reference' },
                { text: '启动参数', link: '/zh/xnu/boot-arguments' },
              ],
            },
          ],
          '/zh/devices/': [
            {
              text: '设备',
              items: [
                { text: '支持的设备', link: '/zh/devices/' },
                { text: '小米平板 6S Pro（sheng）', link: '/zh/devices/sheng' },
                { text: '无人值守测试', link: '/zh/devices/sheng-unattended-test' },
                {
                  text: '社区移植',
                  collapsed: true,
                  items: [
                    { text: 'DroidVM 客户机', link: '/zh/devices/droidvm' },
                    { text: 'QEMU virt', link: '/zh/devices/qemu' },
                    { text: '联想小新 Pad 2022（tb128fu）', link: '/zh/devices/tb128fu' },
                    { text: '一加 10 Pro 5G（negroni）', link: '/zh/devices/negroni' },
                    { text: '小米 17 Pro（pandora）', link: '/zh/devices/pandora' },
                    { text: '小米 13（fuxi）', link: '/zh/devices/fuxi' },
                    { text: '一加 7 Pro（guacamole）', link: '/zh/devices/guacamole' },
                    { text: '一加 Ace 5（giulia）', link: '/zh/devices/giulia' },
                    { text: '小米平板 7 / POCO Pad X1（uke）', link: '/zh/devices/uke' },
                    { text: '小米平板 8 Pro（piano）', link: '/zh/devices/piano' },
                    { text: '小米 13 Pro（nuwa）', link: '/zh/devices/nuwa' },
                    { text: '一加 13T（oneplus13t）', link: '/zh/devices/oneplus13t' },
                    { text: '一加平板 2 Pro（erhai）', link: '/zh/devices/erhai' },
                    { text: 'OPPO Find X7 Ultra（PHY120）', link: '/zh/devices/phy120' },
                    { text: 'Redmi K40 Pro（haydn）', link: '/zh/devices/haydn' },
                    { text: '小米平板 5（nabu）', link: '/zh/devices/nabu' },
                    { text: '一加 6T（fajita）', link: '/zh/devices/fajita' },
                    { text: 'Microsoft Surface Duo 2（zeta）', link: '/zh/devices/zeta' },
                    { text: '一加 Ace 5 Pro（hummer）', link: '/zh/devices/hummer' },
                    { text: '小米 15（dada）', link: '/zh/devices/dada' },
                    { text: 'Redmi Note 14 Pro+ 5G（amethyst）', link: '/zh/devices/amethyst' },
                    { text: 'Redmi K70（vermeer）', link: '/zh/devices/vermeer' },
                    { text: '努比亚红魔 8 Pro / 8 Pro+（nx729j）', link: '/zh/devices/nx729j' },
                    { text: '小米平板 6（pipa）', link: '/zh/devices/pipa' },
                    { text: 'Galaxy Tab A7 10.4（gta4l）', link: '/zh/devices/gta4l' },
                    { text: 'Redmi Note 10 Pro（sweet）', link: '/zh/devices/sweet' },
                    { text: '一加 5（cheeseburger）', link: '/zh/devices/cheeseburger' },
                    { text: 'Redmi K20 Pro / Mi 9T Pro（raphael）', link: '/zh/devices/raphael' },
                    { text: 'Galaxy Z Fold3（q2q）', link: '/zh/devices/q2q' },
                    { text: 'Redmi K30 5G（picasso）', link: '/zh/devices/picasso' },
                    { text: 'Redmi 9A（dandelion）', link: '/zh/devices/dandelion' },
                    { text: '小米 6（sagit）', link: '/zh/devices/sagit' },
                  ],
                },
              ],
            },
          ],
          '/zh/reference/': [
            {
              text: '参考',
              items: [
                { text: '命令行', link: '/zh/reference/cli' },
                { text: '设备配置', link: '/zh/reference/configuration' },
                { text: '启动配置', link: '/zh/reference/boot-configuration' },
                { text: '输出布局', link: '/zh/reference/output-layout' },
                { text: 'QEMU 测试', link: '/zh/reference/qemu' },
                { text: '故障排查', link: '/zh/reference/troubleshooting' },
                { text: '术语表', link: '/zh/reference/glossary' },
              ],
            },
          ],
          '/zh/contributing/': [
            {
              text: '参与贡献',
              items: [
                { text: '文档站', link: '/zh/contributing/documentation' },
                { text: '仓库布局', link: '/zh/contributing/repository' },
              ],
            },
          ],
        },
        outline: { level: [2, 3], label: '本页内容' },
        docFooter: { prev: '上一页', next: '下一页' },
        returnToTopLabel: '回到顶部',
        sidebarMenuLabel: '菜单',
        darkModeSwitchLabel: '外观',
        lightModeSwitchTitle: '切换到浅色主题',
        darkModeSwitchTitle: '切换到深色主题',
        editLink: {
          pattern: 'https://github.com/UniXNU/UniXNU/edit/main/docs/:path',
          text: '在 GitHub 上编辑此页',
        },
      },
    },
  },
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo-light.svg' }],
    ['meta', { name: 'theme-color', content: '#0b0c0f' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'UniXNU' }],
    ['meta', { property: 'og:description', content: 'Run iOS and macOS on non-Apple ARM64 hardware through UEFI.' }],
  ],
  themeConfig: {
    logo: {
      light: '/logo-light.svg',
      dark: '/logo-dark.svg',
      alt: 'UniXNU',
    },
    siteTitle: 'UniXNU',
    nav: [
      { text: 'Guide', link: '/guide/overview', activeMatch: '^/(guide/|building)' },
      { text: 'Porting', link: '/porting/', activeMatch: '^/porting/' },
      { text: 'Drivers', link: '/drivers/overview', activeMatch: '^/drivers/' },
      { text: 'XNU', link: '/xnu/source-and-patches', activeMatch: '^/xnu/' },
      { text: 'Devices', link: '/devices/', activeMatch: '^/devices/' },
      { text: 'Reference', link: '/reference/cli', activeMatch: '^/reference/' },
      { text: 'Contributing', link: '/contributing/documentation', activeMatch: '^/contributing/' },
      { text: 'GitHub', link: 'https://github.com/UniXNU/UniXNU', target: '_blank', rel: 'noopener' },
    ],
    sidebar: {
      '/guide/': [
        {
          text: 'Guide',
          items: [
            { text: 'Overview', link: '/guide/overview' },
            { text: 'Requirements', link: '/guide/requirements' },
            { text: 'Build', link: '/building' },
            { text: 'Build the kernel', link: '/guide/build-kernel' },
            { text: 'Boot the image', link: '/guide/boot' },
            { text: 'Debugging and logs', link: '/guide/debugging' },
            { text: 'Skip Setup', link: '/guide/skip-setup' },
            { text: 'MobileGestalt identity', link: '/guide/mobilegestalt' },
            { text: 'Userdata image', link: '/guide/userdata' },
          ],
        },
      ],
      '/building': [
        {
          text: 'Guide',
          items: [
            { text: 'Overview', link: '/guide/overview' },
            { text: 'Requirements', link: '/guide/requirements' },
            { text: 'Build', link: '/building' },
            { text: 'Build the kernel', link: '/guide/build-kernel' },
            { text: 'Boot the image', link: '/guide/boot' },
            { text: 'Debugging and logs', link: '/guide/debugging' },
            { text: 'Skip Setup', link: '/guide/skip-setup' },
            { text: 'MobileGestalt identity', link: '/guide/mobilegestalt' },
            { text: 'Userdata image', link: '/guide/userdata' },
          ],
        },
      ],
      '/concepts/': [
        {
          text: 'Concepts',
          items: [
            { text: 'Boot chain', link: '/concepts/boot-chain' },
            { text: 'Boot payload', link: '/concepts/payload' },
            { text: 'Kernel prelink', link: '/concepts/prelink' },
            { text: 'Userdata layout', link: '/concepts/userdata' },
            { text: 'Integrity and boot policy', link: '/concepts/security' },
          ],
        },
      ],
      '/porting/': [
        {
          text: 'Porting',
          items: [
            { text: 'Porting overview', link: '/porting/' },
            { text: 'Device repository', link: '/porting/device-repository' },
            { text: 'UEFI firmware', link: '/porting/uefi-firmware' },
            { text: 'Device tree', link: '/porting/device-tree' },
            { text: 'Bring-up order', link: '/porting/bring-up' },
            { text: 'Dual-system partition', link: '/porting/dual-system-partition' },
          ],
        },
      ],
      '/drivers/': [
        {
          text: 'Drivers',
          items: [
            { text: 'Driver layers', link: '/drivers/overview' },
            { text: 'UEFI drivers', link: '/drivers/uefi-drivers' },
            { text: 'XNU drivers', link: '/drivers/xnu-drivers' },
            { text: 'Adreno 740 driver', link: '/drivers/native-adreno' },
            { text: 'Novatek touch driver', link: '/drivers/native-novatek-touch' },
            { text: 'Kext bundles', link: '/drivers/kexts' },
            { text: 'Device tree matching', link: '/drivers/device-tree-matching' },
          ],
        },
      ],
      '/xnu/': [
        {
          text: 'XNU',
          items: [
            { text: 'Source and patches', link: '/xnu/source-and-patches' },
            { text: 'Four-kilobyte pages', link: '/xnu/four-k-page-tables' },
            { text: 'Patch reference', link: '/xnu/patch-reference' },
            { text: 'Boot arguments', link: '/xnu/boot-arguments' },
          ],
        },
      ],
      '/devices/': [
        {
          text: 'Devices',
          items: [
            { text: 'Supported devices', link: '/devices/' },
            { text: 'Xiaomi Pad 6S Pro (sheng)', link: '/devices/sheng' },
            { text: 'Unattended test cycle', link: '/devices/sheng-unattended-test' },
            {
              text: 'Community ports',
              collapsed: true,
              items: [
                { text: 'DroidVM guest', link: '/devices/droidvm' },
                { text: 'QEMU virt', link: '/devices/qemu' },
                { text: 'Lenovo Xiaoxin Pad 2022 (tb128fu)', link: '/devices/tb128fu' },
                { text: 'OnePlus 10 Pro 5G (negroni)', link: '/devices/negroni' },
                { text: 'Xiaomi 17 Pro (pandora)', link: '/devices/pandora' },
                { text: 'Xiaomi 13 (fuxi)', link: '/devices/fuxi' },
                { text: 'OnePlus 7 Pro (guacamole)', link: '/devices/guacamole' },
                { text: 'OnePlus Ace 5 (giulia)', link: '/devices/giulia' },
                { text: 'Xiaomi Pad 7 / POCO Pad X1 (uke)', link: '/devices/uke' },
                { text: 'Xiaomi Pad 8 Pro (piano)', link: '/devices/piano' },
                { text: 'Xiaomi 13 Pro (nuwa)', link: '/devices/nuwa' },
                { text: 'OnePlus 13T (oneplus13t)', link: '/devices/oneplus13t' },
                { text: 'OnePlus Pad 2 Pro (erhai)', link: '/devices/erhai' },
                { text: 'OPPO Find X7 Ultra (PHY120)', link: '/devices/phy120' },
                { text: 'Redmi K40 Pro (haydn)', link: '/devices/haydn' },
                { text: 'Xiaomi Pad 5 (nabu)', link: '/devices/nabu' },
                { text: 'OnePlus 6T (fajita)', link: '/devices/fajita' },
                { text: 'Microsoft Surface Duo 2 (zeta)', link: '/devices/zeta' },
                { text: 'OnePlus Ace 5 Pro (hummer)', link: '/devices/hummer' },
                { text: 'Xiaomi 15 (dada)', link: '/devices/dada' },
                { text: 'Redmi Note 14 Pro+ 5G (amethyst)', link: '/devices/amethyst' },
                { text: 'Redmi K70 (vermeer)', link: '/devices/vermeer' },
                { text: 'Nubia RedMagic 8 Pro / 8 Pro+ (nx729j)', link: '/devices/nx729j' },
                { text: 'Xiaomi Pad 6 (pipa)', link: '/devices/pipa' },
                { text: 'Galaxy Tab A7 10.4 (gta4l)', link: '/devices/gta4l' },
                { text: 'Redmi Note 10 Pro (sweet)', link: '/devices/sweet' },
                { text: 'OnePlus 5 (cheeseburger)', link: '/devices/cheeseburger' },
                { text: 'Redmi K20 Pro / Mi 9T Pro (raphael)', link: '/devices/raphael' },
                { text: 'Galaxy Z Fold3 (q2q)', link: '/devices/q2q' },
                { text: 'Redmi K30 5G (picasso)', link: '/devices/picasso' },
                { text: 'Redmi 9A (dandelion)', link: '/devices/dandelion' },
                { text: 'Xiaomi Mi 6 (sagit)', link: '/devices/sagit' },
              ],
            },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'Command line', link: '/reference/cli' },
            { text: 'Device configuration', link: '/reference/configuration' },
            { text: 'Boot configuration', link: '/reference/boot-configuration' },
            { text: 'Output layout', link: '/reference/output-layout' },
            { text: 'QEMU testing', link: '/reference/qemu' },
            { text: 'Troubleshooting', link: '/reference/troubleshooting' },
            { text: 'Glossary', link: '/reference/glossary' },
          ],
        },
      ],
      '/contributing/': [
        {
          text: 'Contributing',
          items: [
            { text: 'Documentation site', link: '/contributing/documentation' },
            { text: 'Repository layout', link: '/contributing/repository' },
          ],
        },
      ],
    },
    search: {
      provider: 'local',
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/UniXNU/UniXNU' },
      { icon: 'x', link: 'https://x.com/unixnu' },
      {
        icon: {
          svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.89-.86.2-1.3l15.97-6.16c.73-.33 1.43.18 1.15 1.3l-2.72 12.81c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z"/></svg>',
        },
        link: 'https://t.me/unixnu',
      },
    ],
    footer: {
      message: 'Released under the BSD-2-Clause-Patent License.',
      copyright: 'Copyright 2026 UniXNU contributors',
    },
    editLink: {
      pattern: 'https://github.com/UniXNU/UniXNU/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },
    docFooter: {
      prev: 'Previous',
      next: 'Next',
    },
    outline: {
      level: [2, 3],
      label: 'On this page',
    },
    returnToTopLabel: 'Back to top',
    sidebarMenuLabel: 'Menu',
    darkModeSwitchLabel: 'Appearance',
    lightModeSwitchTitle: 'Use light theme',
    darkModeSwitchTitle: 'Use dark theme',
  },
}))
