FROM python:3.11-slim

WORKDIR /app

# psycopg2-binary 预编译 wheel 需要运行时的 libpq，slim 镜像默认没有，显式装
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建上传目录，并把种子图（git 里的 static_seed/admin/*.jpg）打进镜像，
# 使 Neon 数据里 /uploads/admin/*.jpg 的相对路径在容器内可访问
RUN mkdir -p /app/uploads/admin
RUN cp -f static_seed/admin/*.jpg /app/uploads/admin/ 2>/dev/null || true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
