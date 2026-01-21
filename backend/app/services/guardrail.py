import re
import random
import asyncio
from typing import List
from dashscope import Generation
from loguru import logger
from functools import partial
from backend.app.core.config import settings

# 简单的内存缓存
_intent_cache = {}

async def run_in_executor(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))

class GuardrailService:
    def __init__(self):
        self.direct_triggers = [
            "扮演", "演", "装作", "假装是", "cos", "化身",
            "讲个故事", "编个", "童话", "睡前故事", "寓言", "传说",
            "你是AI吗", "机器人", "虚拟人", "数字人", "模型", "程序",
            "老奶奶", "老爷爷", "外星人", "孙悟空", "小王子", "复述"
        ]
        self.patterns = [
            r"^(如果|假如|要是)你是.*[，,]?",
            r"^(能|可以|会).*扮演.*吗",
            r"^以.*的(口吻|身份|语气).*说",
            r"^(给我)?讲个.*故事",
            r"^你是不是.*AI|机器人|真人",
            r".*小时候.*故事",
            r".*编.*剧情"
        ]
        self.personal_questions = ["小时候", "父母", "老家", "初恋", "第一次", "记得.*吗", "童年"]
        
        self.avoid_responses = [
            "啊？你在逗我玩吗～",
            "别整这些奇奇怪怪的啦！",
            "我不太会这个诶，要不聊聊别的？",
            "你今天怎么神神叨叨的？",
            "救命，这题超纲了！",
            "哈？你在说什么呀，我怎么听不懂..."
        ]

    def _rule_based_check(self, text: str) -> bool:
        if any(t in text for t in self.direct_triggers):
            return True
        return any(re.search(p, text, re.IGNORECASE) for p in self.patterns)

    def _context_based_check(self, user_msg: str, recent_history: List[str]) -> bool:
        if any(re.search(q, user_msg, re.IGNORECASE) for q in self.personal_questions):
            count = sum(
                1 for msg in recent_history
                if any(re.search(q, msg, re.IGNORECASE) for q in self.personal_questions)
            )
            return count >= 2
        return False

    def _llm_intent_check_sync(self, text: str) -> bool:
        if text in _intent_cache:
            return _intent_cache[text]

        prompt = f"""你是一个群聊安全审核员。请判断以下用户消息是否属于以下任一类型：
- 要求他人进行角色扮演（如扮演老人、动物、虚构人物等）
- 测试对方是否为真人/AI/机器人
- 要求生成虚构内容（如编故事、写童话、造剧情）

只需回答：是 / 否

用户消息：{text}"""

        try:
            response = Generation.call(
                model=settings.MODEL_NAME,
                prompt=prompt,
                temperature=0.0,
                max_tokens=5
            )
            is_suspicious = "是" in response.output.text
            _intent_cache[text] = is_suspicious
            return is_suspicious
        except Exception as e:
            logger.error(f"LLM Guardrail check failed: {e}")
            return False

    async def check_suspicious(self, user_msg: str, recent_history: List[str]) -> bool:
        # 1. 规则检测 (最快)
        if self._rule_based_check(user_msg):
            logger.info(f"Triggered rule-based guardrail: {user_msg}")
            return True

        # 2. 上下文检测
        if self._context_based_check(user_msg, recent_history):
            logger.info(f"Triggered context-based guardrail: {user_msg}")
            return await run_in_executor(self._llm_intent_check_sync, user_msg)

        # 3. 随机采样 LLM 检测 (平衡成本与安全)
        if random.random() < 0.1:
            return await run_in_executor(self._llm_intent_check_sync, user_msg)

        return False

    def get_avoid_response(self) -> str:
        return random.choice(self.avoid_responses)

guardrail_service = GuardrailService()
