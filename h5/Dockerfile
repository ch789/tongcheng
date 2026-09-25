# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
# 构建时注入 VITE_API_URL（跨域指向 API 容器域名 + /api）；
# 不传则前端回退相对 /api（同域反代形态）。用法：
#   docker build --build-arg VITE_API_URL=https://<api域名>/api -t h5 .
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
