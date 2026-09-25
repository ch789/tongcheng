<template>
  <el-container class="admin-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span class="logo-icon">🏠</span>
        <span class="logo-text">同城老乡服务平台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        :router="true"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-sub-menu index="home">
          <template #title>
            <el-icon><HomeFilled /></el-icon>
            <span>首页管理</span>
          </template>
          <el-menu-item index="/admin/home">首页内容</el-menu-item>
          <el-menu-item index="/admin/ads">广告轮播</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="product">
          <template #title>
            <el-icon><Goods /></el-icon>
            <span>产品管理</span>
          </template>
          <el-menu-item index="/admin/products/review">待审核产品</el-menu-item>
          <el-menu-item index="/admin/products/list">全部产品</el-menu-item>
          <el-menu-item index="/admin/products/industries">行业字典</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="activity">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>活动管理</span>
          </template>
          <el-menu-item index="/admin/activities">活动列表</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="user">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/admin/users">用户列表</el-menu-item>
          <el-menu-item index="/admin/merchants">商户入驻审核</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <span class="admin-name">管理员</span>
          <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '管理后台')

function handleLogout() {
  localStorage.removeItem('token')
  router.push('/admin/login')
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', sans-serif; background: #f0f2f5; }
</style>

<style scoped>
.admin-layout {
  height: 100vh;
}

.sidebar {
  background: #304156;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #263445;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  color: #fff;
  font-size: 14px;
  font-weight: bold;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.page-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-name {
  font-size: 14px;
  color: #666;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
