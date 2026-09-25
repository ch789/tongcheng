<template>
  <div class="event-card" @click="$emit('click', event)">
    <div class="event-thumb">
      <img
        :src="resolveAsset(event.cover_image) || '/images/placeholder.jpg'"
        :alt="event.title"
        loading="lazy"
      />
      <span class="event-status-badge" :class="getStatusClass(event.status)">
        {{ getStatusText(event.status) }}
      </span>
    </div>
    <div class="event-body">
      <h3 class="event-title">{{ event.title }}</h3>
      <p class="event-time">🕐 {{ formatTime(event.start_time) }} · {{ event.location || '地点待定' }}</p>
      <div class="event-footer">
        <span class="event-participants">👥 已有 {{ event.registered_count || 0 }} 人报名</span>
        <span v-if="event.max_participants && event.max_participants > 0" class="event-limit">
          限 {{ event.max_participants }} 人
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import { resolveAsset } from '@/utils/asset'

defineProps<{
  event: {
    id: number
    title: string
    cover_image?: string
    start_time?: string
    location?: string
    status: string
    registered_count?: number
    max_participants?: number
  }
}>()

defineEmits<{
  (e: 'click', event: any): void
}>()

function formatTime(time: string | undefined) {
  if (!time) return '待定'
  return dayjs(time).format('MM月DD日 HH:mm')
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    upcoming: 'default',
    registering: 'success',
    ended: 'default',
    off_shelf: 'default',
  }
  return map[status] || 'default'
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    upcoming: '未开始',
    registering: '报名中',
    ended: '已结束',
    off_shelf: '已下架',
  }
  return map[status] || status
}

function getStatusClass(status: string) {
  const map: Record<string, string> = {
    upcoming: 'status-upcoming',
    registering: 'status-registering',
    ended: 'status-ended',
    off_shelf: 'status-off',
  }
  return map[status] || 'status-upcoming'
}
</script>

<style scoped>
.event-card {
  display: flex;
  gap: 10px;
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  padding: 10px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.event-card:active {
  box-shadow: 0 4px 16px rgba(26, 115, 232, 0.15);
  transform: translateY(-1px);
}

.event-thumb {
  flex-shrink: 0;
  width: 90px;
  height: 90px;
  border-radius: 10px;
  overflow: hidden;
  background: #f0f2f5;
  position: relative;
}

.event-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.event-status-badge {
  position: absolute;
  top: 4px;
  left: 4px;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 600;
  color: #fff;
}

.status-registering { background: #4caf50; }
.status-upcoming  { background: #909399; }
.status-ended     { background: #f56c6c; }
.status-off       { background: #909399; }

.event-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.event-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.event-time {
  font-size: 11px;
  color: #888;
  margin: 0 0 4px;
  line-height: 1.4;
}

.event-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}

.event-participants {
  color: #1a73e8;
  font-weight: 500;
}

.event-limit {
  color: #aaa;
  margin-left: auto;
}
</style>
