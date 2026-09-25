<template>
  <div class="profile-page">
    <!-- 用户信息卡片 -->
    <div class="user-card" v-if="userStore.isLoggedIn">
      <div class="user-avatar">
        <van-image
          :src="resolveAsset(userStore.userInfo?.avatar_url) || '/images/default-avatar.png'"
          round
          width="60"
          height="60"
        />
      </div>
      <div class="user-info">
        <div class="user-name">{{ userStore.userInfo?.nickname || '未设置昵称' }}</div>
        <van-tag :type="getRoleType(userStore.role)">{{ getRoleLabel(userStore.role) }}</van-tag>
      </div>
      <van-icon name="manager" size="24" color="#fff" @click="showNotifications = true" style="cursor:pointer" />
    </div>
    <div class="login-card" v-else>
      <van-button type="primary" block @click="$router.push('/login')">微信授权登录</van-button>
      <van-divider>或</van-divider>
      <van-button block @click="showSmsLogin = true">手机号登录</van-button>
    </div>

    <!-- 公告栏 -->
    <div class="notice-bar" v-if="announcement">
      <van-notice-bar left-icon="volume-o" :text="announcement" />
    </div>

    <!-- 功能菜单 -->
    <van-cell-group inset v-if="userStore.isLoggedIn">
      <van-cell title="我的报名" is-link @click="$router.push('/events')" />
      <van-cell title="我的产品" is-link v-if="userStore.role === 'merchant'" @click="$router.push('/my-products')" />
      <van-cell title="商户入驻" is-link v-if="userStore.role !== 'merchant' && userStore.role !== 'admin'" @click="$router.push('/merchant-apply')" />

      <!-- 商户申请状态 -->
      <van-cell
        v-if="merchantApp"
        :title="`商户申请：${getStatusText(merchantApp.status)}`"
        is-link
        @click="showMerchantDetail = true"
      >
        <template #right-icon>
          <van-tag :type="getStatusTagType(merchantApp.status)" size="small">{{ getStatusText(merchantApp.status) }}</van-tag>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 退出登录 -->
    <div class="logout-section" v-if="userStore.isLoggedIn">
      <van-button type="danger" block @click="handleLogout">退出登录</van-button>
    </div>

    <!-- 短信登录弹窗 -->
    <van-popup v-model:show="showSmsLogin" position="bottom" round>
      <div class="sms-login">
        <h3>手机号登录</h3>
        <van-field v-model="smsPhone" label="手机号" placeholder="请输入手机号" />
        <van-field v-model="smsCode" label="验证码" placeholder="请输入验证码">
          <template #button>
            <van-button size="small" type="primary" @click="sendSmsCode">发送验证码</van-button>
          </template>
        </van-field>
        <van-button type="primary" block @click="handleSmsLogin">登录</van-button>
      </div>
    </van-popup>

    <!-- 通知列表弹窗 -->
    <van-popup v-model:show="showNotifications" position="bottom" round :style="{ maxHeight: '70vh' }">
      <div class="notifications-panel">
        <div class="notif-header">
          <span>通知</span>
          <van-button size="small" type="primary" @click="markAllReadLocal">全部已读</van-button>
        </div>
        <van-empty v-if="notifications.length === 0" description="暂无通知" />
        <van-cell
          v-for="n in notifications"
          :key="n.id"
          :title="n.title"
          :label="n.content"
          :note="formatTime(n.created_at)"
          :class="{ 'unread': !n.is_read }"
          is-link
          @click="markRead(n.id)"
        />
      </div>
    </van-popup>

    <!-- 商户申请详情弹窗 -->
    <van-popup v-model:show="showMerchantDetail" position="bottom" round>
      <div class="merchant-detail">
        <h3>商户申请详情</h3>
        <van-cell-group inset>
          <van-cell title="商户名称" :value="merchantApp?.shop_name" />
          <van-cell title="联系电话" :value="merchantApp?.contact_phone" />
          <van-cell title="经营地址" :value="merchantApp?.address" />
          <van-cell title="申请状态" :value="getStatusText(merchantApp?.status)" />
          <van-cell v-if="merchantApp?.reject_reason" title="驳回原因" :value="merchantApp.reject_reason" />
        </van-cell-group>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/stores/user'
