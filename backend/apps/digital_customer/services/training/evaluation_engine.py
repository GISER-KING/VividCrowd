"""
评价引擎 - 实时分析和最终评分
"""
from typing import Dict, List, Any
from loguru import logger
import json
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.db_models import TrainingSession, ConversationRound, StageEvaluation, CustomerChunk
from backend.core.config import settings
from dashscope import Generation


# 评分标准映射表
SCORING_CRITERIA = {
    1: {  # 信任与关系建立
        "task_name": "信任与关系建立",
        "score_1": "未判断客户是否具备沟通意愿；在明显防御状态下直接推进",
        "score_2": "意识到互动问题但未调整沟通方式",
        "score_3": "建立基本沟通条件但不稳定",
        "score_4": "能根据互动状态调整沟通方式",
        "score_5": "明确判断是否具备继续沟通条件并据此决策"
    },
    2: {  # 信息探索与需求诊断
        "task_name": "信息探索与需求诊断",
        "score_1": "未形成任何需求判断",
        "score_2": "收集零散信息但未结构化",
        "score_3": "形成初步问题判断但存在关键缺口",
        "score_4": "判断结构基本完整，个别要素不清",
        "score_5": "形成清晰、可用于决策的需求诊断结构"
    },
    3: {  # 价值呈现与方案链接
        "task_name": "价值呈现与方案链接",
        "score_1": "未建立需求与方案关系",
        "score_2": "仅介绍方案内容，无对应逻辑",
        "score_3": "存在对应尝试但逻辑不完整",
        "score_4": "对应关系基本清晰但边界模糊",
        "score_5": "清晰完成需求—方案映射并说明适用边界"
    },
    4: {  # 异议/顾虑处理管理
        "task_name": "异议/顾虑处理管理",
        "score_1": "忽视明显异议或顾虑",
        "score_2": "注意到异议但未区分类型",
        "score_3": "识别异议但回应方式不匹配",
        "score_4": "异议得到回应但仍存在残留不确定",
        "score_5": "异议被正确识别、分类并得到澄清或确认"
    },
    5: {  # 进程推进与节奏管理
        "task_name": "进程推进与节奏管理",
        "score_1": "多次在信息不足或不匹配时推进",
        "score_2": "出现明显过早或滞后推进",
        "score_3": "推进节奏偶有偏差",
        "score_4": "节奏整体合理，个别节点判断不稳",
        "score_5": "推进/放缓/终止均基于当下信息状态判断"
    }
}


class EvaluationEngine:
    """评价引擎 - 使用Qwen-plus进行智能评价"""

    def _get_stage_criteria(self, stage: int) -> Dict[str, str]:
        """获取阶段评分标准"""
        from .stage_controller import StageController
        controller = StageController()
        stage_info = controller.get_stage_info(stage)
        return {
            "name": stage_info.get("name", f"阶段{stage}"),
            "objectives": ", ".join(stage_info.get("required_tasks", [])),
            "criteria": ", ".join(stage_info.get("completion_criteria", []))
        }

    async def analyze_message(
        self,
        message: str,
        stage: int,
        session: TrainingSession,
        db_session: Session = None
    ) -> Dict[str, Any]:
        """实时分析销售话术质量"""

        stage_criteria = self._get_stage_criteria(stage)

        # 构建客户画像上下文
        customer_context = ""
        if session.customer_profile:
            p = session.customer_profile
            customer_context = f"""
【客户背景知识】
- 客户姓名: {p.name or '未知'}
- 画像类型: {p.profile_type}
- 行业/职业: {p.industry or '未知'} / {p.occupation or '未知'}
- 性格特征: {p.personality_traits or '未知'}
- 痛点: {p.pain_points or '未知'}
- 需求: {p.needs or '未知'}
- 常见异议: {p.objections or '未知'}
"""
            # 如果有db_session，尝试从chunks获取更多上下文（作为补充）
            if db_session:
                try:
                    # 简单获取前2个chunk作为补充背景
                    chunks = db_session.execute(
                        select(CustomerChunk.chunk_text)
                        .where(CustomerChunk.customer_profile_id == p.id)
                        .limit(2)
                    ).scalars().all()
                    if chunks:
                        customer_context += "\n【客户详细背景片段】:\n" + "\n".join([f"- {c[:200]}..." for c in chunks])
                except Exception as e:
                    logger.warning(f"Failed to fetch customer chunks: {e}")

        prompt = f"""你是一位资深销售培训专家。请分析以下销售话术的质量。

{customer_context}

当前阶段：{stage} - {stage_criteria['name']}
阶段目标：{stage_criteria['objectives']}

销售话术：
{message}

请从以下维度评价：
1. 是否符合当前阶段目标
2. 沟通方式是否恰当（考虑到客户的性格和背景）
3. 是否有明显错误
4. 推进节奏是否合理
5. 是否有效针对了客户的痛点或需求（基于客户背景）

返回JSON格式：
{{
    "quality": "excellent/good/fair/poor",
    "issues": ["发现的问题"],
    "suggestions": ["改进建议"]
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_qwen_plus(prompt)
            return result
        except Exception as e:
            logger.error(f"Message analysis failed: {e}")
            return {
                "quality": "fair",
                "issues": [],
                "suggestions": []
            }

    def _get_stage_rounds(self, session: TrainingSession, stage: int) -> List[ConversationRound]:
        """获取指定阶段的所有对话轮次"""
        return [r for r in session.rounds if r.stage == stage]

    def _format_conversation(self, rounds: List[ConversationRound]) -> str:
        """格式化对话内容"""
        return "\n\n".join([
            f"【第{r.round_number}轮】\n销售: {r.trainee_message}\n客户: {r.customer_response}"
            for r in rounds
        ])

    async def evaluate_stage(
        self,
        session: TrainingSession,
        stage: int
    ) -> Dict[str, Any]:
        """评价单个阶段的表现"""

        rounds = self._get_stage_rounds(session, stage)

        if not rounds:
            return {
                "score": 1,
                "strengths": [],
                "weaknesses": ["未进行有效沟通"],
                "suggestions": ["需要主动开启对话"],
                "evidence": "无对话记录"
            }

        # 构建完整对话
        conversation = self._format_conversation(rounds)

        # 获取评分标准
        criteria = SCORING_CRITERIA.get(stage, {})

        prompt = f"""评价销售在"{criteria['task_name']}"阶段的表现。

