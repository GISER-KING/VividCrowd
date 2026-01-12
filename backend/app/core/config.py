import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # === 基础配置 ===
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    # 升级为 qwen-max 以获得更好的人设扮演能力
    MODEL_NAME: str = "qwen-max"
    PROFILES_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agents_profiles.json")

    # === 聊天行为配置 ===
    # 模拟真人打字/思考延迟（秒）
    # 建议设置在 8.0 - 10.0 秒，模拟真实群聊的打字速度，避免秒回
    MIN_TYPING_DELAY: float = 8.0
    MAX_TYPING_DELAY: float = 10.0
    
    # 每次触发最大回复的 Agent 数量
    MAX_AGENTS_PER_ROUND: int = 3
    
    # === 在线时间控制（新增）===
    # 深夜模式开始时间 (24小时制)
    NIGHT_MODE_START_HOUR: int = 23
    # 深夜模式结束时间
    NIGHT_MODE_END_HOUR: int = 7
    # 深夜模式下的活跃度衰减系数 (0.0 - 1.0)
    # 0.2 表示深夜只有平时 20% 的概率会回复，且回复人数上限也会降低
    NIGHT_MODE_PROBABILITY: float = 0.2
    # 深夜模式下最大回复人数
    NIGHT_MODE_MAX_AGENTS: int = 1

    # === 人设与风格控制 (新增) ===
    # 是否开启严格人设模式
    # True: Agent 会拒绝回答不符合自己身份的问题（如理科生不懂中医），回复更像真人
    # False: Agent 会尽力回答所有问题（容易像百科全书/机器人）
    STRICT_PERSONA_CHECK: bool = True

    # === 智能路由配置 (新增) ===
    # 是否开启 LLM 语义路由 (Slow Path)
    # 开启后，当无法通过规则匹配到回答者时，会调用 LLM 进行分析
    ENABLE_LLM_ROUTING: bool = True
    # 路由使用的模型 (建议使用 turbo 以保证速度，response 使用 max 保证质量)
    ROUTER_MODEL_NAME: str = "qwen-turbo"

    class Config:
        env_file = ".env"

settings = Settings()