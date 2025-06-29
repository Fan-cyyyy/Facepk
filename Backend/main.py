import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 使用普通导入
from config.settings import PROJECT_NAME, VERSION, API_V1_STR, BACKEND_CORS_ORIGINS
from config.logging_config import setup_logging
# 导入API路由模块
from api.v1 import auth, scores, rankings, matches

# 设置日志
logger = setup_logging()

# 创建应用
app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="魔镜Mirror颜值PK平台API"
)

# 设置CORS
if BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 添加静态文件目录，用于上传的图片
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 路由
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# 包含API路由 - 暂时注释掉，等创建好相应文件后再取消注释
app.include_router(auth.router, prefix=API_V1_STR)
app.include_router(scores.router, prefix=API_V1_STR)
app.include_router(rankings.router, prefix=API_V1_STR)
app.include_router(matches.router, prefix=API_V1_STR)

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {PROJECT_NAME} v{VERSION}")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {PROJECT_NAME}")

# 直接运行
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 