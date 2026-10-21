<script setup lang="ts">
import { useData } from 'vitepress'

const { lang } = useData()
const qq = 'https://qun.qq.com/universal-share/share?ac=1&authKey=Pubz23DOCY76nxjlGuSms2zesk4jRvas4zrXJRYk7omf7CprXbGQigLEI%2BCoYR8D&busi_data=eyJncm91cENvZGUiOiIxMTI2MTE2NzU5IiwidG9rZW4iOiJwSHJsUDN1UnN2Vi8yM210TjJRbzBIcERmcUpyOS9lb0hHVVpadWdvVFdScVpSYUFLT1YzTk5TWC9mN2xWYmtIIiwidWluIjoiMzE1MTEwOTc0MSJ9&data=_cJgr-jX9yJ2-GXwVjRN5FOhDyk5B-HAfIk5LSunbW_XkkmKqNXbpH33wzP93J0p9DI1fbjgBUrUfTVhwDcxjg&svctype=4&tempid=h5_group_info'
</script>

<template>
  <div class="community-footer">
    <a :href="qq" target="_blank" rel="noopener">{{ lang.startsWith('zh') ? '加入 QQ 群' : 'Join the QQ group' }}</a>
  </div>
</template>

<style scoped>
.community-footer {
  border-top: 1px solid var(--vp-c-gutter);
  padding: 18px 24px;
  text-align: center;
  font-size: 14px;
}

.community-footer a {
  color: var(--vp-c-brand-1);
  text-decoration: none;
}

.community-footer a:hover {
  text-decoration: underline;
}
</style>
