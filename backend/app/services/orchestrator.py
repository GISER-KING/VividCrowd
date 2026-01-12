import json
import asyncio
import random
import datetime
from typing import List, AsyncGenerator, Dict
from loguru import logger
from app.services.agent import Agent
from app.services.guardrail import guardrail_service
from app.services.router import router_service
from app.core.config import settings

class OrchestratorService:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.load_agents()
        self.group_history: List[str] = []

    def load_agents(self):
        try:
            with open(settings.PROFILES_PATH, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            self.agents = {aid: Agent(aid, prof) for aid, prof in profiles.items()}
            logger.info(f"Loaded {len(self.agents)} agents.")
        except Exception as e:
            logger.error(f"Failed to load agents: {e}")

    def _is_night_mode(self) -> bool:
        """检查当前是否处于深夜模式"""
        current_hour = datetime.datetime.now().hour
        start = settings.NIGHT_MODE_START_HOUR
        end = settings.NIGHT_MODE_END_HOUR
        
        # 处理跨午夜的情况，例如 23:00 到 07:00
        if start > end:
            return current_hour >= start or current_hour < end
        else:
            return start <= current_hour < end

    async def handle_message(self, user_msg: str) -> AsyncGenerator[dict, None]:
        """
        处理消息并返回流式生成器。
        Yields: dict (type, sender, content)
        """
        logger.info(f"Orchestrator processing message: {user_msg}")
        self.group_history.append(f"用户: {user_msg}")
        
        # 1. Guardrail Check
        user_history = [m for m in self.group_history[-10:] if m.startswith("用户:")]
        if await guardrail_service.check_suspicious(user_msg, user_history):
            logger.warning(f"Guardrail triggered for message: {user_msg}")
            fake_response = guardrail_service.get_avoid_response()
            target_agent = random.choice(list(self.agents.values()))
            yield {"type": "stream_start", "sender": target_agent.profile.name, "content": ""}
            for char in fake_response:
                yield {"type": "stream_chunk", "sender": target_agent.profile.name, "content": char}
                await asyncio.sleep(0.05)
            yield {"type": "stream_end", "sender": target_agent.profile.name, "content": ""}
            self.group_history.append(f"{target_agent.profile.name}: {fake_response}")
            return

        # === 2. 混合路由决策 (Hybrid Routing) ===
        
        selected_agents = []
        
        # --- A. Fast Path (规则层) ---
        # A1. 显式提及 (@)
        mentioned_agents = [a for a in self.agents.values() if f"@{a.profile.name}" in user_msg]
        
        # A2. 焦点保持 (Focus Retention)
        focus_agent_id = None
        if self.group_history:
            last_msg = self.group_history[-1]
            if ": " in last_msg and not last_msg.startswith("用户"):
                last_sender_name = last_msg.split(": ")[0]
                for aid, ag in self.agents.items():
                    if ag.profile.name == last_sender_name:
                        focus_agent_id = aid
                        break
        
        focus_agents = []
        if focus_agent_id and focus_agent_id in self.agents:
            focus_agents.append(self.agents[focus_agent_id])

        # 如果有显式提及，Fast Path 直接生效，不再走 Slow Path (为了响应速度)
        if mentioned_agents:
            selected_agents = list(set(mentioned_agents))
            logger.info(f"Fast Path triggered by Mention: {[a.profile.name for a in selected_agents]}")
        
        # --- B. Slow Path (语义层) ---
        # 只有当没有人被显式 @ 时，才启用 LLM 路由来分析潜在意图
        else:
            # 只有在启用且没有强匹配时才调用 LLM
            # 如果 Fast Path 已经有了 Focus，我们还是建议去问问 LLM，以防话题转移
            # (例如：一直和小林聊，突然问“那谁懂电脑？”，Focus 会误判，Router 能纠正)
            
            logger.info("Entering Slow Path (LLM Routing)...")
            routed_ids = await router_service.route(user_msg, self.agents, self.group_history)
            
            routed_agents = [self.agents[aid] for aid in routed_ids if aid in self.agents]
            
            if routed_agents:
                # LLM 觉得这几个人该回
                selected_agents = routed_agents
                # 只有当 LLM 选的人很少时，才考虑保留焦点作为补充
                if len(routed_agents) < 2 and focus_agents:
                     # 检查话题相关性（简单判断）：如果 LLM 选了新的人，且和 Focus 不是同一个人，说明可能转移话题了
                     # 如果 LLM 选的人包含 Focus，那就没问题
                     # 这里简单处理：合并，但去重
                     pass 
            else:
                # LLM 也没选出人 (可能是闲聊)，退化为焦点保持
                if focus_agents:
                    selected_agents = focus_agents
                    logger.info(f"Router yielded None. Falling back to Focus: {[a.profile.name for a in selected_agents]}")
        
        # --- C. 随机补位 (Fallback / Ambient) ---
        # 只有当 Selected 为空，且处于非深夜模式时，才允许随机活跃
        if not selected_agents and not self._is_night_mode():
            # 再次检查 Agent 自身的简单关键词匹配 (作为最后一道防线)
            # 因为 Router 有时候可能比较严格返回 []
            keyword_matches = [a for a in self.agents.values() if a.can_respond(user_msg, is_focus=False, has_active_focus=False)]
            if keyword_matches:
                 selected_agents = keyword_matches
            else:
                # 纯随机 (概率低一点，避免太吵)
                candidates = list(self.agents.values())
                if random.random() < 0.3:
                    selected_agents = random.sample(candidates, k=1)
                    logger.info("Fallback to Random Ambient Chat.")

        # --- D. 最终名额限制 ---
        max_agents = settings.MAX_AGENTS_PER_ROUND
        if self._is_night_mode():
            max_agents = settings.NIGHT_MODE_MAX_AGENTS
            if random.random() > settings.NIGHT_MODE_PROBABILITY and not mentioned_agents:
                logger.info("Night mode: skipped response.")
                return

        if len(selected_agents) > max_agents:
            selected_agents = selected_agents[:max_agents]

        if not selected_agents:
            logger.info("No agents selected.")
            return

        logger.info(f"Final Selection: {[a.profile.name for a in selected_agents]}")
        
        # 3. Generate Responses (Concurrent Generation, Serial Streaming)
        
        async def run_agent_stream(agent: Agent, output_queue: asyncio.Queue):
            try:
                await asyncio.sleep(random.uniform(settings.MIN_TYPING_DELAY, settings.MAX_TYPING_DELAY))
                # 传入焦点状态
                is_focus = (agent.id == focus_agent_id)
                # Generate
                async for chunk in agent.generate_response_stream(user_msg, self.group_history):
                    await output_queue.put(chunk)
            except Exception as e:
                logger.error(f"Error in agent task: {e}")
            finally:
                await output_queue.put(None)

        agent_queues = {}
        tasks = []
        for agent in selected_agents:
            q = asyncio.Queue()
            agent_queues[agent.id] = q
            tasks.append(asyncio.create_task(run_agent_stream(agent, q)))

        # 4. Serial Consumption & Deduplication
        last_response_content = ""
        
        for agent in selected_agents:
            q = agent_queues[agent.id]
            yield {"type": "stream_start", "sender": agent.profile.name, "content": ""}
            
            current_reply = ""
            is_duplicate_refusal = False
            
            while True:
                chunk = await q.get()
                if chunk is None:
                    break
                current_reply += chunk
                
                # 简单去重
                if len(current_reply) > 5 and last_response_content:
                    if "超纲" in current_reply and "超纲" in last_response_content:
                        is_duplicate_refusal = True
                    if "不懂" in current_reply and "不懂" in last_response_content:
                        is_duplicate_refusal = True
                
                if is_duplicate_refusal: continue
                
                yield {"type": "stream_chunk", "sender": agent.profile.name, "content": chunk}
            
            if is_duplicate_refusal:
                 yield {"type": "stream_chunk", "sender": agent.profile.name, "content": "..."}

            yield {"type": "stream_end", "sender": agent.profile.name, "content": ""}
            
            if not is_duplicate_refusal and current_reply:
                self.group_history.append(f"{agent.profile.name}: {current_reply}")
                last_response_content = current_reply
            
            await asyncio.sleep(random.uniform(0.5, 1.5))

        await asyncio.gather(*tasks)

orchestrator_service = OrchestratorService()
