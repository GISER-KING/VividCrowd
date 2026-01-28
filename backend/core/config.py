import os
from pydantic_settings import BaseSettings, SettingsConfigDict
import dotenv

# 第一步：在类定义前加载 .env 文件
dotenv.load_dotenv()

class Settings(BaseSettings):
    """应用配置类 - 自动从环境变量/.env 读取"""
    
    # 配置 Pydantic 从 .env 文件和环境变量读取
    model_config = SettingsConfigDict(
        env_file='.env',           # 从 .env 文件读取
        env_file_encoding='utf-8',
        case_sensitive=False,      # 环境变量不区分大小写
        extra='ignore'             # 忽略未定义的环境变量
    )
    
    # === 服务器配置 ===
    HOST: str = "127.0.0.1"
    PORT: int = 8001
    DEBUG: bool = False

    # === 基础配置 ===
    DASHSCOPE_API_KEY: str  # 必填，无默认值（会从环境变量自动读取）
    MODEL_NAME: str = "qwen-max"
    PROFILES_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents_profiles.json")

    # === 聊天行为配置 ===
    MIN_TYPING_DELAY: float = 8.0
    MAX_TYPING_DELAY: float = 10.0
    MAX_AGENTS_PER_ROUND: int = 3

    # === 在线时间控制 ===
    NIGHT_MODE_START_HOUR: int = 23
    NIGHT_MODE_END_HOUR: int = 7
    NIGHT_MODE_PROBABILITY: float = 0.2
    NIGHT_MODE_MAX_AGENTS: int = 1

    # === 人设与风格控制 ===
    STRICT_PERSONA_CHECK: bool = True

    # === 智能路由配置 ===
    ENABLE_LLM_ROUTING: bool = True
    ROUTER_MODEL_NAME: str = "qwen-turbo"

    # === 数字人视频配置 ===
    # 火山引擎
    CELEBRITY_VOLCENGINE_ACCESS_KEY: str  # 必填
    CELEBRITY_VOLCENGINE_SECRET_KEY: str  # 必填
    CELEBRITY_VOLCENGINE_REGION: str = "cn-north-1"
    CELEBRITY_IMAGE_URL: str = "imgs/ElonMask.jpg"

    # 阿里云 OSS
    CELEBRITY_OSS_ACCESS_KEY_ID: str      # 必填
    CELEBRITY_OSS_ACCESS_KEY_SECRET: str  # 必填
    CELEBRITY_OSS_BUCKET_NAME: str = "digitalpatient"
    CELEBRITY_OSS_ENDPOINT: str = "oss-cn-beijing.aliyuncs.com"
    CELEBRITY_OSS_AUDIO_DIR: str = "celebrity_audio"

    # TTS
    CELEBRITY_TTS_VOICE: str = "longxiaochun"
    CELEBRITY_TTS_MODEL: str = "cosyvoice-v1"


# 创建全局配置实例
settings = Settings()

# ✅ 验证：可以直接通过 settings.变量名 访问
# 例如：settings.DASHSCOPE_API_KEY 会自动从环境变量读取