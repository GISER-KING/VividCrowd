"""
面试编排器 - 协调整个面试流程
"""
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from interviewer_agent import InterviewerAgent
from backend.apps.digital_interviewer.services.evaluation_engine import InterviewEvaluationEngine
from backend.apps.digital_interviewer.services.experience_service import ExperienceService
from backend.models.db_models import (
    InterviewerProfile,
    InterviewSession,
    InterviewRound,
    InterviewEvaluation,
    InterviewKnowledge
)


class InterviewOrchestrator:
    """面试编排器"""

    def __init__(self, db: Session, api_key: str = None, base_url: str = None):
        """初始化编排器"""
        self.db = db
        self.api_key = api_key
        self.base_url = base_url
        self.evaluation_engine = InterviewEvaluationEngine(api_key, base_url)

        # 活跃的Agent实例
        self.active_agents: Dict[str, InterviewerAgent] = {}

    async def start_interview(
        self,
        session_id: str,
        experience_set_ids: List[int] = None,
        experience_mode: str = "none"
    ) -> Dict[str, Any]:
        """
        开始面试

        Args:
            session_id: 会话ID
            experience_set_ids: 面经集ID列表
            experience_mode: 面经使用模式 (none/reference/strict/mixed)

        Returns:
            第一个问题和状态
        """
        # 获取会话信息
        session = self.db.query(InterviewSession).filter_by(session_id=session_id).first()
        if not session:
            raise ValueError("会话不存在")

        # 获取面试官信息
        interviewer = self.db.query(InterviewerProfile).filter_by(
            id=session.interviewer_profile_id
        ).first()
        if not interviewer:
            raise ValueError("面试官不存在")

        # 获取参考问题（如果选择了面经集）
        reference_questions = []
        if experience_set_ids and experience_mode != "none":
            experience_service = ExperienceService(db=self.db)
            reference_questions = experience_service.get_questions_by_sets(experience_set_ids)

        # 获取简历数据（如果有关联简历）
        resume_data = None
        if session.resume_id:
            from backend.models.db_models import CandidateResume
            resume = self.db.query(CandidateResume).filter_by(id=session.resume_id).first()
            if resume and resume.parsed_data:
                resume_data = resume.parsed_data

        # 创建Agent实例
        profile_data = {
            "name": interviewer.name,
            "title": interviewer.title,
            "company": interviewer.company,
            "expertise_areas": interviewer.expertise_areas,
            "system_prompt": interviewer.system_prompt
        }

        agent = InterviewerAgent(
            profile_data=profile_data,
            interview_type=session.interview_type,
            reference_questions=reference_questions,
            experience_mode=experience_mode,
            resume_data=resume_data,
            api_key=self.api_key,
            base_url=self.base_url
        )

        self.active_agents[session_id] = agent

        # 生成第一个问题
        question_data = await agent.generate_question(round_number=1)

        # 保存轮次
        round_obj = InterviewRound(
            session_id=session.id,
            round_number=1,
            question=question_data['question'],
            answer="",  # 待填充
            question_type=question_data.get('question_type'),
            is_followup=False
        )
        self.db.add(round_obj)

        # 更新会话
        session.current_round = 1
        session.total_rounds = 1
        self.db.commit()

        return {
            "question": question_data['question'],
            "round_number": 1,
            "video_state": "speaking"
        }

    async def process_answer(
        self,
        session_id: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        处理候选人回答

        Args:
            session_id: 会话ID
            answer: 候选人回答

        Returns:
            下一步动作（新问题或结束）
        """
        # 获取会话
        session = self.db.query(InterviewSession).filter_by(session_id=session_id).first()
        if not session:
            raise ValueError("会话不存在")

        # 获取Agent
        agent = self.active_agents.get(session_id)
        if not agent:
            raise ValueError("Agent不存在")

        # 获取当前轮次
        current_round = self.db.query(InterviewRound).filter_by(
            session_id=session.id,
            round_number=session.current_round
        ).first()

        if not current_round:
            raise ValueError("当前轮次不存在")

        # 更新回答
        current_round.answer = answer
        self.db.commit()

        # 评估回答
        evaluation = await self.evaluation_engine.evaluate_answer(
            question=current_round.question,
            answer=answer,
            interview_type=session.interview_type
        )

        # 保存评估结果
        current_round.answer_quality = evaluation.get('quality', 'fair')
        current_round.evaluation_data = evaluation
        self.db.commit()

        # 决定下一步
        max_rounds = session.max_rounds or 5  # 使用会话配置的轮数，默认5轮
        should_continue = session.current_round < max_rounds

        if should_continue:
            # 生成下一个问题
            next_round = session.current_round + 1
            question_data = await agent.generate_question(
                round_number=next_round,
                previous_answer=answer
            )

            # 保存新轮次
            round_obj = InterviewRound(
                session_id=session.id,
                round_number=next_round,
                question=question_data['question'],
                answer="",
                question_type=question_data.get('question_type'),
                is_followup=question_data.get('is_followup', False)
            )
            self.db.add(round_obj)

            # 更新会话
            session.current_round = next_round
            session.total_rounds = next_round
            self.db.commit()

            return {
                "action": "continue",
                "question": question_data['question'],
                "round_number": next_round,
                "video_state": "speaking",
                "evaluation": evaluation
            }
        else:
            # 结束面试
            return await self.end_interview(session_id)

    async def end_interview(self, session_id: str) -> Dict[str, Any]:
        """
        结束面试并生成最终评估

        Args:
            session_id: 会话ID

        Returns:
            最终评估结果
        """
        # 获取会话
        session = self.db.query(InterviewSession).filter_by(session_id=session_id).first()
        if not session:
            raise ValueError("会话不存在")

        # 获取所有轮次
        rounds = self.db.query(InterviewRound).filter_by(session_id=session.id).all()
        rounds_data = [
            {
                "question": r.question,
                "answer": r.answer,
                "evaluation_data": r.evaluation_data
            }
            for r in rounds
        ]

        # 生成最终评估
        final_eval = await self.evaluation_engine.generate_final_evaluation(
            rounds=rounds_data,
            interview_type=session.interview_type
        )

        # 保存最终评估
        evaluation = InterviewEvaluation(
            session_id=session.id,
            technical_score=final_eval['technical_score'],
            communication_score=final_eval['communication_score'],
            problem_solving_score=final_eval['problem_solving_score'],
            cultural_fit_score=final_eval['cultural_fit_score'],
            total_score=final_eval['total_score'],
            performance_level=final_eval['performance_level'],
            strengths=final_eval.get('strengths', []),
            weaknesses=final_eval.get('weaknesses', []),
            suggestions=final_eval.get('suggestions', [])
        )
        self.db.add(evaluation)

        # 更新会话状态
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        if session.started_at:
            duration = (datetime.utcnow() - session.started_at).total_seconds()
            session.duration_seconds = int(duration)

        self.db.commit()

        # 清理Agent
        if session_id in self.active_agents:
            del self.active_agents[session_id]

        return {
            "action": "end",
            "evaluation": final_eval,
            "video_state": "idle"
        }


