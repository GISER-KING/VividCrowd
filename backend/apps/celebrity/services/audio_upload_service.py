"""
名人数字人音频上传服务
负责将音频文件上传到阿里云OSS
"""
import oss2
from backend.core.config import settings
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AudioUploadService:
    """音频上传服务类"""

    def __init__(self):
        self.access_key_id = settings.CELEBRITY_OSS_ACCESS_KEY_ID
        self.access_key_secret = settings.CELEBRITY_OSS_ACCESS_KEY_SECRET
        self.bucket_name = settings.CELEBRITY_OSS_BUCKET_NAME
        self.endpoint = settings.CELEBRITY_OSS_ENDPOINT
        self.audio_dir = settings.CELEBRITY_OSS_AUDIO_DIR

        # 初始化OSS客户端
        if self.access_key_id and self.access_key_secret and self.bucket_name:
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
            logger.info(f"[Celebrity AudioUploadService] OSS initialized - Bucket: {self.bucket_name}")
        else:
            self.bucket = None
            logger.warning("[Celebrity AudioUploadService] OSS not configured")

    def upload_audio(self, audio_bytes: bytes, file_extension: str = "mp3") -> str:
        """
        上传音频到OSS

        Args:
            audio_bytes: 音频数据（字节）
            file_extension: 文件扩展名

        Returns:
            音频的公网URL
        """
        if not self.bucket:
            raise Exception("OSS未配置，无法上传音频")

        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}.{file_extension}"
        object_key = f"{self.audio_dir}/{filename}"

        logger.info(f"[Celebrity AudioUploadService] Uploading audio: {object_key}")

        try:
            # 上传到OSS
            result = self.bucket.put_object(object_key, audio_bytes)

            if result.status == 200:
                # 生成公网URL
                audio_url = f"https://{self.bucket_name}.{self.endpoint}/{object_key}"
                logger.info(f"[Celebrity AudioUploadService] Upload success: {audio_url}")
                return audio_url
            else:
                raise Exception(f"OSS上传失败: {result.status}")

        except Exception as e:
            logger.error(f"[Celebrity AudioUploadService] Upload failed: {e}")
            raise
    

    def get_public_url(self, object_key: str) -> str:
        """
        获取文件的公网访问URL（不带签名）
        适用于 Bucket 权限为公共读的情况，或第三方服务不支持带签名的URL时使用
        """
        if not self.bucket:
            raise Exception("OSS未配置")
        
        # 移除可能存在的开头的 /
        if object_key.startswith("/"):
            object_key = object_key[1:]
            
        # 构造标准 OSS 公网 URL
        url = f"https://{self.bucket_name}.{self.endpoint}/{object_key}"
        return url

        
    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """
        获取OSS文件的签名URL（用于私有文件）

        Args:
            object_key: OSS对象键
            expires: 过期时间（秒）

        Returns:
            签名URL
        """
        if not self.bucket:
            raise Exception("OSS未配置")

        try:
            # 如果是完整URL，提取object_key
            if object_key.startswith("http"):
                # 从URL中提取object_key
                parts = object_key.split(f"{self.bucket_name}.{self.endpoint}/")
                if len(parts) > 1:
                    object_key = parts[1]

            # 生成签名URL
            url = self.bucket.sign_url('GET', object_key, expires, slash_safe=True)
            if url.startswith("http://"):
                url = url.replace("http://", "https://", 1)
            logger.info(f"[Celebrity AudioUploadService] Generated signed URL for: {url}")
            return url

        except Exception as e:
            logger.error(f"[Celebrity AudioUploadService] Failed to generate signed URL: {e}")
            logger.error(f"[Celebrity AudioUploadService] Failed to generate signed URL: {url}")
            raise


# 全局服务实例
audio_upload_service = AudioUploadService()
