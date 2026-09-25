<template>
  <van-tabbar
    v-model="active"
    :fixed="true"
    :border="false"
    :safe-area-inset-bottom="true"
    class="custom-tabbar"
  >
    <van-tabbar-item icon="home-o" @click="go('/')">首页</van-tabbar-item>
    <van-tabbar-item icon="orders-o" @click="go('/products')">产品</van-tabbar-item>
    <van-tabbar-item icon="calendar-o" @click="go('/events')">活动</van-tabbar-item>
    <van-tabbar-item icon="friend-o" @click="go('/profile')">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const active = ref(0)

// 按一级路径前缀归到对应 tab（/products/5 → 产品，/events/7 → 活动），
// 不再用精确匹配（否则详情页查不到 → 兜底落到"首页"选中态，点首页却没反应）
const tabs = [
  { prefix: '/', index: 0 },
  { prefix: '/products', index: 1 },
  { prefix: '/events', index: 2 },
  { prefix: '/profile', index: 3 },
]

function matchTab(path: string): number {
  // 从具体到宽泛匹配；'/' 只匹配首页本身
  if (path === '/') return 0
  for (const t of tabs) {
    if (t.prefix === '/') continue
    if (path === t.prefix || path.startsWith(t.prefix + '/')) return t.index
  }
  return 0
}

watch(() => route.path, (path) => {
  active.value = matchTab(path)
}, { immediate: true })

// 显式导航兜底：van-tabbar-item 的 to 在"active 值与目标一致"时不触发跳转，
// 这里手动 router.push，确保详情页点"首页"一定能回到 /
function go(to: string) {
  active.value = matchTab(to)
  if (route.path !== to) router.push(to)
}
</script>

<style scoped>
.custom-tabbar {
  background: #ffffff !important;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  position: fixed !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  z-index: 99999 !important;
  width: 100% !important;
}

.custom-tabbar :deep(.van-tabbar) {
  position: fixed !important;
  bottom: 0 !important;
  left: 0 !important;
  right: 0 !important;
  width: 100% !important;
  z-index: 99999 !important;
  background: #ffffff !important;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08) !important;
}

.custom-tabbar :deep(.van-tabbar-item) {
  padding-bottom: env(safe-area-inset-bottom, 0) !important;
}

/* 激活态颜色覆盖 */
:deep(.van-tabbar-item--active) {
  color: #1a73e8 !important;
}

:deep(.van-tabbar-item__icon) {
  transition: transform 0.2s;
}

:deep(.van-tabbar-item--active .van-tabbar-item__icon) {
  transform: translateY(-1px);
}
</style>
