<template>
  <div class="product-card" @click="$emit('click', product)">
    <div class="product-thumb">
      <img
        :src="resolveAsset(product.images?.[0]) || '/images/placeholder.jpg'"
        :alt="product.title"
        loading="lazy"
      />
    </div>
    <div class="product-body">
      <h3 class="product-title">{{ product.title }}</h3>
      <p class="product-desc">{{ product.description ? (product.description.length > 40 ? product.description.slice(0, 40) + '…' : product.description) : '' }}</p>
      <div class="product-meta">
        <span v-if="product.category" class="meta-tag industry">{{ product.category }}</span>
        <span v-if="product.district" class="meta-tag district">{{ product.district }}</span>
      </div>
      <div class="product-footer">
        <span v-if="product.contact_phone" class="product-phone">📞 {{ product.contact_phone }}</span>
        <span class="product-views">{{ product.view_count || 0 }} 浏览</span>
        <span v-if="product.merchant_name" class="product-merchant">🏪 {{ product.merchant_name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { resolveAsset } from '@/utils/asset'
defineProps<{
  product: {
    id: number
    title: string
    description?: string
    images?: string[]
    category?: string
    district?: string
    view_count?: number
    merchant_name?: string
    contact_phone?: string
  }
}>()

defineEmits<{
  (e: 'click', product: any): void
}>()
</script>

<style scoped>
.product-card {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s, transform 0.2s;
  cursor: pointer;
}

.product-card:active {
  box-shadow: 0 4px 16px rgba(26, 115, 232, 0.15);
  transform: translateY(-1px);
}

.product-thumb {
  width: 100%;
  height: 120px;
  overflow: hidden;
  background: #f0f2f5;
}

.product-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:active .product-thumb img {
  transform: scale(1.03);
}

.product-body {
  padding: 10px 10px 8px;
}

.product-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-desc {
  font-size: 12px;
  color: #888;
  margin: 0 0 6px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}

.meta-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.meta-tag.industry {
  background: #e8f0fe;
  color: #1a73e8;
}

.meta-tag.district {
  background: #f1f3f4;
  color: #5f6368;
}

.product-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 11px;
}

.product-phone {
  color: #1a73e8;
  font-weight: 500;
}

.product-views {
  color: #aaa;
  margin-left: auto;
}

.product-merchant {
  color: #ff9800;
  font-weight: 500;
}
</style>
