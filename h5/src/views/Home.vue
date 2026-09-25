<template>
  <div class="home-page">
    <!-- 蓝色品牌头部 -->
    <div class="brand-header">
      <div class="brand-inner">
        <div class="brand-logo">🏠</div>
        <h1 class="brand-title">同城老乡服务平台</h1>
        <p class="brand-subtitle">团结同乡资源，服务在外老乡</p>
        <p v-if="announcement" class="brand-tagline">找商户、找活动、找同乡服务，一站搞定</p>
      </div>
      <!-- 装饰波浪 -->
      <div class="brand-wave">
        <svg viewBox="0 0 1440 120" preserveAspectRatio="none">
          <path d="M0,60 C360,120 720,0 1080,60 C1260,90 1380,80 1440,60 L1440,120 L0,120 Z" fill="#ffffff"/>
        </svg>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="home-content">

      <!-- 轮播广告卡片 -->
      <div class="carousel-card" v-if="banners.length > 0">
        <van-swipe
          class="banner-swipe"
          :autoplay="3500"
          :show-indicators="true"
          indicator-color="var(--primary-color)"
          lazy-render
        >
          <van-swipe-item v-for="ad in banners" :key="ad.id">
            <div class="banner-wrap" @click="handleAdClick(ad)">
              <img :src="resolveAsset(ad.image)" :alt="ad.title" class="banner-image" />
              <div v-if="ad.title" class="banner-caption">{{ ad.title }}</div>
            </div>
          </van-swipe-item>
        </van-swipe>
      </div>

      <!-- 快捷入口 -->
      <div class="quick-entry-card">
        <div
          v-for="item in quickItems"
          :key="item.key"
          class="entry-item"
          @click="navigateTo(item.path)"
        >
          <div class="entry-icon-wrap">
            <van-icon :name="item.icon" size="26" color="#fff" />
          </div>
          <span class="entry-label">{{ item.label }}</span>
        </div>
      </div>

      <!-- 公告区块 -->
      <div class="notice-card" v-if="announcement">
        <div class="notice-header">
          <span class="notice-title">最新公告</span>
          <span class="notice-dot"></span>
        </div>
        <div class="notice-body">
          <p class="notice-text">{{ announcement }}</p>
        </div>
      </div>

      <!-- 热门推荐 - 产品 -->
      <div class="recommend-section" v-if="hotProducts.length > 0">
        <div class="section-header">
          <span class="section-title">产品展示</span>
          <span class="section-more" @click="$router.push('/products')">查看更多 ›</span>
        </div>
        <div class="product-list">
          <ProductCard
            v-for="product in hotProducts"
            :key="product.id"
            :product="product"
            @click="$router.push(`/products/${product.id}`)"
          />
        </div>
      </div>

      <!-- 热门推荐 - 活动 -->
      <div class="event-section" v-if="hotEvents.length > 0">
        <div class="section-header">
          <span class="section-title">活动报名</span>
          <span class="section-more" @click="$router.push('/events')">查看更多 ›</span>
        </div>
        <div class="event-list">
          <EventCard
            v-for="event in hotEvents"
            :key="event.id"
            :event="event"
            @click="$router.push(`/events/${event.id}`)"
          />
        </div>
      </div>

    </div><!-- /home-content -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getEvents } from '@/api/events'
import { getProducts } from '@/api/products'
import request from '@/api/request'
import { resolveAsset } from '@/utils/asset'
import EventCard from '@/components/EventCard.vue'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()

// Banner广告数据
const banners = ref<Array<{ id: number; title: string; image: string; link?: string }>>([])

// 快捷入口
const quickItems = ref([
  { key: 'products', label: '产品展示', icon: 'shop-o', path: '/products' },
  { key: 'events', label: '活动报名', icon: 'calendar-o', path: '/events' },
  { key: 'merchant', label: '商户入驻', icon: 'shop', path: '/merchant-apply' },
  { key: 'consult', label: '我的咨询', icon: 'service', path: '/profile' },
])

// 热门产品
const hotProducts = ref<any[]>([])

// 热门活动
const hotEvents = ref<any[]>([])

// 平台Slogan和公告（来自首页API）
const slogan = ref('团结同乡资源，服务在外老乡\n找商户、找活动、找同乡服务，一步搞定')
const announcement = ref('同城老乡服务平台正式上线！欢迎在外的老乡注册使用。')

async function loadHome() {
  try {
    // 走共享 request 实例（baseURL 读 VITE_API_URL，同域/跨域零改；拦截器已带 token 并解包 data）
    const data: any = await request.get('/home')
    if (data.slogan) slogan.value = data.slogan
    if (data.announcement) announcement.value = data.announcement
    if (data.ads && data.ads.length > 0) {
      banners.value = data.ads.map((ad: any) => ({
        id: ad.id,
        title: ad.title,
        image: ad.image,
        link: ad.link,
      }))
    }
  } catch (e) {
    console.error('加载首页内容失败', e)
  }

  // 热门产品（取最近2个）
  try {
    const productsRes = await getProducts({ page: 1, page_size: 2 })
    hotProducts.value = (productsRes.items || []).map((p: any) => ({
      id: p.id,
      title: p.title,
      merchant_name: p.merchant_name,
      category: p.industry_name,
      district: p.area,
      images: p.images && p.images.length > 0 ? p.images : [],
      view_count: p.view_count,
    }))
  } catch (e) {
    console.error('加载产品失败', e)
  }

  // 热门活动（取最近2个）
  try {
    const eventsRes = await getEvents({ page: 1, page_size: 2 })
    hotEvents.value = (eventsRes.items || []).map((e: any) => ({
      id: e.id,
      title: e.title,
      event_type: '',
      district: '',
      start_time: e.start_time,
      status: e.status,
      cover_image: e.cover_image,
      participant_count: e.registered_count,
      max_participants: e.max_participants,
    }))
  } catch (e) {
    console.error('加载活动失败', e)
  }
}

