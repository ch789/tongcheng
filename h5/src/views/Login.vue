<template>
  <div class="login-page">
    <!-- 顶部蓝色渐变背景 -->
    <div class="login-bg">
      <div class="login-logo">🏠</div>
      <h1 class="login-title">同城老乡服务平台</h1>
      <p class="login-subtitle">在外老乡的一站式服务平台</p>
    </div>

    <!-- 登录表单卡片 -->
    <div class="login-card">
      <!-- 微信登录 -->
      <van-form @submit="handleWechatLogin">
        <van-button
          native-type="submit"
          type="primary"
          icon="weibo"
          block
          round
          class="wechat-login-btn"
        >
          微信授权登录
        </van-button>
      </van-form>

      <div class="divider">
        <span>或</span>
      </div>

      <!-- 短信登录 -->
      <van-form @submit="handleSmsLogin">
        <van-field
          v-model="phone"
          name="phone"
          label="手机号"
          placeholder="请输入手机号"
          type="tel"
          maxlength="11"
          required
          class="login-field"
        />
        <van-field
          v-model="code"
          name="code"
          label="验证码"
          placeholder="请输入验证码"
          required
          class="login-field"
        >
          <template #button>
            <van-button
              size="small"
              type="primary"
              plain
              @click="sendCode"
              :disabled="countdown > 0"
              class="sms-code-btn"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </van-button>
          </template>
        </van-field>
        <van-button type="primary" block native-type="submit" class="sms-login-btn">
          短信登录
        </van-button>
      </van-form>

      <!-- 开发模式验证码提示 -->
      <van-notice-bar
        color="#fff"
        background="#1a73e8"
        :text="'开发模式验证码: ' + (debugCode || '请点击获取验证码')"
        class="debug-notice"
      />

      <p class="agreement">登录即表示同意《用户协议》和《隐私政策》</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { wechatLogin, smsLogin, sendSmsCode } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const phone = ref('')
const code = ref('')
const countdown = ref(0)
const debugCode = ref('')

async function handleWechatLogin() {
  // 获取URL中的code参数（微信授权回调）
  const params = new URLSearchParams(window.location.search)
  const wxCode = params.get('code')

  if (!wxCode) {
    showToast('未获取到授权码，请从公众号进入')
    return
  }

  try {
    await userStore.loginWithWechat(wxCode)
    showToast('登录成功')
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/')
  } catch (error: any) {
    showToast(error?.detail || '登录失败，请重试')
  }
}

async function handleSmsLogin() {
  if (!phone.value || !code.value) {
    showToast('请填写完整信息')
    return
  }
  try {
    const res = await smsLogin(phone.value, code.value)
    // 存储 token 和用户信息到 store
    userStore.token = res.access_token
    userStore.userInfo = {
      id: res.user_id,
      nickname: res.nickname || '',
      avatar_url: res.avatar_url || '',
      role: res.role,
    }
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user_info', JSON.stringify(userStore.userInfo))
    showToast('登录成功')
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/')
  } catch (error: any) {
    showToast(error?.detail || '登录失败')
  }
}

async function sendCode() {
  if (!phone.value || phone.value.length !== 11) {
    showToast('请输入正确的手机号')
    return
  }
  try {
    const res = await sendSmsCode(phone.value)
    debugCode.value = res.code
    showToast({ message: '验证码已发送: ' + res.code, type: 'success', duration: 4000 })
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error: any) {
    showToast({ message: error?.detail || '发送失败', type: 'fail', duration: 3000 })
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--bg-color);
  display: flex;
  flex-direction: column;
}

/* ── 顶部蓝色背景区 ── */
.login-bg {
  background: linear-gradient(135deg, #1a73e8 0%, #4a9af5 60%, #7bb8f7 100%);
  padding: 60px 24px 48px;
  text-align: center;
  color: #fff;
  position: relative;
  overflow: hidden;
}

.login-bg::before {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 160px;
  height: 160px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
}

.login-bg::after {
  content: '';
  position: absolute;
  bottom: -50px;
  left: -30px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 50%;
}

.login-logo {
  font-size: 48px;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,0.15));
}

.login-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 6px;
  position: relative;
  z-index: 1;
  letter-spacing: 1px;
}

.login-subtitle {
  font-size: 13px;
  opacity: 0.85;
  margin: 0;
  position: relative;
  z-index: 1;
}

/* ── 白色卡片区 ── */
.login-card {
  flex: 1;
  margin: -24px 16px 16px;
  background: #fff;
  border-radius: 20px 20px 0 0;
  padding: 28px 20px 24px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 2;
}

/* ── 微信登录按钮 ── */
.wechat-login-btn {
  background: #07c160 !important;
  border-color: #07c160 !important;
  height: 44px !important;
  font-size: 15px !important;
  font-weight: 500 !important;
}

/* ── 分割线 ── */
.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #bbb;
  font-size: 12px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #eee;
}

.divider span {
  padding: 0 12px;
}

/* ── 表单字段 ── */
.login-field {
  margin-bottom: 12px;
  border-radius: 10px;
  background: #f7f8fa;
  border: 1px solid transparent;
  transition: border-color 0.2s;
}

.login-field:focus-within {
  border-color: var(--primary-color);
  background: #fff;
}

.sms-code-btn {
  color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

/* ── 短信登录按钮 ── */
.sms-login-btn {
  margin-top: 8px;
  height: 44px;
  font-size: 15px;
  font-weight: 500;
  background: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

/* ── 调试提示 ── */
.debug-notice {
  margin-top: 16px;
  border-radius: 8px;
  font-size: 12px;
}

/* ── 协议声明 ── */
.agreement {
  text-align: center;
  font-size: 11px;
  color: #bbb;
  margin-top: 20px;
  margin-bottom: 0;
}
</style>
