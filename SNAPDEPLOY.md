# SnapDeploy 容器化部署说明（独立容器 + 跨域）

目标：用 Docker 容器方式把 4 个服务（Postgres / API / H5 / Admin）部署到 SnapDeploy，
各容器独立、各自公网域名，前端跨域调 API。

## 容器清单与构建

| 容器 | 源 | 构建 | 运行端口 | 说明 |
|------|----|------|---------|------|
| postgres | `postgres:16`（`postgres.yml`） | 镜像直起 | 5432 | 自起，`pgdata` 卷持久化 |
| api | `api/` | `docker build -f api/Dockerfile` | 8000 | uvicorn，首启自动建表+播种 |
| h5 | `h5/` | `docker build -f h5/Dockerfile` | 80 | build→nginx |
| admin | `admin/` | `docker build -f admin/Dockerfile` | 80 | build→nginx（生产形态） |

> 前端是跨域模型：H5/Admin 容器内 nginx 不做反代，浏览器直接打 API 公网域名。
> 因此前端构建必须注入 `VITE_API_URL`（见下）。

## 各容器环境变量

### Postgres（`postgres.yml`）
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=<强密码>`（上线务必改）
- `POSTGRES_DB=handanzh`
- 数据卷 `pgdata` 持久化
- 连接串（给 API 用）：`postgresql://postgres:<强密码>@<postgres容器主机>:5432/handanzh`

### API（`api/Dockerfile` 跑 uvicorn）
| 变量 | 值 |
|------|----|
| `DATABASE_URL` | 上面 Postgres 连接串 |
| `SECRET_KEY` | 随机强串（`python3 -c "import secrets;print(secrets.token_hex(32))"`），勿用 dev 值 |
| `BASE_URL` | API 容器公网域名，如 `https://<api域名>`（驱动图片绝对 URL、导出链接） |
| `WECHAT_APPID`/`WECHAT_SECRET` | 可选 |

- 健康检查：`GET /health` → `{"status":"ok"}`

### H5（`h5/Dockerfile`）
- 构建时：`VITE_API_URL=https://<api域名>/api`（跨域指向 API，末尾带 `/api`）
- 不设则回退相对 `/api`（同域反代形态，本方案不用）

### Admin（`admin/Dockerfile`）
- 构建时：`VITE_API_URL=https://<api域名>/api`

## 构建与启动顺序

1. **起 Postgres**：`docker compose -f postgres.yml up -d`（或用 SnapDeploy 等价方式）
   - 等它 ready：`docker exec handanzh-db pg_isready -U postgres`
2. **起 API**：`docker build -f api/Dockerfile -t api .` → 注入上面 env 跑
   - 首启 `lifespan→init_db()` 自动建表 + 幂等播种（admin 账号、行业、首页文案）
   - 验证：`GET /health` 200；`POST /api/auth/password/login` 用 `admin/admin123` 拿 token
3. **起 H5**：`docker build -f h5/Dockerfile -t h5 .`（构建命令里带 `VITE_API_URL`）
4. **起 Admin**：`docker build -f admin/Dockerfile -t admin .`（同上）

> 独立容器跨域：H5/Admin 的构建在 SnapDeploy 上通常是「构建命令注入 env」。
> 例：`npm install && VITE_API_URL=https://<api域名>/api npm run build`（对应各 Dockerfile 的 builder 阶段）。

## 验证

- Postgres：`pg_isready` OK
- API：`/health` 200；`/api/home` 返回播种的 slogan/公告
- H5：打开域名 → 首页文案 + 轮播（跨域调 `<api域名>/api`，CORS 已开 `*`）
- Admin：打开域名 → `admin/admin123` 登录
- 图片：API 的 `BASE_URL` 设成其公网域名后，上传/已有图片走绝对 URL 正常显示

## 图片（方式 1：种子图打进 API 镜像）

- 种子图 18 张（6 产品 / 6 活动 / 6 广告）在 `api/static_seed/admin/`（**进 git**），
  `api/Dockerfile` 构建时 `cp` 进 `/app/uploads/admin/`，容器起来即有。
- 数据里 `/uploads/admin/*.jpg` 的相对路径，容器内静态挂载 `/uploads` 直接命中。
- 运行期新上传的图写进 `/app/uploads/`（临时盘，容器重启会清，MVP 已接受）。

## 改动清单（本次为 SnapDeploy 做的）

- `admin/Dockerfile`：dev 形态（`npm run dev`）→ 生产 build+nginx
- `admin/nginx.conf`：新增（SPA 回退 + 保留可选反代段）
- `h5/nginx.conf`：`/api`、`/uploads` 反代段注释掉（跨域模型下独立容器无 `backend` hostname）
- `admin/.dockerignore`、`h5/.dockerignore`：新增，减小镜像
- `postgres.yml`：新增（本地 Postgres 容器；用 Neon 时不需要）
- `api/app/database.py`：连接池改为 `QueuePool(pool_size=5, max_overflow=5, pool_recycle=600)`，适配 Neon pooler
- `api/static_seed/admin/`：18 张种子图（进 git），`api/Dockerfile` 构建时拷进镜像

## 待你确认的占位

- 各容器**公网域名**（SnapDeploy 分配后回填 `VITE_API_URL`、`BASE_URL`、`DATABASE_URL` 里的主机）
- Postgres **强密码**（替换 `postgres.yml` 里的默认值）