function navigateTo(path: string) {
  router.push(path)
}

function handleAdClick(ad: any) {
  if (ad.link) {
    if (ad.link.startsWith('http')) {
      window.open(ad.link, '_blank')
    } else {
      router.push(ad.link)
    }
  }
}

onMounted(() => {
  loadHome()
})
</script>

<style scoped lang="scss">
/* ── 页面外层 ── */
.home-page {
  min-height: 100vh;
  background: var(--bg-color);
  padding-bottom: calc(60px + env(safe-area-inset-bottom));
  /* 宽屏（iPad/桌面）下不无限拉伸：内容居中、最大宽 768px，两侧留白 */
  max-width: 768px;
  margin: 0 auto;
}

/* ── 蓝色品牌头部 ── */
.brand-header {
  position: relative;
  background: linear-gradient(135deg, #1a73e8 0%, #4a9af5 60%, #7bb8f7 100%);
  /* 随视口缩放：窄屏 32/48，宽屏更大，避免又矮又挤 */
  padding: clamp(32px, 6vw, 56px) clamp(20px, 4vw, 40px) clamp(48px, 8vw, 80px);
  text-align: center;
  color: #fff;
  overflow: hidden;
}

.brand-header::before {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 160px;
  height: 160px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
}

.brand-header::after {
  content: '';
  position: absolute;
  bottom: -60px;
  left: -30px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 50%;
}

.brand-inner {
  position: relative;
  z-index: 1;
}

.brand-logo {
  font-size: clamp(40px, 7vw, 64px);
  margin-bottom: 8px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.brand-title {
  font-size: clamp(22px, 3.6vw, 34px);
  font-weight: 700;
  margin: 0 0 6px;
  letter-spacing: 1px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.brand-subtitle {
  font-size: clamp(15px, 2.4vw, 22px);
  font-weight: 600;
  margin: 0 0 4px;
  opacity: 0.95;
}

.brand-tagline {
  font-size: 12px;
  opacity: 0.75;
  margin: 0;
  white-space: pre-line;
}

.brand-wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  line-height: 0;
}

/* ── 内容区 ── */
.home-content {
  position: relative;
  margin-top: 0;
  z-index: 2;
}

/* ── 轮播卡片 ── */
.carousel-card {
  margin: 0 12px 12px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.banner-swipe {
  /* 高度随视口自适应：手机小屏 150px，越宽越高（2.5:1 贴合轮播图），
     宽屏/iPad 下 banner 不再被拉满裁切 */
  height: clamp(150px, 32vw, 300px);
}

.banner-wrap {
  width: 100%;
  height: 100%;
  cursor: pointer;
  position: relative;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.banner-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px 12px;
  background: linear-gradient(transparent, rgba(0,0,0,0.5));
  color: #fff;
  font-size: clamp(12px, 1.5vw, 14px);
  font-weight: 500;
}

/* ── 快捷入口卡片 ── */
.quick-entry-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  margin: 0 12px 12px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 18px 8px 14px;
}

.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 2px;
  border-radius: var(--radius-md);
  transition: background 0.2s;

  &:active {
    background: var(--primary-light);
  }
}

.entry-icon-wrap {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 8px rgba(26, 115, 232, 0.2);
}

/* 四种渐变色对应四个入口 */
.entry-item:nth-child(1) .entry-icon-wrap {
  background: linear-gradient(135deg, #1a73e8, #4a9af5);
}
.entry-item:nth-child(2) .entry-icon-wrap {
  background: linear-gradient(135deg, #ff9800, #ffb74d);
}
.entry-item:nth-child(3) .entry-icon-wrap {
  background: linear-gradient(135deg, #4caf50, #81c784);
}
.entry-item:nth-child(4) .entry-icon-wrap {
  background: linear-gradient(135deg, #9c27b0, #ba68c8);
}

.entry-label {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 500;
  text-align: center;
  line-height: 1.3;
}

/* ── 公告卡片 ── */
.notice-card {
  margin: 0 12px 12px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.notice-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px 8px;
  border-bottom: 1px solid var(--border-color);
}

.notice-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.notice-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.notice-body {
  padding: 10px 14px 12px;
}

.notice-text {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.7;
  margin: 0;
  word-break: break-all;
}

/* ── 区块标题 ── */
.recommend-section,
.event-section {
  margin: 0 12px 12px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  position: relative;
  padding-left: 10px;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 2px;
    bottom: 2px;
    width: 3px;
    border-radius: 2px;
    background: var(--primary-color);
  }
}

.section-more {
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: background 0.2s;

  &:active {
    background: var(--primary-light);
    color: var(--primary-color);
  }
}

/* ── 产品列表 ── */
.product-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

/* ── 活动列表 ── */
.event-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
