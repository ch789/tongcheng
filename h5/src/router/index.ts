import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', keepAlive: true },
  },
  {
    path: '/products',
    component: () => import('@/views/Products.vue'),
    meta: { title: '产品', keepAlive: true },
  },
  {
    path: '/products/:id',
    component: () => import('@/views/ProductDetail.vue'),
    meta: { title: '产品详情' },
  },
  {
    path: '/events',
    component: () => import('@/views/Events.vue'),
    meta: { title: '活动', keepAlive: true },
  },
  {
    path: '/events/:id',
    component: () => import('@/views/EventDetail.vue'),
    meta: { title: '活动详情' },
  },
  {
    path: '/profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '我的', requiresAuth: true },
  },
  {
    path: '/login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/merchant-apply',
    component: () => import('@/views/MerchantApply.vue'),
    meta: { title: '商户入驻' },
  },
  {
    path: '/membership',
    component: () => import('@/views/Membership.vue'),
    meta: { title: '会员权益' },
  },
  {
    path: '/my-products',
    component: () => import('@/views/MyProducts.vue'),
    meta: { title: '我的产品', requiresAuth: true },
  },
  {
    path: '/publish-product',
    component: () => import('@/views/PublishProduct.vue'),
    meta: { title: '发布产品', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局路由守卫
router.beforeEach((to, _from, next) => {
  document.title = to.meta.title || '同城老乡服务平台'
  const userStore = useUserStore()

  // 需要登录的页面
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
