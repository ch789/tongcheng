/** 微信工具函数（预留，当前登录走后端 /auth/wechat/login 接口） */

// 判断是否在微信环境
export function isWechat(): boolean {
  return /micromessenger/i.test(navigator.userAgent)
}

// 获取当前URL参数
export function getUrlParams(): Record<string, string> {
  const params: Record<string, string> = {}
  const search = window.location.search.slice(1)
  search.split('&').forEach((pair) => {
    const [key, value] = pair.split('=')
    if (key) params[decodeURIComponent(key)] = decodeURIComponent(value || '')
  })
  return params
}
