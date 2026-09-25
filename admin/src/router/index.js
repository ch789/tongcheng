import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 根路径：落到登录页，避免 "No match found for path '/'" 白屏
  // （裸 /admin 由下方 layout 路由的子 { path:'', redirect:'/admin/dashboard' } 处理）
  { path: '/', redirect: '/admin/login' },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('@/views/Login.vue') },
  {
    path: '/admin',
    component: () => import('@/views/Layout.vue'),
    meta: { requireAuth: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '数据概览' } },
      { path: 'home', name: 'HomeManage', component: () => import('@/views/HomeManage.vue'), meta: { title: '首页内容管理' } },
      { path: 'ads', name: 'AdManage', component: () => import('@/views/AdManage.vue'), meta: { title: '广告轮播管理' } },
      { path: 'products/review', name: 'ProductReview', component: () => import('@/views/ProductManage.vue'), meta: { title: '产品审核' } },
      { path: 'products/list', name: 'ProductList', component: () => import('@/views/ProductList.vue'), meta: { title: '全部产品' } },
      { path: 'products/industries', name: 'IndustryManage', component: () => import('@/views/IndustryManage.vue'), meta: { title: '行业字典管理' } },
      { path: 'activities', name: 'ActivityManage', component: () => import('@/views/ActivityManage.vue'), meta: { title: '活动管理' } },
      { path: 'users', name: 'UserManage', component: () => import('@/views/UserManage.vue'), meta: { title: '用户管理' } },
      { path: 'merchants', name: 'MerchantManage', component: () => import('@/views/MerchantManage.vue'), meta: { title: '商户入驻审核' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path.startsWith('/admin') && !to.path.includes('login') && !token) {
    next('/admin/login')
  } else {
    next()
  }
})

export default router
