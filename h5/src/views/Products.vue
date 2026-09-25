<template>
  <div class="products-page">
    <!-- 顶部蓝色标题栏 -->
    <div class="page-header">
      <span class="page-title">产品展示</span>
    </div>

    <!-- 搜索框 -->
    <div class="search-wrap">
      <van-search
        v-model="searchKey"
        placeholder="搜索产品、商户"
        shape="round"
        @search="handleSearch"
        @clear="handleClear"
        class="custom-search"
      />
    </div>

    <!-- 行业标签快速筛选 -->
    <div class="tabs-wrap">
      <van-tabs
        v-model:active="selectedIndustryIdx"
        @change="handleIndustryChange"
        sticky
        offset-top="0"
        class="custom-tabs"
      >
        <van-tab title="全部" :name="0" />
        <van-tab
          v-for="(ind, idx) in industries"
          :key="ind.id"
          :title="ind.name"
          :name="idx + 1"
        />
      </van-tabs>
    </div>

    <!-- 产品列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div class="product-grid">
          <ProductCard
            v-for="product in products"
            :key="product.id"
            :product="product"
            @click="$router.push(`/products/${product.id}`)"
          />
        </div>
        <div v-if="products.length === 0 && !loading" class="empty-state">
          <van-empty description="暂无产品" />
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { getProducts, getIndustries } from '@/api/products'
import ProductCard from '@/components/ProductCard.vue'

const searchKey = ref('')
const selectedIndustryIdx = ref(0)
const industries = ref<{ id: number; name: string }[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)

const page = ref(1)
const size = ref(15)
const products = ref<any[]>([])

async function loadIndustries() {
  try {
    const data = await getIndustries()
    industries.value = data || []
  } catch (e) {
    console.error('加载行业失败', e)
  }
}

async function loadProducts() {
  try {
    const params: any = { page: page.value, page_size: size.value }
    if (searchKey.value) params.keyword = searchKey.value
    if (selectedIndustryIdx.value > 0) {
      params.industry_id = industries.value[selectedIndustryIdx.value - 1].id
    }
    const res = await getProducts(params)
    const items = (res.items || []).map((p: any) => ({
      id: p.id,
      title: p.title,
      description: p.description,
      images: p.images && p.images.length > 0 ? p.images : [],
      category: p.industry_name,
      district: p.area,
      merchant_name: p.merchant_name,
      view_count: p.view_count,
    }))
    if (page.value === 1) {
      products.value = items
    } else {
      products.value = [...products.value, ...items]
    }
    finished.value = items.length < size.value
  } catch (error) {
    showToast('加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onLoad() {
  loading.value = true
  loadProducts()
}

function onRefresh() {
  page.value = 1
  finished.value = false
  products.value = []
  loadProducts()
}

function handleSearch() {
  page.value = 1
  products.value = []
  finished.value = false
  loadProducts()
}

function handleClear() {
  searchKey.value = ''
  handleSearch()
}

function handleIndustryChange(idx: number) {
  selectedIndustryIdx.value = idx
  page.value = 1
  products.value = []
  finished.value = false
  loadProducts()
}

onMounted(() => {
  loadIndustries()
  loadProducts()
})
</script>

<style scoped lang="scss">
.products-page {
  min-height: 100vh;
  background: var(--bg-color);
  padding-bottom: calc(60px + env(safe-area-inset-bottom));
}

/* ── 页面标题栏 ── */
.page-header {
  background: linear-gradient(135deg, #1a73e8, #4a9af5);
  padding: 12px 16px;
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

/* ── 搜索框 ── */
.search-wrap {
  padding: 10px 12px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.custom-search :deep(.van-search__content) {
  background: #f5f7fa;
  border-radius: 20px;
}

/* ── 行业筛选 Tabs ── */
.tabs-wrap {
  background: #fff;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 9;
}

.custom-tabs :deep(.van-tabs__wrap) {
  background: #fff;
}

.custom-tabs :deep(.van-tab--active) {
  color: var(--primary-color) !important;
  font-weight: 600;
}

.custom-tabs :deep(.van-tabs__line) {
  background: var(--primary-color) !important;
}

/* ── 产品网格 ── */
.product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 10px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}
</style>
