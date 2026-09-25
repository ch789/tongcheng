import request from './request'

// 商户入驻申请
export const applyMerchant = (data: object) =>
  request.post('/admin/merchants/apply', data)

// 我的商户信息
export const getMyMerchant = () =>
  request.get('/admin/merchants/my')

// 更新个人信息
export const updateProfile = (data: object) =>
  request.put('/auth/profile', data)

// 通知列表
export const getNotifications = (params?: object) =>
  request.get('/admin/notifications', { params })

// 标记通知已读
export const markNotificationRead = (id: number) =>
  request.put(`/admin/notifications/${id}/read`)

// 全部已读
export const markAllRead = () =>
  request.put('/admin/notifications/read-all')