评分标准（1-5分）：
1分：{criteria['score_1']}
2分：{criteria['score_2']}
3分：{criteria['score_3']}
4分：{criteria['score_4']}
5分：{criteria['score_5']}

对话内容：
{conversation}

返回JSON：
{{
    "score": 1-5,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"],
    "suggestions": ["建议1", "建议2"],
    "evidence": "评分依据"
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_qwen_plus(prompt)
            # 确保score在1-5范围内
            if "score" in result:
                result["score"] = max(1, min(5, result["score"]))
            return result
        except Exception as e:
            logger.error(f"Stage evaluation failed: {e}")
            return {
                "score": 3,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "evidence": "评价失败"
            }

    async def generate_final_report(
        self,
        session: TrainingSession,
        scores: Dict[str, int]
    ) -> Dict[str, Any]:
        """生成最终评价报告"""

        # 收集所有对话
        all_rounds = session.rounds
        full_conversation = self._format_conversation(all_rounds)

        # 收集阶段评价
        stage_evaluations = {}
        for eval in session.stage_evaluations:
            stage_evaluations[eval.stage_number] = {
                "score": eval.score,
                "strengths": eval.strengths or [],
                "weaknesses": eval.weaknesses or []
            }

        prompt = f"""生成销售培训的最终评价报告。

5项核心任务得分：
1. 信任与关系建立：{scores.get('trust_building', 0)}/5
2. 信息探索与需求诊断：{scores.get('needs_diagnosis', 0)}/5
3. 价值呈现与方案链接：{scores.get('value_presentation', 0)}/5
4. 异议处理管理：{scores.get('objection_handling', 0)}/5
5. 进程推进与节奏管理：{scores.get('progress_management', 0)}/5

总分：{scores.get('total', 0)}/25

各阶段详细评价：
{json.dumps(stage_evaluations, ensure_ascii=False, indent=2)}

完整对话记录：
{full_conversation}

请生成：
1. 整体表现总结
2. 核心优势（3-5条）
3. 主要不足（3-5条）
4. 关键改进建议（5-8条）
5. 未完成的任务列表

返回JSON格式：
{{
    "overall_summary": "整体表现总结",
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["不足1", "不足2", "不足3"],
    "improvements": ["建议1", "建议2", "建议3", "建议4", "建议5"],
    "uncompleted_tasks": ["未完成任务1", "未完成任务2"]
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_qwen_plus(prompt)
            return result
        except Exception as e:
            logger.error(f"Final report generation failed: {e}")
            return {
                "overall_summary": "评价报告生成失败",
                "strengths": [],
                "weaknesses": [],
                "improvements": [],
                "uncompleted_tasks": []
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
