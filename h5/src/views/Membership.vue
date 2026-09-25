<template>
  <div class="membership-page">
    <van-nav-bar title="会员权益" left-arrow @click-left="$router.back()" />

    <!-- 当前会员状态 -->
    <div class="membership-status">
      <div class="status-card" :class="userStore.membershipTier">
        <div class="tier-label">{{ getTierLabel(userStore.membershipTier) }}</div>
        <div class="tier-desc" v-if="userStore.membershipTier !== 'free'">
          有效期至: {{ formatExpiry() }}
        </div>
        <div class="tier-desc" v-else>
          升级会员享更多权益
        </div>
      </div>
    </div>

    <!-- 权益对比 -->
    <div class="权益-card">
      <h3>会员权益对比</h3>
      <van-cell-group inset>
        <van-cell title="产品发布" label="免费: 5个/月 | 基础: 20个/月 | 高级: 不限 | 钻石: 不限+广告位" />
        <van-cell title="活动报名" label="优先报名权（高级/钻石）" />
        <van-cell title="数据分析" label="基础数据（基础）| 精准分析（高级）| 专属顾问（钻石）" />
        <van-cell title="客服响应" label="优先客服（基础+）" />
      </van-cell-group>
    </div>

    <!-- 会员套餐 -->
    <div class="plans-card">
      <h3>选择会员套餐</h3>
      <van-cell-group inset>
        <van-cell
          v-for="plan in plans"
          :key="plan.tier"
          :title="plan.name"
          :label="`¥${plan.monthly}/月`"
          :value="plan.tier === userStore.membershipTier ? '当前等级' : '选择'"
          is-link
          @click="selectPlan(plan)"
        >
          <template #icon>
            <van-tag :type="getTagType(plan.tier)">{{ plan.name }}</van-tag>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 申请按钮 -->
    <div style="padding: 16px;" v-if="userStore.membershipTier === 'free'">
      <van-button type="primary" block @click="applyMembership">申请会员</van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { showToast } from 'vant'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const plans = ref([
  { tier: 'basic', name: '普通会员', monthly: 99, yearly: 999 },
  { tier: 'advanced', name: '高级会员', monthly: 299, yearly: 2999 },
  { tier: 'diamond', name: '钻石会员', monthly: 999, yearly: 9999 },
])

function getTierLabel(tier: string) {
  const map: Record<string, string> = {
    free: '普通用户',
    basic: '普通会员',
    advanced: '高级会员',
    diamond: '钻石会员',
  }
  return map[tier] || '普通用户'
}

function getTagType(tier: string) {
  const map: Record<string, string> = {
    basic: 'primary',
    advanced: 'success',
    diamond: 'warning',
  }
  return map[tier] || 'default'
}

function formatExpiry() {
  // TODO: 从用户信息中获取实际到期时间
  return '待定'
}

function selectPlan(plan: any) {
  showToast(`${plan.name} - 请联系管理员申请`)
}

function applyMembership() {
  showToast('请联系管理员申请会员')
}
</script>

<style scoped>
.membership-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.membership-status {
  padding: 16px;
}

.status-card {
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  color: #fff;
}

.status-card.basic { background: linear-gradient(135deg, #667eea, #764ba2); }
.status-card.advanced { background: linear-gradient(135deg, #11998e, #38ef7d); }
.status-card.diamond { background: linear-gradient(135deg, #f093fb, #f5576c); }

.tier-label {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.tier-desc {
  font-size: 14px;
  opacity: 0.9;
}

.权益-card, .plans-card {
  margin: 12px 16px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
}

h3 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #333;
}
</style>
