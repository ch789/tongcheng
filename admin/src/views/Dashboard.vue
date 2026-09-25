<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #409EFF">
            <el-icon size="24"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">注册用户</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #67C23A">
            <el-icon size="24"><Goods /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalProducts }}</div>
            <div class="stat-label">产品数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #E6A23C">
            <el-icon size="24"><Calendar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalActivities }}</div>
            <div class="stat-label">活动数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: #F56C6C">
            <el-icon size="24"><Bell /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingReview }}</div>
            <div class="stat-label">待审核</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>快速操作</template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/admin/products/review')">审核产品</el-button>
            <el-button type="success" @click="$router.push('/admin/activities')">创建活动</el-button>
            <el-button type="warning" @click="$router.push('/admin/merchants')">商户审核</el-button>
            <el-button @click="$router.push('/admin/home')">编辑首页</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>平台公告</template>
          <div class="notice">
            <p>欢迎使用同城老乡服务平台管理后台！</p>
            <p style="margin-top: 8px; color: #999; font-size: 13px;">V1.0 MVP + V1.5 版本已就绪</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const stats = ref({
  totalUsers: 0,
  totalProducts: 0,
  totalActivities: 0,
  pendingReview: 0,
})

onMounted(async () => {
  try {
    const [users, products, activities] = await Promise.all([
      api.get('/admin/users?page=1&page_size=1'),
      api.get('/admin/products?page=1&page_size=1'),
      api.get('/admin/activities?page=1&page_size=1'),
    ])
    stats.value.totalUsers = users.total || 0
    stats.value.totalProducts = products.total || 0
    stats.value.totalActivities = activities.total || 0

    // 统计待审核产品数量
    try {
      const pendingProducts = await api.get('/admin/products?page=1&page_size=1&status=pending_review')
      stats.value.pendingReview = pendingProducts.total || 0
    } catch (e) {
      console.error('加载待审核数量失败', e)
    }
  } catch (e) {
    console.error('加载统计数据失败', e)
  }
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.notice p {
  color: #666;
  line-height: 1.6;
}
</style>
