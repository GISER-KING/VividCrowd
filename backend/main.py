"""
VividCrowd 后端总入口
统一挂载三个子应用：群聊、数字分身、数字客服
"""
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from backend.core.database import init_db
from backend.core.config import settings
from backend.apps.chat.app import chat_app
from backend.apps.celebrity.app import celebrity_app
from backend.apps.customer_service.app import customer_service_app, orchestrator, CSV_DIR
from backend.apps.customer_service.services.excel_importer import import_qa_from_csv
from backend.apps.customer_service.services.csv_registry import auto_import_csv_files
from backend.apps.digital_customer.app import digital_customer_app, start_scheduler as start_digital_customer_scheduler, stop_scheduler as stop_digital_customer_scheduler, init_digital_customer_tables
from backend.apps.digital_interviewer.app import router as digital_interviewer_router, scan_all_digital_humans


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 50)
    logger.info("VividCrowd 后端启动中...")
    logger.info(f"环境: {'开发' if settings.DEBUG else '生产'}")
    logger.info("=" * 50)

    # 初始化数据库
    await init_db()
    # 显式初始化数字客户表（防止init_db遗漏）
    init_digital_customer_tables()
    logger.info("数据库初始化完成")

    # 启动数字客户定时任务
    await start_digital_customer_scheduler()

    # 初始化客服子应用
    from backend.core.database import async_session
    async with async_session() as db:
        # 自动导入 CSV 文件
        logger.info("开始导入客服 CSV 数据...")
        await auto_import_csv_files(
            db=db,
            csv_dir=CSV_DIR,
            import_func=import_qa_from_csv,
            api_key=settings.DASHSCOPE_API_KEY
        )

        # 初始化客服编排器
        logger.info("初始化客服编排器...")
        await orchestrator.initialize(db)
        logger.info("客服子应用初始化完成")

    # 扫描数字面试官虚拟人形象库
    logger.info("扫描虚拟人形象库...")
    scan_all_digital_humans()
    logger.info("数字面试官初始化完成")

    yield

    # 关闭时
    await stop_digital_customer_scheduler()
    logger.info("VividCrowd 后端关闭")


# 创建主应用
app = FastAPI(
    title="VividCrowd",
    description="VividCrowd 智能对话平台 - 群聊、数字分身、数字客服、数字客户",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载子应用
app.mount("/api/chat", chat_app)
app.mount("/api/celebrity", celebrity_app)
app.mount("/api/customer-service", customer_service_app)
app.mount("/api/digital-customer", digital_customer_app)

# 挂载数字面试官路由
app.include_router(digital_interviewer_router, prefix="/api")

# 挂载静态文件服务 - 提供虚拟人形象视频访问
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")


@app.get("/")
async def root():
    """根路径 - 返回API信息"""
    return {
        "name": "VividCrowd API",
        "version": "2.0.0",
        "modules": {
            "chat": "/api/chat",
            "celebrity": "/api/celebrity",
            "customer_service": "/api/customer-service",
            "digital_customer": "/api/digital-customer",
            "digital_interviewer": "/api/digital-interviewer"
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "modules": {
            "chat": "ok",
            "celebrity": "ok",
            "customer_service": "ok",
            "digital_customer": "ok",
            "digital_interviewer": "ok"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )