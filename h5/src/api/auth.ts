import request from './request'

// 微信网页授权登录
export const wechatLogin = (code: string) =>
  request.post('/auth/wechat/login', { code })

// 手机号+验证码登录
export const smsLogin = (phone: string, code: string) =>
  request.post('/auth/phone/login', { phone, code })

// 获取当前用户信息
export const getCurrentUser = () =>
  request.get('/auth/me')

// 发送短信验证码（开发模式返回验证码）
export const sendSmsCode = (phone: string) =>
  request.post('/auth/sms/send', { phone })
