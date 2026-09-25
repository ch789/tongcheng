<template>
  <div class="product-detail" v-if="product">
    <van-swipe class="product-swipe" :autoplay="4000" indicator-color="#ff6b35" v-if="product.images?.length > 0">
      <van-swipe-item v-for="(img, i) in product.images" :key="i">
        <img :src="resolveAsset(img)" class="product-image" />
      </van-swipe-item>
    </van-swipe>
    <div v-else class="product-placeholder">
      <van-icon name="photo-o" size="60" color="#ddd" />
    </div>

    <div class="product-info">
      <div class="product-title">{{ product.title }}</div>
      <div class="product-meta">
        <span class="product-merchant" v-if="product.merchant_name">🏪 {{ product.merchant_name }}</span>
        <van-tag v-if="product.category" size="medium">{{ product.category }}</van-tag>
        <van-tag v-if="product.district" size="medium" type="default">{{ product.district }}</van-tag>
      </div>
      <div class="product-desc" v-html="product.description" v-if="product.description"></div>
    </div>

    <van-divider />

    <div class="contact-section" v-if="product.contact_phone">
      <van-cell-group inset>
        <van-cell title="联系电话" :value="product.contact_phone" is-link @click="callPhone" />
        <van-cell title="浏览量" :value="`${product.view_count || 0} 次`" />
      </van-cell-group>
    </div>

    <div class="action-section">
      <van-button type="primary" block @click="contactMerchant">联系商家</van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { showToast } from 'vant'
import { getProduct } from '@/api/products'
import { resolveAsset } from '@/utils/asset'

const route = useRoute()
const product = ref<any>(null)

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    product.value = await getProduct(id)
  } catch (error: any) {
    showToast(error?.detail || '加载失败')
  }
})

function callPhone() {
  if (product.value?.contact_phone) {
    window.location.href = `tel:${product.value.contact_phone}`
  }
}

function contactMerchant() {
  callPhone()
}
</script>

<style scoped>
.product-detail {
  min-height: 100vh;
  background: #fff;
  padding-bottom: 20px;
}

.product-swipe {
  height: 300px;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f5f6f8;
}

.product-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.product-info {
  padding: 16px;
}

.product-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.product-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.product-merchant {
  font-size: 13px;
  color: #666;
}

.product-desc {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
}

.contact-section {
  padding: 0 16px;
}

.action-section {
  padding: 16px;
}
</style>
