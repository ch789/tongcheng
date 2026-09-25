<template>
  <div class="events-page">
    <!-- 顶部蓝色标题栏 -->
    <div class="page-header">
      <span class="page-title">活动报名</span>
    </div>

    <!-- 状态筛选 Tabs -->
    <div class="tabs-wrap">
      <van-tabs
        v-model:active="activeTab"
        @change="handleTabChange"
        sticky
        offset-top="0"
        class="custom-tabs"
      >
        <van-tab title="全部" name="all" />
        <van-tab title="进行中" name="registering" />
        <van-tab title="即将开始" name="upcoming" />
        <van-tab title="已结束" name="ended" />
      </van-tabs>
    </div>

    <!-- 活动列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <div class="event-list">
          <EventCard
            v-for="event in events"
            :key="event.id"
            :event="event"
            @click="$router.push(`/events/${event.id}`)"
          />
        </div>
        <div v-if="events.length === 0 && !loading" class="empty-state">
          <van-empty description="暂无活动" />
        </div>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getEvents } from '@/api/events'
import EventCard from '@/components/EventCard.vue'

const activeTab = ref('all')
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const events = ref<any[]>([])
const page = ref(1)
const size = ref(15)

const statusMap: Record<string, string> = {
  all: '',
  registering: 'registering',
  upcoming: 'upcoming',
  ended: 'ended',
}

async function loadEvents() {
  try {
    const res = await getEvents({
      page: page.value,
      page_size: size.value,
      status: statusMap[activeTab.value],
    })
    const items = (res.items || []).map((e: any) => ({
      id: e.id,
      title: e.title,
      event_type: '',
      district: e.location || '',
      start_time: e.start_time,
      status: e.status,
      cover_image: e.cover_image,
      participant_count: e.registered_count,
      max_participants: e.max_participants,
    }))
    if (page.value === 1) {
      events.value = items
    } else {
      events.value = [...events.value, ...items]
    }
    finished.value = items.length < size.value
  } catch (error) {
    console.error('加载活动失败', error)
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onLoad() {
  loading.value = true
  loadEvents()
}

function onRefresh() {
  page.value = 1
  finished.value = false
  events.value = []
  loadEvents()
}

function handleTabChange(name: string) {
  activeTab.value = name
  page.value = 1
  events.value = []
  finished.value = false
  loadEvents()
}

onMounted(() => {
  loadEvents()
})
</script>

<style scoped lang="scss">
.events-page {
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

/* ── 状态筛选 Tabs ── */
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

/* ── 活动列表 ── */
.event-list {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}
</style>
