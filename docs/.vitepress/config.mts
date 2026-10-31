import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import deviceCatalog from './device-catalog.json'

function deviceSidebar(zh: boolean) {
  const prefix = zh ? '/zh' : ''
  return [{
    text: zh ? '设备' : 'Devices',
    items: [
      { text: zh ? '设备列表' : 'Device list', link: `${prefix}/devices/` },
      ...deviceCatalog.map(device => ({
        text: zh ? device.title_zh : device.title,
        link: `${prefix}/devices/${device.name}`,
      })),
    ],
  }]
}

function taskSidebars(prefix: string, zh: boolean) {
  const item = (en: string, cn: string, path: string) => ({ text: zh ? cn : en, link: `${prefix}${path}` })
  const group = (en: string, cn: string, items: ReturnType<typeof item>[], collapsed = false) => ({ text: zh ? cn : en, items, collapsed })
  const build = [
    group('1. Prepare', '1. 准备', [
      item('Build and boot', '构建与启动', 'building'),
      item('Select a device', '选择设备', 'devices/'),
      item('Host and inputs', '主机与输入', 'guide/requirements'),
      item('Local configuration', '本地配置', 'reference/configuration#local-build-inputs'),
    ]),
    group('2. Build images', '2. 构建镜像', [
      item('Kernel', '内核', 'guide/build-kernel'),
      item('Firmware integration', '固件集成', 'porting/uefi-firmware'),
      item('Root and Data', '根卷与 Data', 'guide/userdata'),
      item('Payload', 'Payload', 'concepts/payload'),
      item('Skip Setup', '跳过 Setup', 'guide/skip-setup'),
      item('Platform identity', '平台身份', 'guide/mobilegestalt'),
    ]),
    group('3. Boot and diagnose', '3. 启动与诊断', [
      item('Boot the image', '启动镜像', 'guide/boot'),
      item('Boot arguments', '启动参数', 'xnu/boot-arguments'),
      item('Logs and checkpoints', '日志与检查点', 'guide/debugging'),
      item('Capture logs', '抓取日志', 'porting/log-capture'),
      item('Troubleshooting', '故障排查', 'reference/troubleshooting'),
      item('QEMU verification', 'QEMU 验证', 'reference/qemu'),
    ]),
  ]
  const port = [
    group('1. Prepare the port', '1. 准备移植', [
      item('Welcome', '欢迎', 'porting/'),
      item('Port a device', '移植设备', 'porting/steps'),
      item('Migrate a repository', '迁移已有仓库', 'porting/migration'),
      item('Device repository', '设备仓库', 'porting/device-repository'),
      item('Component selection', '选择组件', 'reference/components'),
      item('Select and add SoC support', '选择与添加 SoC 支持', 'porting/soc-support'),
      item('arm64e OS profiles', 'arm64e OS 配置', 'porting/arm64e'),
    ]),
    group('2. Describe hardware', '2. 描述硬件', [
      item('Device tree', '设备树', 'porting/device-tree'),
      item('Firmware integration', '固件集成', 'porting/uefi-firmware'),
      item('Dual-system partition', '双系统分区', 'porting/dual-system-partition'),
    ]),
    group('3. Adapt drivers', '3. 适配驱动', [
      item('Adaptation sequence', '适配顺序', 'porting/drivers'),
      item('Platform and memory', '平台与内存', 'porting/platform'),
      item('UFS storage', 'UFS 存储', 'porting/ufs'),
      item('Display and brightness', '显示与亮度', 'porting/display'),
      item('Touch and buttons', '触控与按键', 'porting/input'),
      item('GPU and Metal', 'GPU 与 Metal', 'porting/gpu'),
      item('Wi-Fi', 'Wi-Fi', 'porting/network'),
      item('DSP, audio and power', 'DSP、音频与电源', 'porting/power'),
      item('Develop a driver', '开发驱动', 'drivers/overview'),
      item('Change XNU', '修改 XNU', 'xnu/source-and-patches'),
    ]),
    group('4. Verify and publish', '4. 验证与发布', [
      item('Build and boot', '构建与启动', 'building'),
      item('Bring-up sequence', '启动验证顺序', 'porting/bring-up'),
      item('Log capture and boot tests', '日志抓取与启动测试', 'porting/log-capture'),
      item('Porting record', '适配记录', 'porting/records'),
      item('Publish documentation', '发布文档', 'contributing/documentation'),
    ]),
  ]
  const reference = [
    group('Technical reference', '技术参考', [item('Find a procedure or field', '查找操作与字段', 'reference/')]),
    group('Configuration and outputs', '配置与输出', [
      item('Command line', '命令行', 'reference/cli'),
      item('Device configuration', '设备配置', 'reference/configuration'),
      item('Component catalog', '组件目录', 'reference/components'),
      item('Boot configuration', '启动配置', 'reference/boot-configuration'),
      item('Output layout', '输出布局', 'reference/output-layout'),
      item('Glossary', '术语表', 'reference/glossary'),
    ], true),
    group('Boot concepts', '启动原理', [
      item('Boot chain', '启动链', 'concepts/boot-chain'),
      item('Prelink', '预链接', 'concepts/prelink'),
      item('Payload', 'Payload', 'concepts/payload'),
      item('Userdata layout', 'userdata 布局', 'concepts/userdata'),
      item('Integrity and boot policy', '完整性与启动策略', 'concepts/security'),
    ], true),
    group('Driver development', '驱动开发', [
      item('Develop a driver', '开发驱动', 'drivers/overview'),
      item('Repositories and components', '仓库与组件', 'drivers/repositories'),
      item('UEFI drivers', 'UEFI 驱动', 'drivers/uefi-drivers'),
      item('Built-in XNU drivers', '内置 XNU 驱动', 'drivers/xnu-drivers'),
      item('Kext bundles', 'Kext 包', 'drivers/kexts'),
      item('Device tree matching', '设备树匹配', 'drivers/device-tree-matching'),
    ], true),
    group('XNU kernel', 'XNU 内核', [
      item('Source and patches', '源码与补丁', 'xnu/source-and-patches'),
      item('Patch reference', '补丁参考', 'xnu/patch-reference'),
      item('4 KiB page tables', '4 KiB 页表', 'xnu/four-k-page-tables'),
      item('Boot arguments', '启动参数', 'xnu/boot-arguments'),
    ], true),
    group('Verification and contribution', '验证与贡献', [
      item('QEMU', 'QEMU', 'reference/qemu'),
      item('Troubleshooting', '故障排查', 'reference/troubleshooting'),
      item('Repository layout', '仓库布局', 'contributing/repository'),
      item('Documentation', '文档维护', 'contributing/documentation'),
    ], true),
  ]
  return { build, port, reference }
}

