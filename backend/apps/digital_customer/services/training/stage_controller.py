"""
阶段控制器 - 管理5个销售阶段的推进逻辑
"""
from typing import Dict, List, Any
from loguru import logger
import json
from backend.models.db_models import TrainingSession, ConversationRound
from backend.core.config import settings
from dashscope import Generation


class StageController:
    """阶段推进控制器"""

    STAGE_CONFIG = {
        1: {
            "name": "信任与关系建立",
            "max_rounds": 3,
            "required_tasks": [
                "判断客户沟通意愿",
                "建立基本沟通条件",
                "调整沟通方式"
            ],
            "completion_criteria": [
                "客户态度从防御转为中性或开放",
                "建立了基本的对话节奏",
                "客户愿意继续沟通"
            ]
        },
        2: {
            "name": "信息探索与需求诊断",
            "max_rounds": 3,
            "required_tasks": [
                "收集客户基本信息",
                "识别客户痛点",
                "明确预算和时间约束",
                "形成需求诊断结构"
            ],
            "completion_criteria": [
                "获得了客户的关键信息",
                "明确了至少2个核心痛点",
                "了解了预算范围"
            ]
        },
        3: {
            "name": "价值呈现与方案链接",
            "max_rounds": 3,
            "required_tasks": [
                "介绍产品/方案",
                "建立需求与方案的对应关系",
                "说明适用边界"
            ],
            "completion_criteria": [
                "客户理解了方案价值",
                "建立了需求-方案映射",
                "客户认可方案相关性"
            ]
        },
        4: {
            "name": "异议/顾虑处理管理",
            "max_rounds": 3,
            "required_tasks": [
                "识别客户异议类型",
                "针对性回应异议",
                "澄清客户顾虑"
            ],
            "completion_criteria": [
                "客户提出了异议",
                "异议得到了回应",
                "客户顾虑被澄清"
            ]
        },
        5: {
            "name": "收尾与成交",
            "max_rounds": 3,
            "required_tasks": [
                "总结沟通要点",
                "推进下一步行动",
                "确认客户意向"
            ],
            "completion_criteria": [
                "明确了下一步",
                "客户表达了意向"
            ]
        }
    }

    def get_stage_name(self, stage: int) -> str:
        """获取阶段名称"""
        return self.STAGE_CONFIG.get(stage, {}).get("name", f"阶段{stage}")

    def get_stage_info(self, stage: int) -> Dict[str, Any]:
        """获取阶段信息"""
        return self.STAGE_CONFIG.get(stage, {})

    def _get_stage_rounds(self, session: TrainingSession, stage: int) -> List[ConversationRound]:
        """获取指定阶段的所有对话轮次"""
        return [r for r in session.rounds if r.stage == stage]

    async def check_stage_completion(
        self,
        session: TrainingSession,
        stage: int,
        current_round: int
    ) -> Dict[str, Any]:
        """检查阶段是否应该推进"""

        config = self.STAGE_CONFIG[stage]
        rounds = self._get_stage_rounds(session, stage)

        # 分析任务完成情况
        completion_analysis = await self._analyze_task_completion(
            rounds,
            config["required_tasks"],
            config["completion_criteria"]
        )

        # 推进逻辑
        should_advance = False
        reason = ""

        if completion_analysis["completion_rate"] >= 0.8:
            # 任务完成度达标，允许推进
            should_advance = True
            reason = "阶段任务已完成"
        elif current_round >= config["max_rounds"]:
            # 达到最大轮次，强制推进
            should_advance = True
            reason = "达到最大轮次，强制推进"

        return {
            "should_advance": should_advance,
            "reason": reason,
            "completion_rate": completion_analysis["completion_rate"],
            "completed_tasks": completion_analysis["completed_tasks"],
            "uncompleted_tasks": completion_analysis["uncompleted_tasks"]
        }

    async def _analyze_task_completion(
        self,
        rounds: List[ConversationRound],
        required_tasks: List[str],
        criteria: List[str]
    ) -> Dict:
        """使用LLM分析任务完成情况"""

        if not rounds:
            return {
                "completed_tasks": [],
                "uncompleted_tasks": required_tasks,
                "completion_rate": 0.0,
                "evidence": {}
            }

        # 构建对话历史
        conversation = "\n".join([
            f"销售: {r.trainee_message}\n客户: {r.customer_response}"
            for r in rounds
        ])

        # 调用Qwen-plus分析
        prompt = f"""分析以下销售对话，判断是否完成了这些任务：

必需任务：
{chr(10).join(f"- {task}" for task in required_tasks)}

完成标准：
{chr(10).join(f"- {c}" for c in criteria)}

对话内容：
{conversation}

请以JSON格式返回：
{{
    "completed_tasks": ["已完成的任务"],
    "uncompleted_tasks": ["未完成的任务"],
    "completion_rate": 0.0-1.0,
    "evidence": {{"任务名": "完成证据"}}
}}

只返回JSON，不要其他内容。"""

        try:
            response = await self._call_qwen_plus(prompt)
            return response
        except Exception as e:
            logger.error(f"Task completion analysis failed: {e}")
            return {
                "completed_tasks": [],
                "uncompleted_tasks": required_tasks,
                "completion_rate": 0.0,
                "evidence": {}
            }

    async def _call_qwen_plus(self, prompt: str) -> Dict:
        """调用Qwen-plus API"""
        try:
            response = Generation.call(
                model='qwen-plus',
                prompt=prompt,
                api_key=settings.DASHSCOPE_API_KEY,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试解析JSON
                try:
                    # 移除可能的markdown代码块标记
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()

                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {content}")
                    return {}
            else:
                logger.error(f"Qwen API error: {response.message}")
                return {}
        except Exception as e:
            logger.error(f"Qwen API call failed: {e}")
            return {}
