/**
 * 图片资源解析（最小改动 + 容器化/k8s 友好）：
 *  - http(s) 绝对 URL（管理端接口已带域，见 api/app/routers/admin.py）→ 原样透传
 *  - /uploads/…（本地相对路径）→ 跨域时补上后端 origin
 *  - 未注入 VITE_API_URL（本地/k8s 同域）→ 保持相对，<img> 天然走同域，零改即通
 */
const API_ORIGIN = (import.meta.env.VITE_API_URL || '').replace(/\/+api\/?$/, '')

export const resolveAsset = (p?: string | null): string | undefined => {
  if (!p) return undefined
  if (/^https?:\/\//.test(p)) return p
  if (p.startsWith('/uploads/')) return API_ORIGIN ? `${API_ORIGIN}${p}` : p
  return p
}
