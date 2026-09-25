<template>
  <div class="my-products-page">
    <van-nav-bar title="我的产品" left-arrow @click-left="$router.back()" />

    <!-- 状态统计 -->
    <van-tabs v-model:active="activeTab" @change="handleTabChange">
      <van-tab title="全部" name="all" />
      <van-tab title="待审核" name="pending_review" />
      <van-tab title="已通过" name="approved" />
      <van-tab title="已驳回" name="rejected" />
      <van-tab title="已下架" name="off_shelf" />
    </van-tabs>

    <!-- 产品列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div class="product-list">
          <van-card
            v-for="product in products"
            :key="product.id"
            :title="product.title"
            :desc="product.description || '暂无描述'"
            :thumb="resolveAsset(product.images?.[0]) || '/images/placeholder.jpg'"
            @click="goToDetail(product.id)"
            clickable
          >
            <template #tags>
              <van-tag :type="getStatusType(product.status)">{{ getStatusText(product.status) }}</van-tag>
              <van-tag v-if="product.industry_name" size="medium">{{ product.industry_name }}</van-tag>
              <van-tag v-if="product.area" size="medium" type="default">{{ product.area }}</van-tag>
            </template>
            <template #footer>
              <span class="product-meta">
                <van-icon name="eye" /> {{ product.view_count || 0 }} 浏览
              </span>
              <span v-if="product.reject_reason" class="reject-reason">
                驳回原因: {{ product.reject_reason }}
              </span>
            </template>
          </van-card>
        </div>
        <div v-if="products.length === 0 && !loading" class="empty-state">
          <van-empty description="暂无产品" />
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 发布产品按钮 -->
    <div class="fixed-btn" @click="$router.push('/publish-product')">
      <van-icon name="plus" /> 发布产品
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getMyProducts } from '@/api/products'
import { useUserStore } from '@/stores/user'
import { resolveAsset } from '@/utils/asset'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('all')
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const products = ref<any[]>([])

const statusMap: Record<string, string> = {
  all: '',
  pending_review: 'pending_review',
  approved: 'approved',
  rejected: 'rejected',
  off_shelf: 'off_shelf',
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    pending_review: 'warning',
    approved: 'success',
    rejected: 'danger',
    off_shelf: 'info',
  }
  return map[status] || 'default'
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending_review: '待审核',
    approved: '已通过',
    rejected: '已驳回',
    off_shelf: '已下架',
  }
  return map[status] || status
}

async function loadProducts() {
  if (!userStore.isLoggedIn) {
    showToast('请先登录')
    router.push('/login')
    return
  }

  loading.value = true
  try {
    const res = await getMyProducts()
    const filtered = activeTab.value === 'all'
      ? res
      : res.filter((p: any) => p.status === activeTab.value)

    if (activeTab.value === 'all' || activeTab.value === statusMap[activeTab.value]) {
      products.value = filtered
    } else {
      products.value = filtered
    }

    finished.value = true
  } catch (error: any) {
    showToast(error?.detail || '加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onLoad() {
  loadProducts()
}

function onRefresh() {
  products.value = []
  loadProducts()
}

function handleTabChange(name: string) {
  activeTab.value = name
  products.value = []
  finished.value = false
  loadProducts()
}

function goToDetail(id: number) {
  router.push(`/products/${id}`)
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.my-products-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 80px;
}

.product-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.product-meta {
  font-size: 12px;
  color: #999;
}

.reject-reason {
  display: block;
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
}
</style>
