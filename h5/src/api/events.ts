import request from './request'

// 活动列表
export const getEvents = (params?: object) =>
  request.get('/activities', { params })

// 活动详情
export const getEvent = (id: number) =>
  request.get(`/activities/${id}`)

// 报名活动
export const registerEvent = (eventId: number, data: object) =>
  request.post(`/activities/${eventId}/register`, data)

// 我的报名记录
export const getMyRegistrations = () =>
  request.get('/activities/my-registrations')

// 广告申请（商户提交）
export const applyAd = (data: object) =>
  request.post('/ads/apply', data)

// 我的广告列表
export const getMyAds = () =>
  request.get('/ads')
