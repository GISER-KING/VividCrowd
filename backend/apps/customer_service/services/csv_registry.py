"""
CSV Registry 服务 - 管理 CSV 文件的导入注册
基于文件名和 MD5 哈希实现去重和变更检测
"""
import os
import hashlib
from datetime import datetime
from typing import Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from backend.models.db_models import CSVRegistry


class CSVRegistryService:
    """CSV 文件注册服务"""

    @staticmethod
    def compute_file_hash(filepath: str) -> str:
        """计算文件的 MD5 哈希值"""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    async def get_registered_files(self, db: AsyncSession) -> Dict[str, str]:
        """
        获取所有已注册的文件

        Returns:
            {filename: file_hash} 字典
        """
        result = await db.execute(select(CSVRegistry))
        records = result.scalars().all()
        return {r.filename: r.file_hash for r in records}

    async def get_registry_entry(self, db: AsyncSession, filename: str) -> Optional[CSVRegistry]:
        """获取指定文件的注册记录"""
        result = await db.execute(
            select(CSVRegistry).where(CSVRegistry.filename == filename)
        )
        return result.scalar_one_or_none()

    async def is_file_registered(self, db: AsyncSession, filename: str) -> bool:
        """检查文件是否已注册"""
        entry = await self.get_registry_entry(db, filename)
        return entry is not None

    async def is_file_changed(self, db: AsyncSession, filename: str, current_hash: str) -> bool:
        """
        检查文件是否变更

        Args:
            filename: 文件名
            current_hash: 当前文件的 MD5 哈希

        Returns:
            True 表示文件已变更或不存在，False 表示未变更
        """
        entry = await self.get_registry_entry(db, filename)
        if entry is None:
            return True  # 文件未注册，视为"变更"
        return entry.file_hash != current_hash

    async def register_file(
        self,
        db: AsyncSession,
        filename: str,
        file_hash: str,
        record_count: int,
        status: str = "success"
    ) -> CSVRegistry:
        """
        注册或更新文件记录

        Args:
            filename: 文件名
            file_hash: MD5 哈希值
            record_count: 导入的记录数
            status: 状态 (success/failed)

        Returns:
            CSVRegistry 记录
        """
        entry = await self.get_registry_entry(db, filename)

        if entry:
            # 更新现有记录
            entry.file_hash = file_hash
            entry.record_count = record_count
            entry.status = status
            entry.imported_at = datetime.utcnow()
            logger.info(f"更新注册记录: {filename} (hash: {file_hash[:8]}...)")
        else:
            # 创建新记录
            entry = CSVRegistry(
                filename=filename,
                file_hash=file_hash,
                record_count=record_count,
                status=status,
                imported_at=datetime.utcnow()
            )
            db.add(entry)
            logger.info(f"新增注册记录: {filename} (hash: {file_hash[:8]}...)")

        await db.commit()
        return entry

    async def get_all_registries(self, db: AsyncSession) -> List[CSVRegistry]:
        """获取所有注册记录"""
        result = await db.execute(select(CSVRegistry))
        return result.scalars().all()


# 全局服务实例
csv_registry_service = CSVRegistryService()


async def auto_import_csv_files(
    db: AsyncSession,
    csv_dir: str,
    import_func,
    api_key: Optional[str] = None
) -> Dict[str, any]:
    """
    自动导入 CSV 目录中的文件

    Args:
        db: 数据库会话
        csv_dir: CSV 文件目录
        import_func: 导入函数 (async def import_func(db, filepath, clear_existing, api_key))
        api_key: API 密钥

    Returns:
        导入统计结果
    """
    if not os.path.exists(csv_dir):
        logger.info(f"CSV 目录不存在: {csv_dir}")
        return {"imported": 0, "skipped": 0, "failed": 0}

    # 扫描目录中的 CSV 文件
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

    if not csv_files:
        logger.info(f"CSV 目录为空: {csv_dir}")
        return {"imported": 0, "skipped": 0, "failed": 0}

    logger.info(f"发现 {len(csv_files)} 个 CSV 文件")

    stats = {"imported": 0, "skipped": 0, "failed": 0, "details": []}

    # 第一个文件使用 clear_existing=True，后续文件使用 False（合并导入）
    first_file = True

    for filename in sorted(csv_files):  # 按文件名排序，保证导入顺序一致
        filepath = os.path.join(csv_dir, filename)
        current_hash = csv_registry_service.compute_file_hash(filepath)

        # 检查是否需要导入
        is_changed = await csv_registry_service.is_file_changed(db, filename, current_hash)

        if not is_changed:
            logger.info(f"跳过未变更的文件: {filename}")
            stats["skipped"] += 1
            stats["details"].append({"filename": filename, "action": "skipped", "reason": "unchanged"})
            continue

        # 执行导入
        logger.info(f"开始导入: {filename}")
        try:
            result = await import_func(
                db=db,
                csv_path=filepath,
                clear_existing=first_file,  # 第一个文件清空，后续合并
                api_key=api_key
            )
            first_file = False  # 后续文件不再清空

            # 注册文件
            record_count = result.get('success_count', 0)
            await csv_registry_service.register_file(
                db=db,
                filename=filename,
                file_hash=current_hash,
                record_count=record_count,
                status="success"
            )

            stats["imported"] += 1
            stats["details"].append({
                "filename": filename,
                "action": "imported",
                "record_count": record_count
            })
            logger.info(f"导入成功: {filename} ({record_count} 条记录)")

        except Exception as e:
            logger.error(f"导入失败: {filename} - {e}")

            # 记录失败
            await csv_registry_service.register_file(
                db=db,
                filename=filename,
                file_hash=current_hash,
                record_count=0,
                status="failed"
            )

            stats["failed"] += 1
            stats["details"].append({
                "filename": filename,
                "action": "failed",
                "error": str(e)
            })

    logger.info(f"自动导入完成: 导入 {stats['imported']}, 跳过 {stats['skipped']}, 失败 {stats['failed']}")
    return stats
