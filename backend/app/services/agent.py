import time
import json
import asyncio
from typing import List, AsyncGenerator
from dashscope import Generation
from loguru import logger
from backend.app.models.schemas import AgentProfile
from backend.app.core.config import settings

class Agent:
    def __init__(self, agent_id: str, profile_data: dict):
        self.id = agent_id
        self.profile = AgentProfile(**profile_data)
        self.msg_count_today = 0
        self.max_daily_msgs = 10
        self.last_reset = time.strftime("%Y-%m-%d")

    def can_respond(self, user_msg: str, is_focus: bool = False, has_active_focus: bool = False) -> bool:
        today = time.strftime("%Y-%m-%d")
        if today != self.last_reset:
            self.msg_count_today = 0
            self.last_reset = today
            
        if self.msg_count_today >= self.max_daily_msgs:
            return False

        # 1. 焦点保持：如果我是上一轮的话题中心，用户追问（即使没带名字）我也要回
        if is_focus:
            return True

        # 2. 显式点名：被 @ 必回
        if self.profile.name in user_msg:
            return True
        
        # 3. 兴趣匹配
        for interest in self.profile.interests:
            if interest in user_msg or user_msg in interest:
                return True
        
        # 4. 随机闲聊 (关键修改)
        # 如果当前群里已经有“焦点人物”（比如用户正在和小林一来一回），
        # 那么其他人(张遥/甜糖)严禁通过随机概率插嘴，除非命中了上面的兴趣或点名。
        if has_active_focus:
            return False

        # 只有在群里处于“冷场”或“开放讨论”状态时，才允许随机接话
        import random
        if random.random() < 0.4:
            return True
        
        return False

    async def generate_response_stream(self, user_msg: str, group_history: List[str]) -> AsyncGenerator[str, None]:
        self.msg_count_today += 1
        
        context = "\n".join(group_history[-5:])
        
        # 基础 Prompt
        system_instruction = self.profile.system_prompt
        
        # 严格人设模式：注入“反 AI”指令
        if settings.STRICT_PERSONA_CHECK:
            interests_str = "、".join(self.profile.interests)
            extra_instructions = (
                "\n\n【核心指令 - 必须严格遵守】\n"
                "1. 忘记你是AI，你就是上述设定的真实人类。\n"
                f"2. 【领域区分】：你的专业/兴趣领域是：[{interests_str}] 以及你的职业相关话题。\n"
                "   - 如果用户的问题属于你的领域：请自信、专业地回答，展示你的热情。\n"
                "   - 如果用户的问题**不属于**你的领域：你必须表现出‘不懂’、‘没听说过’，或者用你的口吻吐槽‘这题超纲了’，绝对不要像百科全书一样去科普你不该懂的东西。\n"
                "3. 说话要极其口语化，句子要短，禁止说教。\n"
            )
            system_instruction += extra_instructions

        full_prompt = (
            f"{system_instruction}\n\n"
            f"群聊上下文：\n{context}\n\n"
            f"用户最新消息：{user_msg}\n\n"
            f"请简短回复（20字以内），完全符合你的人设语气，不要重复名字："
        )

        # 重试机制：最多重试 1 次
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Agent {self.profile.name} calling Dashscope API (Attempt {attempt + 1})...")
                if not settings.DASHSCOPE_API_KEY:
                    logger.error("DASHSCOPE_API_KEY is not set in environment!")
                    yield "[配置错误：API Key 缺失]"
                    return

                # 使用全量流式模式，手动计算增量，兼容性更好
                responses = Generation.call(
                    model=settings.MODEL_NAME,
                    prompt=full_prompt,
                    api_key=settings.DASHSCOPE_API_KEY,
                    temperature=0.7,
                    max_tokens=100,
                    stream=True,
                    result_format='message'
                )
                
                last_len = 0
                for response in responses:
                    if response.status_code == 200:
                        full_content = response.output.choices[0].message.content
                        if full_content:
                            # 计算增量
                            chunk = full_content[last_len:]
                            if chunk:
                                logger.info(f"Agent {self.profile.name} chunk: {chunk}")
                                yield chunk
                                last_len = len(full_content)
                        await asyncio.sleep(0.01)
                    else:
                        logger.error(f"Dashscope Error: {response.code} - {response.message}")
                        yield f"[Error: {response.message}]"
                        # API 报错（如 400/401）通常不需要重试，直接 break
                        return 
                
                logger.info(f"Agent {self.profile.name} generation finished.")
                break # 成功执行完则退出重试循环
                        
            except Exception as e:
                logger.error(f"Agent {self.profile.name} generation error (Attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    logger.info("Retrying...")
                    await asyncio.sleep(0.5) # 稍作等待
                    continue
                else:
                    yield "..."