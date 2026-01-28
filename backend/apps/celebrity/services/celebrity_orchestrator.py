import asyncio
from typing import List, Dict, Any, AsyncGenerator
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.database import celebrity_async_session
from backend.models.db_models import KnowledgeSource
from backend.core.config import settings
from .celebrity_agent import CelebrityAgent
from .session_manager import CelebritySessionManager
from .audio_service import synthesize_audio
from .audio_upload_service import audio_upload_service
from .video_service import celebrity_video_service

class CelebrityOrchestratorService:
    """名人对话编排器 - 管理多个名人 Agent 的对话"""

    def __init__(self, enable_video: bool = True):
        """
        Args:
            enable_video: 是否启用视频生成功能
        """
        self.enable_video = enable_video

    async def _generate_video_for_response(self, text: str, sender: str):
        """
        为回复生成数字人视频（先返回音频，后返回视频）

        Args:
            text: 回复文本
            sender: 发送者名称

        Yields:
            audio_ready消息和video_ready消息
        """
        try:
            # 检查配置
            if not settings.CELEBRITY_VOLCENGINE_ACCESS_KEY or not settings.CELEBRITY_VOLCENGINE_SECRET_KEY:
                logger.warning("[Celebrity Video] 火山引擎未配置，跳过视频生成")
                return

            if not settings.CELEBRITY_OSS_ACCESS_KEY_ID or not settings.CELEBRITY_OSS_BUCKET_NAME:
                logger.warning("[Celebrity Video] OSS未配置，跳过视频生成")
                return

            if not settings.CELEBRITY_IMAGE_URL:
                logger.warning("[Celebrity Video] 名人形象图片未配置，跳过视频生成")
                return

            logger.info(f"[Celebrity Video] 开始为 {sender} 的回复生成音频和视频...")

            # Step 1: TTS 生成音频
            logger.info("[Celebrity Video] 正在进行 TTS 生成...")
            audio_bytes = await synthesize_audio(text)

            # Step 2: 立即将音频以base64格式发送给前端播放
            import base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            audio_data_url = f"data:audio/mp3;base64,{audio_base64}"

            yield {
                "type": "audio_ready",
                "sender": sender,
                "content": audio_data_url
            }
            logger.info(f"[Celebrity Video] 音频{audio_data_url}已发送（base64格式），开始上传到OSS...")

            # Step 3: 上传音频到 OSS（用于火山引擎访问）
            logger.info("[Celebrity Video] 正在上传音频到 OSS...")
            audio_url = audio_upload_service.upload_audio(audio_bytes, file_extension="mp3")
            logger.info(f"[Celebrity Video] 音频上传成功: {audio_url}")

            # Step 4: 后台生成视频
            # 如果是首次使用，先创建形象
            if not celebrity_video_service.cached_resource_id:
                logger.info("[Celebrity Video] 首次使用，创建名人形象...")
                raw_image_path = settings.CELEBRITY_IMAGE_URL
                logger.info(f"[Celebrity Video] 原始图片配置路径: {raw_image_path}")

                # 如果不是HTTP URL，则通过OSS生成签名URL
                if not raw_image_path.startswith("http"):
                    # image_url = audio_upload_service.get_file_url(raw_image_path)
                    image_url = audio_upload_service.get_public_url(raw_image_path)
                    logger.info(f"[Celebrity Video] oss image 路径: {raw_image_path}")
                else:
                    image_url = raw_image_path
                
                logger.info(f"[Celebrity Video] 解析后的图片URL: {image_url}")
                await celebrity_video_service.create_avatar(image_url)
                

            video_url = await celebrity_video_service.generate_video(audio_url)

            # 转换为代理URL
            from urllib.parse import quote
            proxy_url = f"/celebrity/digital-human/proxy-video?url={quote(video_url)}"
            logger.info(f"[Celebrity Video] 视频生成成功: {proxy_url}")

            # Step 5: 返回视频URL
            yield {
                "type": "video_ready",
                "sender": sender,
                "content": proxy_url
            }

        except Exception as e:
            logger.error(f"[Celebrity Video] 音频/视频生成失败: {e}")
            return

    async def get_celebrity_by_id(self, celebrity_id: int) -> KnowledgeSource | None:
        """根据 ID 获取名人信息"""
        async with celebrity_async_session() as session:
            result = await session.execute(
                select(KnowledgeSource).where(KnowledgeSource.id == celebrity_id)
            )
            return result.scalar_one_or_none()

    async def handle_message(
        self,
        user_msg: str,
        celebrity_ids: List[int],
        mode: str = "private",
        session_id: str = None,
        db: Session = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理用户消息

        Args:
            user_msg: 用户消息
            celebrity_ids: 选中的名人 ID 列表
            mode: 对话模式 - 'private' 一对一 / 'group' 群聊
            session_id: 会话ID
            db: 数据库会话

        Yields:
            WebSocket 消息格式: {type, sender, content}
        """
        if not session_id or not db:
            yield {
                "type": "error",
                "sender": "System",
                "content": "Session未初始化"
            }
            return

        if not celebrity_ids:
            yield {
                "type": "error",
                "sender": "System",
                "content": "请先选择一位名人进行对话"
            }
            return

        # 创建SessionManager
        session_manager = CelebritySessionManager(db)

        # 获取历史记录
        chat_history = session_manager.get_history(session_id, limit=10)

        # 记录用户消息到数据库
        session_manager.add_message(session_id, "用户", user_msg)
        chat_history.append(f"用户: {user_msg}")

        # 获取所有选中的名人
        celebrities = []
        for cid in celebrity_ids:
            celebrity = await self.get_celebrity_by_id(cid)
            if celebrity:
                celebrities.append(celebrity)

        if not celebrities:
            yield {
                "type": "error",
                "sender": "System",
                "content": "未找到选中的名人"
            }
            return

        if mode == "private":
            # 一对一模式：只有一个名人回复
            celebrity = celebrities[0]

            # 创建数据库会话并传递给 Agent
            async with celebrity_async_session() as session:
                agent = CelebrityAgent(celebrity, db_session=session)

                yield {
                    "type": "stream_start",
                    "sender": celebrity.name,
                    "content": ""
                }

                full_response = ""
                async for chunk in agent.generate_response_stream(
                    user_msg,
                    chat_history,
                    mode="private"
                ):
                    full_response += chunk
                    yield {
                        "type": "stream_chunk",
                        "sender": celebrity.name,
                        "content": chunk
                    }

                yield {
                    "type": "stream_end",
                    "sender": celebrity.name,
                    "content": ""
                }

                # 记录回复到数据库
                session_manager.add_message(session_id, celebrity.name, full_response)

                # 生成数字人音频和视频（如果启用）
                if self.enable_video and full_response.strip():
                    logger.info(f"[Celebrity Orchestrator] 开始为 {celebrity.name} 生成音频和视频...")
                    async for media_message in self._generate_video_for_response(full_response, celebrity.name):
                        yield media_message
                    logger.info(f"[Celebrity Orchestrator] 音频和视频处理完成")

        else:
            # 群聊模式：多个名人依次回复
            async with celebrity_async_session() as session:
                for celebrity in celebrities:
                    agent = CelebrityAgent(celebrity, db_session=session)

                    yield {
                        "type": "stream_start",
                        "sender": celebrity.name,
                        "content": ""
                    }

                    full_response = ""
                    async for chunk in agent.generate_response_stream(
                        user_msg,
                        chat_history,
                        mode="group"
                    ):
                        full_response += chunk
                        yield {
                            "type": "stream_chunk",
                            "sender": celebrity.name,
                            "content": chunk
                        }

                    yield {
                        "type": "stream_end",
                        "sender": celebrity.name,
                        "content": ""
                    }

                    # 记录回复到数据库
                    session_manager.add_message(session_id, celebrity.name, full_response)
                    # 同时更新本地历史，供后续专家参考
                    chat_history.append(f"{celebrity.name}: {full_response}")

                    # 生成数字人音频和视频（如果启用）
                    if self.enable_video and full_response.strip():
                        logger.info(f"[Celebrity Orchestrator] 开始为 {celebrity.name} 生成音频和视频...")
                        async for media_message in self._generate_video_for_response(full_response, celebrity.name):
                            yield media_message
                        logger.info(f"[Celebrity Orchestrator] 音频和视频处理完成")

                    # 群聊模式下，每个回复之间稍作延迟
                    if celebrity != celebrities[-1]:
                        await asyncio.sleep(0.5)

    # clear_history 方法已移除
    # 历史记录现在通过 SessionManager 管理，使用 clear_old_sessions() 清理旧会话


# 不再创建全局单例，改为在 WebSocket 连接时创建实例
# celebrity_orchestrator_service = CelebrityOrchestratorService()