import { getNotifications, markNotificationRead, markAllRead } from '@/api/users'
import { getMyMerchant } from '@/api/users'
import { smsLogin } from '@/api/auth'
import dayjs from 'dayjs'
import { resolveAsset } from '@/utils/asset'

const router = useRouter()
const userStore = useUserStore()

const showSmsLogin = ref(false)
const smsPhone = ref('')
const smsCode = ref('')
const showNotifications = ref(false)
const showMerchantDetail = ref(false)
const notifications = ref<any[]>([])
const merchantApp = ref<any>(null)
const announcement = ref('')

function getRoleType(role: string) {
  const map: Record<string, string> = {
    visitor: 'default',
    user: '',
    merchant: 'warning',
    admin: 'danger',
  }
  return map[role] || 'default'
}

function getRoleLabel(role: string) {
  const map: Record<string, string> = {
    visitor: '游客',
    user: '普通用户',
    merchant: '会员商户',
    admin: '管理员',
  }
  return map[role] || role
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending_review: '待审核',
    approved: '已通过',
    rejected: '已驳回',
  }
  return map[status] || status
}

function getStatusTagType(status: string) {
  const map: Record<string, string> = {
    pending_review: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return map[status] || 'default'
}

function formatTime(time: string) {
  return dayjs(time).format('MM月DD日 HH:mm')
}

async function loadNotifications() {
  try {
    const res = await getNotifications({ page: 1, page_size: 20 })
    notifications.value = res.items || []
  } catch (e) {
    console.error('加载通知失败', e)
  }
}

async function markRead(id: number) {
  try {
    await markNotificationRead(id)
    const n = notifications.value.find(x => x.id === id)
    if (n) n.is_read = true
  } catch (e) {
    console.error('标记已读失败', e)
  }
}

async function markAllReadLocal() {
  try {
    await markAllRead()
    notifications.value.forEach(n => { n.is_read = true })
    showToast('已全部标为已读')
  } catch (e) {
    console.error('全部已读失败', e)
  }
}

async function loadMerchantApp() {
  try {
    merchantApp.value = await getMyMerchant()
  } catch (e) {
    // ignore
  }
}

async function handleSmsLogin() {
  if (!smsPhone.value || !smsCode.value) {
    showToast('请填写完整信息')
    return
  }
  try {
    await smsLogin(smsPhone.value, smsCode.value)
    await userStore.fetchUserInfo()
    showSmsLogin.value = false
    showToast('登录成功')
  } catch (error: any) {
    showToast(error?.detail || '登录失败')
  }
}

function sendSmsCode() {
  if (!smsPhone.value || smsPhone.value.length !== 11) {
    showToast('请输入正确的手机号')
    return
  }
  showToast('验证码已发送，请关注页面提示')
}

function handleLogout() {
  userStore.logout()
  router.push('/')
  showToast('已退出登录')
}

onMounted(async () => {
  if (userStore.isLoggedIn) {
    await userStore.fetchUserInfo()
    await loadNotifications()
    await loadMerchantApp()
  }
  // 尝试从 localStorage 读取公告（实际应从 API 获取）
  try {
    const res = await fetch('/api/home')
    const data = await res.json()
    if (data.announcement) announcement.value = data.announcement
  } catch (e) {}
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 16px;
  background: linear-gradient(135deg, #ff6b35, #ffa726);
  color: #fff;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
}

.notice-bar {
  margin: 8px 16px;
}

.login-card {
  padding: 40px 16px;
}

.logout-section {
  padding: 20px 16px;
}

.sms-login {
  padding: 20px;
}

.sms-login h3 {
  text-align: center;
  margin-bottom: 16px;
}

.notifications-panel {
  padding: 16px;
  max-height: 60vh;
  overflow-y: auto;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: bold;
}

.unread {
  background: #fff8e1;
}

.merchant-detail {
  padding: 16px;
}

.merchant-detail h3 {
  text-align: center;
  margin-bottom: 16px;
}
</style>
