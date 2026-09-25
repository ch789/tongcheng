import request from './request'

// 产品列表
export const getProducts = (params?: object) =>
  request.get('/products', { params })

// 产品详情
export const getProduct = (id: number) =>
  request.get(`/products/${id}`)

// 我的产品列表
export const getMyProducts = () =>
  request.get('/products/my')

// 创建产品
export const createProduct = (data: object) =>
  request.post('/products', data)

// 更新产品
export const updateProduct = (id: number, data: object) =>
  request.put(`/products/${id}`, data)

// 删除产品
export const deleteProduct = (id: number) =>
  request.delete(`/products/${id}`)

// 行业列表
export const getIndustries = () =>
  request.get('/products/industries')
