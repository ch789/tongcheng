# 同城老乡服务平台

面向在外生活、工作、经商的同乡的一站式综合服务平台：找商户、找活动、找同乡服务。增进同乡感情、促进商机合作、推进产业构建。
系统支持商户入驻、产品发布、活动报名和数据导出等功能。
包含 H5 用户端、管理后台、FastAPI 后端三部分。

<img width="393" height="852" alt="IMG_3014" src="https://github.com/user-attachments/assets/121027fe-8bcb-49bd-bd58-6f085c9b082f" />
<img width="393" height="852" alt="IMG_3015" src="https://github.com/user-attachments/assets/7a658060-1665-4763-a78f-55eca874e982" />
<img width="393" height="852" alt="IMG_3016" src="https://github.com/user-attachments/assets/b4fbbdad-de6b-4f28-be50-203a47553bb2" />
<img width="1356" height="675" alt="同城老乡服务平台 - 管理后台" src="https://github.com/user-attachments/assets/c2e1bb54-c67d-4e9b-8bb4-e19ed04fabfa" />

## 目录结构

```
├── api/     FastAPI 后端（Python 3.11 + PostgreSQL）
├── h5/      Vue 3 移动端（Vant UI + Pinia）
├── admin/   Vue 3 管理后台（Element Plus）
└── render.yaml   Render 一键部署蓝图（Postgres + API + H5 + Admin）
```

## 本地开发

### 1. 数据库
PostgreSQL `localhost:5432`，库名 `handanzh`。

### 2. 后端
```bash
cd api
pip install -r requirements.txt
cp .env.example .env      # 填 DATABASE_URL / SECRET_KEY / BASE_URL
uvicorn app.main:app --reload --port 8000
```
首次启动会自动建表并幂等播种（管理员 `admin/admin123`、行业字典、首页文案）。

### 3. 前端（H5 / 管理后台）
```bash
cd h5 && npm install && npm run dev      # :3000，/api、/uploads 代理到 :8000
cd admin && npm install && npm run dev   # :3002，同上
```

## 部署（Render）

仓库根目录 `render.yaml` 为一键蓝图，创建 4 个资源：
1. **Postgres**（免费档）— 库 `handanzh`
2. **API**（Docker Web Service）— 复用 `api/Dockerfile`
3. **H5**（Static Site）— `npm run build` 出 `dist`
4. **Admin**（Static Site）— 同上

前端通过构建期环境变量 `VITE_API_URL` 指向 API 域名（跨域直连）；
`BASE_URL` 驱动后端返回的图片绝对 URL。首次部署 API 后，把其真实
域名回填到 H5/Admin 的 `VITE_API_URL` 与 API 的 `BASE_URL`，再重部署即可。

## 测试数据

`api/seed_test_data.py` 可离线生成一批测试数据（6 轮播 / 6 产品 / 6 活动），
图片用 PIL 生成并落地 `api/uploads/admin/`，脚本幂等、可重复运行。
