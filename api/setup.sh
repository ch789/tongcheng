#!/bin/bash
set -e

echo "=== 安装后端依赖 ==="
pip3 install -r requirements.txt

echo "=== 初始化数据库（需先启动 PostgreSQL）==="
echo "请确保 PostgreSQL 已启动，并创建数据库："
echo "  createdb -U postgres handanzh"
echo ""
echo "创建 .env 文件："
cp .env.example .env
if [ ! -f .env ]; then
  echo ".env 文件不存在，请使用 .env.example 作为模板"
fi

echo ""
echo "=== 启动服务 ==="
echo "开发模式：uvicorn app.main:app --reload --port 8000"