const enTasks = taskSidebars('/', false)
const zhTasks = taskSidebars('/zh/', true)

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
          { text: '移植设备', link: '/zh/porting/', activeMatch: '^/zh/porting/' },
          { text: '构建与启动', link: '/zh/building', activeMatch: '^/zh/(guide/|building)' },
          { text: '设备', link: '/zh/devices/', activeMatch: '^/zh/devices/' },
          { text: '技术参考', link: '/zh/reference/', activeMatch: '^/zh/(reference|drivers|xnu|concepts|contributing)/' },
        ],
        sidebar: {
          '/zh/guide/': zhTasks.build,
          '/zh/building': zhTasks.build,
          '/zh/concepts/': zhTasks.reference,
          '/zh/porting/': zhTasks.port,
          '/zh/drivers/': zhTasks.reference,
          '/zh/xnu/': zhTasks.reference,
          '/zh/devices/': deviceSidebar(true),
          '/zh/reference/': zhTasks.reference,
          '/zh/contributing/': zhTasks.reference,
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
      { text: 'Port a device', link: '/porting/', activeMatch: '^/porting/' },
      { text: 'Build and boot', link: '/building', activeMatch: '^/(guide/|building)' },
      { text: 'Devices', link: '/devices/', activeMatch: '^/devices/' },
      { text: 'Technical reference', link: '/reference/', activeMatch: '^/(reference|drivers|xnu|concepts|contributing)/' },
    ],
    sidebar: {
      '/guide/': enTasks.build,
      '/building': enTasks.build,
      '/concepts/': enTasks.reference,
      '/porting/': enTasks.port,
      '/drivers/': enTasks.reference,
      '/xnu/': enTasks.reference,
      '/devices/': deviceSidebar(false),
      '/reference/': enTasks.reference,
      '/contributing/': enTasks.reference,
    },
    search: {
      provider: 'local',
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/UniXNU/UniXNU' },
      { icon: 'x', link: 'https://x.com/UniXNU_new' },
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
