import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { wechatLogin, getCurrentUser } from '@/api/auth'

interface UserState {
  id: number
  nickname: string
  avatar_url: string
  role: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserState | null>(JSON.parse(localStorage.getItem('user_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => userInfo.value?.role || 'visitor')
  const membershipTier = ref('free')  // TODO: 接入实际会员体系后替换

  async function loginWithWechat(code: string) {
    try {
      const res = await wechatLogin(code)
      token.value = res.access_token
      userInfo.value = {
        id: res.user_id,
        nickname: res.nickname,
        avatar_url: res.avatar_url,
        role: res.role,
      }
      localStorage.setItem('token', res.access_token)
      localStorage.setItem('user_info', JSON.stringify(userInfo.value))
      return res
    } catch (error) {
      console.error('微信登录失败', error)
      throw error
    }
  }

  async function fetchUserInfo() {
    try {
      const res = await getCurrentUser()
      userInfo.value = {
        id: res.id,
        nickname: res.nickname,
        avatar_url: res.avatar_url,
        role: res.role,
      }
      localStorage.setItem('user_info', JSON.stringify(userInfo.value))
    } catch (error) {
      logout()
      throw error
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user_info')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    role,
    membershipTier,
    loginWithWechat,
    fetchUserInfo,
    logout,
  }
})
