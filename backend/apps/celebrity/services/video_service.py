"""
名人数字人视频生成服务
基于火山引擎单图音频驱动API实现
文档: https://www.volcengine.com/docs/86081/1804516
"""
import requests
import json
import time
import hashlib
import hmac
from datetime import datetime
from typing import Optional, Dict, Any
from backend.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)


class CelebrityVideoService:
    """名人数字人视频生成服务类"""

    def __init__(self):
        self.access_key = settings.CELEBRITY_VOLCENGINE_ACCESS_KEY
        self.secret_key = settings.CELEBRITY_VOLCENGINE_SECRET_KEY
        self.region = settings.CELEBRITY_VOLCENGINE_REGION
        self.service_name = "cv"  # 固定值
        self.base_url = "https://visual.volcengineapi.com"

        # 名人形象URL（需要准备一张名人的照片）
        self.celebrity_image_url = settings.CELEBRITY_IMAGE_URL

        # 缓存的形象ID（避免重复创建）
        self.cached_resource_id = None

        logger.info(f"[Celebrity VideoService] 初始化完成 - Region: {self.region}")

    def _generate_signature_v4(self, method: str, path: str, query: str, headers: Dict[str, str], body: str) -> tuple:
        """生成火山引擎API v4签名"""
        # 1. 构建规范请求
        canonical_headers = ""
        signed_headers_list = []

        for key in sorted(headers.keys()):
            lower_key = key.lower()
            if lower_key in ['host', 'content-type', 'x-date']:
                canonical_headers += f"{lower_key}:{headers[key].strip()}\n"
                signed_headers_list.append(lower_key)

        signed_headers = ";".join(signed_headers_list)
        hashed_payload = hashlib.sha256(body.encode('utf-8')).hexdigest()
        canonical_request = f"{method}\n{path}\n{query}\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"

        # 2. 构建待签名字符串
        x_date = headers.get('X-Date', '')
        date_stamp = x_date[:8]
        credential_scope = f"{date_stamp}/{self.region}/{self.service_name}/request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = f"HMAC-SHA256\n{x_date}\n{credential_scope}\n{hashed_canonical_request}"

        # 3. 计算签名
        def hmac_sha256(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

        k_date = hmac_sha256(self.secret_key.encode('utf-8'), date_stamp)
        k_region = hmac_sha256(k_date, self.region)
        k_service = hmac_sha256(k_region, self.service_name)
        k_signing = hmac_sha256(k_service, "request")
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        return signature, signed_headers

    def _make_request(self, action: str, params: Dict[str, Any], version: str = "2022-08-31") -> Dict[str, Any]:
        """发送API请求"""
        method = "POST"
        path = "/"
        query = f"Action={action}&Version={version}"

        body = json.dumps(params) if params else ""

        now = datetime.utcnow()
        x_date = now.strftime('%Y%m%dT%H%M%SZ')

        headers = {
            'Host': 'visual.volcengineapi.com',
            'Content-Type': 'application/json',
            'X-Date': x_date,
        }

        signature, signed_headers = self._generate_signature_v4(method, path, query, headers, body)

        date_stamp = x_date[:8]
        credential = f"{self.access_key}/{date_stamp}/{self.region}/{self.service_name}/request"
        headers['Authorization'] = f"HMAC-SHA256 Credential={credential}, SignedHeaders={signed_headers}, Signature={signature}"

        url = f"{self.base_url}/?{query}"

        logger.info(f"[Celebrity VideoService API] {action} - URL: {url}")
        logger.debug(f"[Celebrity VideoService API] Body: {body}")

        try:
            response = requests.post(url, headers=headers, data=body, timeout=30)
            logger.info(f"[Celebrity VideoService API] Status: {response.status_code}")
            logger.debug(f"[Celebrity VideoService API] Body: {response.text}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"[Celebrity VideoService API] HTTP {e.response.status_code}: {e.response.text}")
            raise Exception(f"{e.response.status_code} {e.response.reason}: {e.response.text}")
        except Exception as e:
            logger.error(f"[Celebrity VideoService API] {type(e).__name__}: {str(e)}")
            raise

    async def create_avatar(self, image_url: str, mode: str = "loopy") -> str:
        """
        步骤1：创建数字形象

        Args:
            image_url: 图片URL
            mode: 模式 - "normal"(普通), "loopy"(灵动), "loopyb"(大画幅灵动)

        Returns:
            resource_id: 形象ID
        """
        req_key_map = {
            "normal": "realman_avatar_picture_create_role",
            "loopy": "realman_avatar_picture_create_role_loopy",
            "loopyb": "realman_avatar_picture_create_role_loopyb"
        }

        params = {
            "req_key": req_key_map.get(mode, "realman_avatar_picture_create_role_loopy"),
            "image_url": image_url
        }

        logger.info(f"[Celebrity VideoService] 开始创建形象 - 模式: {mode}, 图片: {image_url}")

        # 提交任务
        result = self._make_request("CVSubmitTask", params)

        if result.get("code") != 10000:
            raise Exception(f"创建形象失败: {result.get('message')}")

        task_id = result.get("data", {}).get("task_id")
        logger.info(f"[Celebrity VideoService] 任务已提交 - task_id: {task_id}")

        # 轮询查询结果
        max_retries = 60  # 最多等待60秒
        for i in range(max_retries):
            time.sleep(1)

            query_params = {
                "req_key": params["req_key"],
                "task_id": task_id
            }

            query_result = self._make_request("CVGetResult", query_params)

            if query_result.get("code") != 10000:
                raise Exception(f"查询形象失败: {query_result.get('message')}")

            status = query_result.get("data", {}).get("status")

            if status == "done":
                # 解析resource_id
                resp_data_str = query_result.get("data", {}).get("resp_data", "{}")
                resp_data = json.loads(resp_data_str)
                resource_id = resp_data.get("resource_id")

                if resource_id:
                    logger.info(f"[Celebrity VideoService] 成功 - resource_id: {resource_id}")
                    self.cached_resource_id = resource_id
                    return resource_id
                else:
                    raise Exception("形象创建失败，未返回resource_id")

            elif status in ["in_queue", "generating"]:
                logger.info(f"[Celebrity VideoService] 处理中... ({i+1}/{max_retries})")
                continue
            else:
                raise Exception(f"形象创建失败，状态: {status}")

        raise Exception("形象创建超时")

    async def generate_video(self, audio_url: str, resource_id: Optional[str] = None, mode: str = "loopy") -> str:
        """
        步骤2：生成视频

        Args:
            audio_url: 音频URL
            resource_id: 形象ID（如果为None，则使用缓存的ID）
            mode: 模式 - "normal"(普通), "loopy"(灵动), "loopyb"(大画幅灵动)

        Returns:
            video_url: 视频URL
        """
        if not resource_id:
            resource_id = self.cached_resource_id

        if not resource_id:
            raise Exception("未找到形象ID，请先创建形象")

        req_key_map = {
            "normal": "realman_avatar_picture_v2",
            "loopy": "realman_avatar_picture_loopy",
            "loopyb": "realman_avatar_picture_loopyb"
        }

        # 构造请求参数
        req_key = req_key_map.get(mode, "realman_avatar_picture_loopy")

        # 强制请求 H.264 编码以确保浏览器兼容性
        req_json = {
            "video_codec": "h264",
            "video_encoding": "h264",
            "codec": "h264",
            "format": "mp4",
            "enable_watermark": False,
        }

        params = {
            "req_key": req_key,
            "audio_url": audio_url,
            "resource_id": resource_id,
            "req_json": json.dumps(req_json),
            "return_url": True
        }

        logger.info(f"[Celebrity VideoService] 开始生成视频 - 模式: {mode}, 音频: {audio_url}")

        # 提交任务
        result = self._make_request("CVSubmitTask", params)

        if result.get("code") != 10000:
            raise Exception(f"生成视频失败: {result.get('message')}")

        task_id = result.get("data", {}).get("task_id")
        logger.info(f"[Celebrity VideoService] 任务已提交 - task_id: {task_id}")

        # 轮询查询结果
        max_retries = 240  # 最多等待120秒
        sleep_interval = 2 # 每次间隔2秒
        logger.info(f"[Celebrity Video] 开始轮询视频生成状态，最大等待 {max_retries * sleep_interval} 秒...")
        for i in range(max_retries):
            # 还在处理中 (PROCESSING / RUNNING)，等待后重试
            await asyncio.sleep(sleep_interval)

            query_params = {
                "req_key": params["req_key"],
                "task_id": task_id
            }

            query_result = self._make_request("CVGetResult", query_params)

            if query_result.get("code") != 10000:
                raise Exception(f"查询视频失败: {query_result.get('message')}")

            status = query_result.get("data", {}).get("status")

            if status == "done":
                # 解析视频URL
                resp_data_str = query_result.get("data", {}).get("resp_data", "{}")
                resp_data = json.loads(resp_data_str)

                # 打印详细的视频元数据
                video_meta = resp_data.get("video", {}).get("VideoMeta", {})
                codec = video_meta.get('Codec', 'unknown')
                logger.info(f"[Celebrity VideoService] 元数据: Codec={codec}, Format={video_meta.get('Format')}, Size={video_meta.get('Size')}")

                if codec and ('hevc' in codec.lower() or 'h265' in codec.lower()):
                    logger.warning(f"[Celebrity VideoService] 警告：视频使用H.265编码，大多数浏览器不支持！")

                if mode == "loopyb":
                    video_url = query_result.get("data", {}).get("video_url")
                else:
                    resp_data_str = query_result.get("data", {}).get("resp_data", "{}")
                    resp_data = json.loads(resp_data_str)
                    preview_urls = resp_data.get("preview_url", [])
                    video_url = preview_urls[0] if preview_urls else None

                if video_url:
                    logger.info(f"[Celebrity VideoService] 成功 - URL: {video_url}")
                    return video_url
                else:
                    raise Exception("视频生成失败，未返回视频URL")

            elif status in ["in_queue", "generating"]:
                # 仅每10秒打印一次日志，避免日志刷屏
                if i % 5 == 0:
                    logger.info(f"[Celebrity VideoService] 处理中... 状态: {status} ({i+1}/{max_retries})")
                continue
            elif status in ["failed", "cancelled", "fail"]:
                # 尝试提取具体的失败原因
                fail_reason = data.get("fail_reason") or data.get("message") or "未知原因"
                raise Exception(f"视频生成任务失败，状态: {status}，原因: {fail_reason}")
            else:
                raise Exception(f"视频生成失败，状态: {status}")

        raise Exception("视频生成超时")

    async def generate_video_from_text(self, text: str, tts_audio_url: str) -> str:
        """
        完整流程：从文本生成数字人视频

        Args:
            text: 名人回复文本
            tts_audio_url: TTS生成的音频URL

        Returns:
            video_url: 视频URL
        """
        logger.info(f"[Celebrity VideoService] 完整流程开始 - 文本: {text[:50]}...")

        # 如果没有缓存的形象ID，先创建形象
        if not self.cached_resource_id:
            logger.info("[Celebrity VideoService] 首次使用，创建名人形象...")
            from .audio_upload_service import audio_upload_service
            # 获取图片的真实URL（处理OSS签名）
            if not self.celebrity_image_url.startswith("http"):
                image_url = audio_upload_service.get_file_url(self.celebrity_image_url)
            else:
                image_url = self.celebrity_image_url
            await self.create_avatar(image_url, mode="loopy")

        # 生成视频
        video_url = await self.generate_video(tts_audio_url, mode="loopy")

        logger.info(f"[Celebrity VideoService] 完整流程完成 - 视频URL: {video_url}")
        return video_url


# 全局服务实例
celebrity_video_service = CelebrityVideoService()
