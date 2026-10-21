import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import CommunityFooter from './CommunityFooter.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'layout-bottom': () => h(CommunityFooter)
  })
}
