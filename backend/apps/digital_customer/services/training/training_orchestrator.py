"""
培训编排器 - 管理整个培训流程的核心控制器
"""
from typing import AsyncGenerator, Dict, Any
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.models.db_models import (
    TrainingSession, ConversationRound, StageEvaluation,
    FinalEvaluation, CustomerProfile
)
from backend.apps.digital_customer.services.customer_agent import CustomerAgent
from .stage_controller import StageController
from .evaluation_engine import EvaluationEngine


class TrainingOrchestrator:
    """销售培训编排器 - 核心控制器"""

    def __init__(self, db: Session):
        self.db = db
        self.stage_controller = StageController()
        self.evaluation_engine = EvaluationEngine()

    def _get_training_session(self, session_id: str) -> TrainingSession:
        """获取培训会话"""
        result = self.db.execute(
            select(TrainingSession).where(TrainingSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def handle_training_message(
        self,
        session_id: str,
        trainee_message: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理培训对话消息"""

        # 1. 获取培训会话
        session = self._get_training_session(session_id)
        if not session:
            yield {
                "type": "error",
                "sender": "System",
                "content": "培训会话不存在"
            }
            return

        # 2. 获取当前阶段信息
        current_stage = session.current_stage
        current_round = session.current_round + 1

        # 3. 实时分析销售话术
        analysis = await self.evaluation_engine.analyze_message(
            trainee_message,
            current_stage,
            session,
            self.db
        )

        yield {
            "type": "analysis",
            "stage": current_stage,
            "round": current_round,
            "quality": analysis.get("quality", "fair"),
            "issues": analysis.get("issues", []),
            "suggestions": analysis.get("suggestions", [])
        }

        # 4. 获取客户画像
        customer = session.customer_profile

        # 5. 构建增强的训练上下文
        enhanced_context = self._build_training_context(
            session,
            current_stage,
            analysis
        )

        # 6. 生成客户响应（使用CustomerAgent）
        from backend.core.database import digital_customer_async_session
        async with digital_customer_async_session() as async_session:
            agent = CustomerAgent(customer, db_session=async_session)

            yield {"type": "stream_start", "sender": customer.name, "content": ""}

            full_response = ""
            async for chunk in agent.generate_response_stream(
                trainee_message,
                [enhanced_context],
                mode="private"
            ):
                full_response += chunk
                yield {"type": "stream_chunk", "sender": customer.name, "content": chunk}

            yield {"type": "stream_end", "sender": customer.name, "content": ""}

        # 7. 记录对话轮次
        conversation_round = ConversationRound(
            session_id=session.id,
            round_number=current_round,
            stage=current_stage,
            trainee_message=trainee_message,
            customer_response=full_response,
            detected_quality=analysis.get("quality"),
            analysis_data=analysis
        )
        self.db.add(conversation_round)
        self.db.flush()

        # 8. 检查阶段完成度
        stage_completion = await self.stage_controller.check_stage_completion(
            session,
            current_stage,
            current_round
        )

        if stage_completion["should_advance"]:
            # 生成阶段评价
            stage_eval_data = await self.evaluation_engine.evaluate_stage(
                session,
                current_stage
            )

            # 保存阶段评价
            stage_eval = StageEvaluation(
                session_id=session.id,
                stage_number=current_stage,
                stage_name=self.stage_controller.get_stage_name(current_stage),
                task_completed=stage_completion["completion_rate"] >= 0.8,
                completion_quality="excellent" if stage_completion["completion_rate"] >= 0.9 else "good" if stage_completion["completion_rate"] >= 0.7 else "fair",
                strengths=stage_eval_data.get("strengths", []),
                weaknesses=stage_eval_data.get("weaknesses", []),
                suggestions=stage_eval_data.get("suggestions", []),
                score=stage_eval_data.get("score", 3),
                completed_at=datetime.utcnow(),
                rounds_used=current_round
            )
            self.db.add(stage_eval)
            self.db.flush()

            yield {
                "type": "stage_complete",
                "stage": current_stage,
                "score": stage_eval_data.get("score", 3),
                "feedback": f"优点：{', '.join(stage_eval_data.get('strengths', []))}\n\n不足：{', '.join(stage_eval_data.get('weaknesses', []))}"
            }

            # 推进到下一阶段
            session.current_stage += 1
            session.current_round = 0

            if session.current_stage > 5:
                # 培训结束，生成最终评价
                final_eval = await self._generate_final_evaluation(session)
                yield {
                    "type": "training_complete",
                    "evaluation": final_eval
                }
        else:
            session.current_round = current_round

        self.db.commit()

    def _build_training_context(
        self,
        session: TrainingSession,
        stage: int,
        analysis: Dict
    ) -> str:
        """构建训练上下文 - 指导AI客户的行为"""

        stage_prompts = {
            1: "你处于初次接触阶段，保持中性态度。如果销售表现良好，可以逐渐开放；如果表现不佳，保持防御。",
            2: "销售正在探索你的需求。根据他们的提问质量，决定透露多少信息。如果问题精准，提供详细信息；如果问题模糊，给出简短回答。",
            3: "销售正在介绍方案。如果他们能清晰地将方案与你的需求关联，表现出兴趣；如果只是泛泛介绍，表现出疑虑。",
            4: "你应该提出一些合理的异议或顾虑，测试销售的应对能力。根据他们的回应质量，决定是否被说服。",
            5: "根据前面的沟通质量，决定是否推进成交。如果销售表现优秀，表达明确意向；如果表现一般，保持观望。"
        }

        context = f"""【培训模式 - 请严格遵守以下指导】

当前培训阶段：第{stage}阶段 - {self.stage_controller.get_stage_name(stage)}

你的行为指导：
{stage_prompts.get(stage, "正常互动")}

销售表现分析：
- 沟通质量：{analysis.get('quality', '未知')}
- 发现的问题：{', '.join(analysis.get('issues', [])) if analysis.get('issues') else '无'}

重要提示：
1. 你是在培训场景中扮演客户，需要根据销售的表现调整你的反应
2. 如果销售表现好，你应该更配合；如果表现差，你应该更挑剔
3. 保持真实客户的行为模式，不要过于配合或过于刁难
4. 回复要简洁自然，像真实对话一样

请根据以上信息，以客户身份自然回应销售的话术。"""

        return context

    async def _generate_final_evaluation(
        self,
        session: TrainingSession
    ) -> Dict[str, Any]:
        """生成最终评价报告"""

        # 收集所有阶段评价
        stage_evals = session.stage_evaluations

        # 计算5项核心任务得分
        scores = self._calculate_final_scores(session, stage_evals)

        # 生成详细报告
        report = await self.evaluation_engine.generate_final_report(
            session,
            scores
        )

        # 计算总分和等级
        total_score = scores["total"]
        if total_score >= 20:
            performance_level = "excellent"
        elif total_score >= 15:
            performance_level = "good"
        elif total_score >= 10:
            performance_level = "average"
        else:
            performance_level = "poor"

        # 保存到数据库
        final_eval = FinalEvaluation(
            session_id=session.id,
            trust_building_score=scores["trust_building"],
            needs_diagnosis_score=scores["needs_diagnosis"],
            value_presentation_score=scores["value_presentation"],
            objection_handling_score=scores["objection_handling"],
            progress_management_score=scores["progress_management"],
            total_score=total_score,
            performance_level=performance_level,
            overall_strengths=report.get("strengths", []),
            overall_weaknesses=report.get("weaknesses", []),
            key_improvements=report.get("improvements", []),
            uncompleted_tasks=report.get("uncompleted_tasks", []),
            detailed_report=report.get("overall_summary", "")
        )

        self.db.add(final_eval)

        # 更新会话状态
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.duration_seconds = int((session.completed_at - session.started_at).total_seconds())

        self.db.commit()

        # 返回评价数据
        return {
            "session_id": session.session_id,
            "trainee_name": session.trainee_name,
            "scenario_name": "销售培训场景",
            "completed_at": session.completed_at.isoformat(),
            "duration_minutes": session.duration_seconds // 60,
            "scores": {
                "trust_building_score": scores["trust_building"],
                "needs_diagnosis_score": scores["needs_diagnosis"],
                "value_presentation_score": scores["value_presentation"],
                "objection_handling_score": scores["objection_handling"],
                "progress_management_score": scores["progress_management"],
                "total_score": total_score,
                "performance_level": performance_level
            },
            "overall_strengths": report.get("strengths", []),
            "overall_weaknesses": report.get("weaknesses", []),
            "key_improvements": report.get("improvements", []),
            "uncompleted_tasks": report.get("uncompleted_tasks", []),
            "stage_details": [
                {
                    "stage": eval.stage_number,
                    "stage_name": eval.stage_name,
                    "score": eval.score,
                    "rounds_used": eval.rounds_used,
                    "strengths": eval.strengths or [],
                    "weaknesses": eval.weaknesses or [],
                    "suggestions": eval.suggestions or []
                }
                for eval in stage_evals
            ]
        }

    def _calculate_final_scores(
        self,
        session: TrainingSession,
        stage_evals: list
    ) -> Dict[str, int]:
        """计算最终得分"""

        # 从阶段评价中提取得分
        stage_scores = {eval.stage_number: eval.score or 3 for eval in stage_evals}

        # 映射到5项核心任务
        scores = {
            "trust_building": stage_scores.get(1, 3),  # 阶段1
            "needs_diagnosis": stage_scores.get(2, 3),  # 阶段2
            "value_presentation": stage_scores.get(3, 3),  # 阶段3
            "objection_handling": stage_scores.get(4, 3),  # 阶段4
            "progress_management": stage_scores.get(5, 3),  # 阶段5
        }

        scores["total"] = sum(scores.values())

        return scores
