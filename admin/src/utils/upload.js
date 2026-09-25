import api from '@/api'

const MAX_UPLOAD_SIZE = 5 * 1024 * 1024 // 5MB
// 前端压缩目标：长边最大 1600px，质量 85（与后端保持一致）
const MAX_WIDTH = 1600
const JPEG_QUALITY = 0.85

/**
 * 在客户端将图片压缩为 JPEG，返回 Blob。
 * 若文件已小于 MAX_UPLOAD_SIZE，不压缩直接原样返回。
 */
export async function compressIfNeeded(file) {
  if (file.size <= MAX_UPLOAD_SIZE) return file

  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let w = img.naturalWidth
        let h = img.naturalHeight
        if (w > MAX_WIDTH || h > MAX_WIDTH) {
          const ratio = MAX_WIDTH / Math.max(w, h)
          w = Math.round(w * ratio)
          h = Math.round(h * ratio)
        }
        canvas.width = w
        canvas.height = h
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, w, h)
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('图片压缩失败'))
              return
            }
            const compressed = new File([blob], file.name.replace(/\.[^.]+$/, '.jpg'), {
              type: 'image/jpeg',
            })
            resolve(compressed)
          },
          'image/jpeg',
          JPEG_QUALITY,
        )
      }
      img.onerror = () => reject(new Error('图片解析失败'))
      img.src = e.target?.result
    }
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsDataURL(file)
  })
}

/**
 * 上传图片（先尝试客户端压缩，超限则走服务端 /upload-compressed 接口）。
 * @returns {{ url: string, path: string, compressed: boolean }}
 */
export async function uploadImage(file) {
  // 走共享 api 实例（baseURL 已含 /api，token 由拦截器自动带），跨域时指向 VITE_API_URL
  // 1. 先尝试客户端压缩上传
  try {
    const compressedFile = await compressIfNeeded(file)
    const form = new FormData()
    form.append('file', compressedFile)
    const res = await api.post('/admin/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return { url: res.url, path: res.path, compressed: compressedFile !== file }
  } catch (e) {
    // 2. 若仍超限制（服务端拒绝），走服务端压缩接口
    if (e?.response?.status === 400 && file.size > MAX_UPLOAD_SIZE) {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/admin/upload-compressed', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return { url: res.url, path: res.path, compressed: res.compressed || true }
    }
    throw e
  }
}
