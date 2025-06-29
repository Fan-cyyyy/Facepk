# 构建阶段
FROM node:16-alpine as build

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 从构建阶段复制文件
COPY --from=build /app/dist /usr/share/nginx/html

# 添加Nginx配置
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"] 