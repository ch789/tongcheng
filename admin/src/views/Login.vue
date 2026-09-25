<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">🏠</div>
        <div class="title">同城老乡服务平台</div>
        <div class="subtitle">管理后台</div>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" native-type="submit">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="tip">演示账号：admin / admin123（将在初始化脚本中创建）</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = ref({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const response = await api.post('/auth/password/login', {
        phone: form.value.username,
        password: form.value.password,
      })
      localStorage.setItem('token', response.access_token)
      ElMessage.success('登录成功')
      router.push('/admin/dashboard')
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '登录失败，请检查账号密码')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  width: 400px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 12px;
}

.title {
  font-size: 22px;
  font-weight: bold;
  color: #333;
}

.subtitle {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.login-form {
  margin-top: 24px;
}

.tip {
  text-align: center;
  font-size: 12px;
  color: #999;
  margin-top: 16px;
}
</style>
