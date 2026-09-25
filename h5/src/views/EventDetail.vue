<template>
  <div class="event-detail" v-if="event">
    <van-swipe class="event-swipe" :autoplay="4000" v-if="event.cover_image">
      <van-swipe-item>
        <img :src="resolveAsset(event.cover_image)" class="event-cover" />
      </van-swipe-item>
    </van-swipe>

    <div class="event-info">
      <div class="event-status" :class="event.status">
        {{ getStatusText(event.status) }}
      </div>
      <h1 class="event-title">{{ event.title }}</h1>
      <div class="event-meta">
        <van-icon name="clock-o" /> {{ formatTime(event.start_time) }} ~ {{ formatTime(event.end_time) }}
      </div>
      <div class="event-meta" v-if="event.location">
        <van-icon name="location-o" /> {{ event.location }}
      </div>
      <div class="event-meta">
        <van-icon name="friends-o" /> 已报名 {{ event.registered_count }} 人
        <span v-if="event.max_participants !== null && event.max_participants > 0"> / 最多 {{ event.max_participants }}</span>
      </div>
    </div>

    <van-divider />
    <div class="event-desc" v-html="event.content" v-if="event.content"></div>
    <van-divider />

    <div class="action-section">
      <van-button
        type="primary"
        block
        :disabled="!canRegister"
        @click="showRegister = true"
      >
        {{ getButtonText() }}
      </van-button>
    </div>
  </div>

  <!-- 报名表单弹窗 -->
  <van-popup v-model:show="showRegister" position="bottom" round>
    <div class="register-form">
      <h3>活动报名</h3>
      <van-field v-model="form.name" label="姓名" placeholder="请输入姓名" required />
      <van-field v-model="form.phone" label="联系电话" placeholder="请输入手机号" required type="tel" />
      <van-field v-model="form.area" label="所在区域" placeholder="如：南开区" required>
        <template #button>
          <van-button size="small" type="primary" @click="showAreaPicker = true">选择</van-button>
        </template>
      </van-field>
      <van-field v-model="form.register_type" label="报名类型" readonly is-link @click="showTypePicker = true" :value="form.register_type === 'personal' ? '个人' : '商户'" />
      <van-field v-model="form.interest" label="意向参与内容" placeholder="请描述您的参与意向" type="textarea" rows="2" />
      <van-field v-model="form.remark" label="备注" placeholder="如有需要请填写" />
      <van-button type="primary" block @click="submitRegister">确认报名</van-button>
    </div>
  </van-popup>

  <!-- 区域选择器 -->
  <van-popup v-model:show="showAreaPicker" position="bottom">
    <van-picker
      :columns="areaOptions"
      @confirm="onAreaConfirm"
      @cancel="showAreaPicker = false"
    />
  </van-popup>

  <!-- 报名类型选择器 -->
  <van-popup v-model:show="showTypePicker" position="bottom">
    <van-picker
      :columns="typeOptions"
      @confirm="onTypeConfirm"
      @cancel="showTypePicker = false"
    />
  </van-popup>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import dayjs from 'dayjs'
import { getEvent, registerEvent } from '@/api/events'
import { useUserStore } from '@/stores/user'
import { resolveAsset } from '@/utils/asset'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const event = ref<any>(null)
const showRegister = ref(false)
const showAreaPicker = ref(false)
const showTypePicker = ref(false)

const form = ref({
  register_type: 'personal',
  name: '',
  phone: '',
  area: '',
  interest: '',
  remark: '',
})

const areaOptions = [
  { text: '南开区', value: '南开区' },
  { text: '河西区', value: '河西区' },
  { text: '滨海新区', value: '滨海新区' },
  { text: '和平区', value: '和平区' },
  { text: '河北区', value: '河北区' },
  { text: '红桥区', value: '红桥区' },
  { text: '东丽区', value: '东丽区' },
  { text: '西青区', value: '西青区' },
]

const typeOptions = [
  { text: '个人', value: 'personal' },
  { text: '商户', value: 'merchant' },
]

const canRegister = computed(() => {
  if (!event.value) return false
  const s = event.value.status
  return s === 'registering' || s === 'upcoming'
})

function getStatusText(status: string) {
  const map: Record<string, string> = {
    upcoming: '未开始',
    registering: '报名中',
    ended: '已结束',
    off_shelf: '已下架',
  }
  return map[status] || status
}

function getButtonText() {
  if (!event.value) return '报名中'
  if (!canRegister.value) return '报名已结束'
  if (event.value.max_participants && event.value.registered_count >= event.value.max_participants) {
    return '已满员'
  }
  return '立即报名'
}

function formatTime(time: string | null | undefined) {
  if (!time) return '待定'
  return dayjs(time).format('MM月DD日 HH:mm')
}

async function submitRegister() {
  if (!userStore.isLoggedIn) {
    showToast('请先登录')
    router.push('/login')
    return
  }
  if (!form.value.name || !form.value.phone || !form.value.area) {
    showToast('请填写完整信息')
    return
  }
  try {
    await registerEvent(event.value.id, form.value)
    showToast('报名成功')
    showRegister.value = false
    const id = Number(route.params.id)
    event.value = await getEvent(id)
  } catch (error: any) {
    showToast(error?.detail || '报名失败，请重试')
  }
}

function onAreaConfirm({ selectedOptions }: any) {
  if (selectedOptions && selectedOptions.length > 0) {
    form.value.area = selectedOptions[0].value
  }
  showAreaPicker.value = false
}

function onTypeConfirm({ selectedOptions }: any) {
  if (selectedOptions && selectedOptions.length > 0) {
    form.value.register_type = selectedOptions[0].value
  }
  showTypePicker.value = false
}

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    event.value = await getEvent(id)
    // 预填充用户信息
    if (userStore.userInfo) {
      form.value.name = userStore.userInfo.nickname || ''
      form.value.phone = ''
    }
  } catch (error) {
    showToast('加载失败')
  }
})
</script>

<style scoped>
.event-detail {
  min-height: 100vh;
  background: #fff;
  padding-bottom: 20px;
}

.event-swipe {
  height: 220px;
}

.event-cover {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f5f6f8;
}

.event-info {
  padding: 16px;
}

.event-status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 8px;
}

.event-status.upcoming { background: #e8f5e9; color: #4caf50; }
.event-status.registering { background: #e3f2fd; color: #2196f3; }
.event-status.ended { background: #ffebee; color: #f44336; }
.event-status.off_shelf { background: #f5f5f5; color: #999; }

.event-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 8px 0;
}

.event-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #666;
  margin-bottom: 6px;
}

.event-desc {
  padding: 0 16px;
  font-size: 14px;
  color: #555;
  line-height: 1.8;
}

.action-section {
  padding: 16px;
}

.register-form {
  padding: 20px;
}

.register-form h3 {
  margin-bottom: 16px;
  text-align: center;
}
</style>
