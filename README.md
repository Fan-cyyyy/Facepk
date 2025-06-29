# 魔镜 Mirror 颜值 PK 平台

基于人脸识别技术的娱乐社交 Web 应用，支持用户上传照片进行颜值评分、PK 对战及全球/好友排行榜展示。

## 项目概述

"魔镜 Mirror 颜值 PK 平台"是一款融合 AI 技术与社交互动的娱乐应用，通过人工智能算法对用户上传的面部照片进行美学评分，支持用户间的 PK 对战，并提供实时排行榜和社交分享功能。

### 核心功能

- **用户注册/登录**：邮箱/用户名密码注册、JWT 认证
- **颜值评分**：支持照片上传，AI 自动评分（0-100分）
- **PK 对战**：支持与好友或随机用户进行颜值 PK
- **排行榜**：全球榜/好友榜/地区榜实时更新
- **社交分享**：生成个性化分享卡片，支持社交平台分享

## 技术架构

### 前端技术栈

- **核心框架**：React 18 + TypeScript
- **状态管理**：Redux Toolkit
- **UI 组件库**：Ant Design + TailwindCSS
- **构建工具**：Vite

### 后端技术栈

- **API 服务**：FastAPI
- **评分引擎**：Flask + OpenCV + Dlib
- **数据库**：MySQL + Redis
- **安全认证**：JWT

### AI 技术

- **人脸检测**：OpenCV + Dlib（68点人脸特征检测）
- **评分模型**：基于SCUT-FBP5500数据集训练的CNN模型
- **备用方案**：百度AI人脸评分接口

## 项目结构

```
Face score PK/
  ├── Backend/           # 后端代码
  │   ├── api/           # API接口定义
  │   ├── models/        # 数据库模型
  │   ├── schemas/       # 请求/响应模式
  │   ├── services/      # 业务逻辑服务
  │   ├── ai/            # AI评分引擎
  │   └── config/        # 配置文件
  │
  ├── Frontend/          # 前端代码
  │   ├── src/           # 源代码
  │   │   ├── components/# 组件
  │   │   ├── pages/     # 页面
  │   │   ├── redux/     # 状态管理
  │   │   ├── hooks/     # 自定义Hooks
  │   │   └── services/  # API服务
  │   └── public/        # 静态资源
  │
  └── docs/              # 项目文档
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### 后端设置

```bash
# 进入后端目录
cd Backend

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑.env文件配置数据库等信息

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn main:app --reload
```

### 前端设置

```bash
# 进入前端目录
cd Frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目团队

| 角色 | 姓名 | 职责 |
|------|------|------|
| **项目经理** | 郑宇风 | 制定计划、协调资源、进度跟踪 |
| **技术负责人** | 朱哲宁 | 架构设计、核心算法开发 |
| **前端开发** | 郑宇风 | Web 界面开发、用户交互实现 |
| **后端开发** | 朱哲宁、樊思宜 | API 开发、数据库设计、评分模块集成 |
| **测试工程师** | 樊思宜 | 测试用例设计、系统测试与部署 |

## 许可证

[MIT](LICENSE)
