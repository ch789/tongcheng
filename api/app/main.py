from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.database import init_db
from app.routers import auth, home, products, activities, ads, admin, exports


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="同城老乡服务平台",
    description="面向在外生活、工作、经商的同乡综合服务平台",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务（上传的图片）
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 用户端路由
app.include_router(auth.router, prefix="/api")
app.include_router(home.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(ads.router, prefix="/api")

# 管理后台路由
app.include_router(admin.router, prefix="/api/admin")

# 数据导出路由
app.include_router(exports.router, prefix="/api/admin")


@app.get("/")
async def root():
    return {"message": "同城老乡服务平台 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
