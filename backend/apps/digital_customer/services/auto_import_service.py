"""
自动导入服务 - 启动时自动导入 data 目录中的客户画像文件
"""
import os
import hashlib
import asyncio
from pathlib import Path
from loguru import logger
from sqlalchemy import select

from backend.core.database import digital_customer_async_session, get_digital_customer_db
from backend.models.db_models import CustomerProfile, CustomerChunk, CustomerProfileRegistry
from backend.apps.digital_customer.services.profile_parser import profile_parser_service
from backend.apps.digital_customer.services.chunking_service import chunking_service
from backend.apps.customer_service.services.embedding_service import embedding_service


class AutoImportService:
    """自动导入服务"""

    def __init__(self, import_dir: str):
        """
        初始化自动导入服务

        Args:
            import_dir: 要扫描的目录路径
        """
        self.import_dir = import_dir
        os.makedirs(import_dir, exist_ok=True)

    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件的 MD5 哈希值"""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    async def is_file_imported(self, file_hash: str) -> bool:
        """检查文件是否已导入"""
        async with digital_customer_async_session() as session:
            result = await session.execute(
                select(CustomerProfileRegistry).where(CustomerProfileRegistry.file_hash == file_hash)
            )
            registry = result.scalar_one_or_none()
            return registry is not None and registry.customer_profile_id is not None

    async def import_file(self, file_path: str) -> bool:
        """
        导入单个文件

        Returns:
            bool: 是否成功导入
        """
        filename = os.path.basename(file_path)

        try:
            # 计算文件哈希
            file_hash = self.calculate_file_hash(file_path)

            # 检查是否已导入
            if await self.is_file_imported(file_hash):
                logger.info(f"文件已导入，跳过: {filename}")
                return False

            logger.info(f"开始导入文件: {filename}")

            # 提取文本
            raw_text = profile_parser_service.extract_text_from_file(file_path)

            # 使用 LLM 解析结构化信息
            parsed_info = await profile_parser_service.parse_customer_profile(raw_text)

            # 验证必填字段
            if not parsed_info.get("profile_type"):
                logger.warning(f"无法从文档中提取客户画像类型，跳过: {filename}")
                return False

            # 生成 System Prompt
            system_prompt = profile_parser_service.generate_system_prompt(parsed_info)

            # 提取真实姓名和画像类型
            real_name = parsed_info.get("real_name")
            profile_type = parsed_info.get("profile_type", "未知客户类型")

            # 创建数据库记录
            customer = CustomerProfile(
                name=real_name,
                profile_type=profile_type,
                age_range=parsed_info.get("age_range"),
                gender=parsed_info.get("gender"),
                occupation=parsed_info.get("occupation"),
                industry=parsed_info.get("industry"),
                personality_traits=parsed_info.get("personality_traits"),
                communication_style=parsed_info.get("communication_style"),
                pain_points=parsed_info.get("pain_points"),
                needs=parsed_info.get("needs"),
                objections=parsed_info.get("objections"),
                system_prompt=system_prompt,
                raw_content=raw_text,
                source_file_path=file_path,
            )

            async with digital_customer_async_session() as session:
                session.add(customer)
                await session.flush()

                # 智能分块
                display_name = customer.name if customer.name else customer.profile_type
                logger.info(f"开始对 {display_name} 的文档进行分块...")
                chunks = chunking_service.chunk_text(
                    text=raw_text,
                    chunk_size=400,
                    overlap=50,
                    min_chunk_size=100
                )

                if chunks:
                    # 批量生成 embedding
                    logger.info(f"生成 {len(chunks)} 个文本块的向量...")
                    texts = [chunk["text"] for chunk in chunks]
                    embeddings = await asyncio.to_thread(embedding_service.get_embeddings_batch, texts)

                    # 存储到数据库
                    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        customer_chunk = CustomerChunk(
                            customer_profile_id=customer.id,
                            customer_name=customer.name,
                            customer_profile_type=customer.profile_type,
                            chunk_text=chunk["text"],
                            chunk_index=chunk["chunk_index"],
                            chunk_metadata=chunk["metadata"],
                            embedding=embedding.tobytes()
                        )
                        session.add(customer_chunk)

                    logger.info(f"成功为 {display_name} 创建 {len(chunks)} 个知识块")

                # 添加注册记录
                registry = CustomerProfileRegistry(
                    filename=filename,
                    file_hash=file_hash,
                    customer_profile_id=customer.id,
                    customer_name=customer.name,
                    customer_profile_type=customer.profile_type,
                    status="success"
                )
                session.add(registry)

                await session.commit()
                logger.info(f"✅ 成功导入文件: {filename} -> {display_name}")
                return True

        except Exception as e:
            logger.error(f"❌ 导入文件失败: {filename}, 错误: {e}")
            return False

    async def scan_and_import(self):
        """扫描目录并导入所有新文件"""
        logger.info("=" * 60)
        logger.info(f"开始扫描目录: {self.import_dir}")
        logger.info("=" * 60)

        # 支持的文件扩展名
        supported_extensions = [".pdf", ".md"]

        # 扫描目录
        files_to_import = []
        for ext in supported_extensions:
            files_to_import.extend(Path(self.import_dir).glob(f"*{ext}"))

        if not files_to_import:
            logger.info("未找到需要导入的文件")
            return

        logger.info(f"找到 {len(files_to_import)} 个文件")

        # 导入文件
        success_count = 0
        skip_count = 0
        fail_count = 0

        for file_path in files_to_import:
            result = await self.import_file(str(file_path))
            if result:
                success_count += 1
            elif result is False:
                skip_count += 1
            else:
                fail_count += 1

        logger.info("=" * 60)
        logger.info(f"导入完成: 成功 {success_count}, 跳过 {skip_count}, 失败 {fail_count}")
        logger.info("=" * 60)


# 创建全局实例
# 默认扫描 backend/data/customer_profiles/ 目录
import os
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
CUSTOMER_PROFILES_DIR = os.path.join(DATA_DIR, "customer_profiles")
auto_import_service = AutoImportService(CUSTOMER_PROFILES_DIR)
