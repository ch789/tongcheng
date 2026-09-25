import request from 'axios'

// 图片上传 API（H5 专用，走 admin/upload-compressed 接口）
export const uploadImage = async (file: File): Promise<{ url: string; path: string; compressed: boolean }> => {
  const token = localStorage.getItem('token') || ''
  const res = await request.post('/api/admin/upload-compressed', file, {
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}
