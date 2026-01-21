import json
import asyncio
from typing import List, Dict
from dashscope import Generation
from loguru import logger
from backend.core.config import settings
from .agent import Agent

class RouterService:
    def __init__(self):
        self.model_name = settings.ROUTER_MODEL_NAME

    def _build_routing_prompt(self, user_msg: str, agents: Dict[str, Agent], history: List[str]) -> str:
        """构建路由 Prompt"""
        agents_desc = []
        for aid, agent in agents.items():
            desc = (
                f"- ID: {aid}\n"
                f"  Name: {agent.profile.name}\n"
                f"  Role: {agent.profile.occupation}\n"
                f"  Interests: {', '.join(agent.profile.interests)}\n"
                f"  Traits: {', '.join(agent.profile.personality_traits)}"
            )
            agents_desc.append(desc)

        agents_text = "\n".join(agents_desc)

        # 截取最近 5 条历史记录，帮助理解上下文
        recent_history_text = "\n".join(history[-5:]) if history else "No history."

        prompt = f"""You are the coordinator of a group chat. Your task is to analyze the user's message and decide which agent(s) should respond.

### Available Agents:
{agents_text}

### Recent Chat History (Context):
{recent_history_text}

### User Message:
"{user_msg}"

### Instructions:
1. Analyze the semantic meaning of the message **in the context of Recent Chat History**. Resolve references like "it", "this", "continue", or "write one".
2. Select 1-2 agents whose persona/interests match the topic BEST.
3. **CRITICAL**: If the conversation is technically specific (e.g. coding, medicine) and a relevant expert is already handling it, **DO NOT** select other agents unless explicitly asked.
4. If the message is a general greeting or unrelated to anyone's expertise, select the most socially active agent.
5. If the message is explicitly for someone (e.g. by context), select them.
6. **Output strictly valid JSON** list of Agent IDs. Example: ["xiaolin", "zhangyao"]

### JSON Output:"""
        return prompt

    async def route(self, user_msg: str, agents: Dict[str, Agent], history: List[str]) -> List[str]:
        """
        执行语义路由
        Returns: List of agent_ids
        """
        if not settings.ENABLE_LLM_ROUTING:
            return []

        prompt = self._build_routing_prompt(user_msg, agents, history)

        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                # 使用 run_in_executor 避免阻塞主线程
                # 这里简化直接调用，因为 Dashscope http request 耗时主要在网络
                # 生产环境建议包装在 executor 中
                response = Generation.call(
                    model=self.model_name,
                    prompt=prompt,
                    api_key=settings.DASHSCOPE_API_KEY,
                    result_format='message',
                    temperature=0.1  # 低温度，保证决策稳定性
                )

                if response.status_code == 200:
                    content = response.output.choices[0].message.content
                    # 清洗可能的 markdown 标记
                    content = content.replace("```json", "").replace("```", "").strip()

                    try:
                        selected_ids = json.loads(content)
                        if isinstance(selected_ids, list):
                            # 过滤掉不存在的 ID
                            valid_ids = [aid for aid in selected_ids if aid in agents]
                            logger.info(f"LLM Router selected: {valid_ids}")
                            return valid_ids
                    except json.JSONDecodeError:
                        logger.warning(f"Router returned invalid JSON: {content}")
                        # JSON 解析失败属于模型问题，重试可能也没用，但也试一下吧
                else:
                    logger.error(f"Router API failed: {response.code} - {response.message}")

                # 如果成功拿到 response 但 status_code!=200 或者解析失败，进入下一次重试
                if attempt < max_retries:
                    logger.warning(f"Router retrying (Attempt {attempt + 1})...")
                    continue

            except Exception as e:
                logger.error(f"Router exception (Attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    logger.warning("Router connection failed, retrying...")
                    await asyncio.sleep(0.5)
                    continue

        return []

router_service = RouterService()
