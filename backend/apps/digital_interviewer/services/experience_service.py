"""
面经管理服务 - 管理面经集的CRUD操作
"""
import os
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger

from backend.models.db_models import InterviewExperienceSet, InterviewKnowledge
from backend.apps.digital_interviewer.services.experience_parser import ExperienceParser


class ExperienceService:
    """面经管理服务"""

    def __init__(self, db: Session, api_key: str = None, base_url: str = None):
        """初始化服务"""
        self.db = db
        self.parser = ExperienceParser(api_key=api_key, base_url=base_url)

    async def create_experience_set(
        self,
        name: str,
        file_path: str,
        interview_type: str = "technical",
        description: str = None,
        company: str = None,
        position: str = None
    ) -> InterviewExperienceSet:
        """
        创建面经集并解析PDF

        Args:
            name: 面经集名称
            file_path: PDF文件路径
            interview_type: 面试类型
            description: 描述
            company: 目标公司
            position: 目标职位

        Returns:
            创建的面经集对象
        """
        logger.info(f"开始创建面经集: {name}")

        # 解析PDF
        parse_result = await self.parser.parse_pdf(file_path)

        # 创建面经集
        experience_set = InterviewExperienceSet(
            name=name,
            description=description or parse_result.get("title"),
            source_filename=os.path.basename(file_path),
            company=company or parse_result.get("company"),
            position=position or parse_result.get("position"),
            interview_type=interview_type or parse_result.get("interview_type", "technical"),
            question_count=len(parse_result.get("questions", [])),
            is_active=True
        )
        self.db.add(experience_set)
        self.db.flush()  # 获取ID

        # 保存问题到知识库
        questions = parse_result.get("questions", [])
        for q in questions:
            knowledge = InterviewKnowledge(
                interview_type=interview_type,
                category=q.get("category"),
                content=q.get("question", ""),
                difficulty_level=q.get("difficulty"),
                source_filename=os.path.basename(file_path),
                experience_set_id=experience_set.id,
                question_text=q.get("question", ""),
                reference_answer=q.get("answer"),
                tags=q.get("tags")
            )
            self.db.add(knowledge)

        self.db.commit()
        self.db.refresh(experience_set)

        logger.info(f"面经集创建成功，ID: {experience_set.id}，问题数: {experience_set.question_count}")
        return experience_set

    def get_experience_sets(
        self,
        interview_type: str = None,
        active_only: bool = True
    ) -> List[InterviewExperienceSet]:
        """
        获取面经集列表

        Args:
            interview_type: 按面试类型筛选
            active_only: 是否只返回激活的面经集

        Returns:
            面经集列表
        """
        query = self.db.query(InterviewExperienceSet)

        if active_only:
            query = query.filter(InterviewExperienceSet.is_active == True)

        if interview_type:
            query = query.filter(InterviewExperienceSet.interview_type == interview_type)

        return query.order_by(InterviewExperienceSet.created_at.desc()).all()

    def get_experience_set(self, set_id: int) -> Optional[InterviewExperienceSet]:
        """获取单个面经集"""
        return self.db.query(InterviewExperienceSet).filter_by(id=set_id).first()

    def get_questions_by_set(self, set_id: int) -> List[InterviewKnowledge]:
        """
        获取面经集中的问题

        Args:
            set_id: 面经集ID

        Returns:
            问题列表
        """
        return self.db.query(InterviewKnowledge).filter_by(
            experience_set_id=set_id
        ).all()

    def get_questions_by_sets(self, set_ids: List[int]) -> List[Dict[str, Any]]:
        """
        获取多个面经集中的问题

        Args:
            set_ids: 面经集ID列表

        Returns:
            问题列表（字典格式）
        """
        questions = self.db.query(InterviewKnowledge).filter(
            InterviewKnowledge.experience_set_id.in_(set_ids)
        ).all()

        return [
            {
                "question": q.question_text or q.content,
                "answer": q.reference_answer,
                "category": q.category,
                "difficulty": q.difficulty_level,
                "tags": q.tags
            }
            for q in questions
        ]

    def delete_experience_set(self, set_id: int) -> bool:
        """
        删除面经集

        Args:
            set_id: 面经集ID

        Returns:
            是否删除成功
        """
        experience_set = self.db.query(InterviewExperienceSet).filter_by(id=set_id).first()
        if not experience_set:
            return False

        # 删除关联的问题（通过cascade自动删除）
        self.db.delete(experience_set)
        self.db.commit()

        logger.info(f"面经集已删除，ID: {set_id}")
        return True

    def update_experience_set(
        self,
        set_id: int,
        name: str = None,
        description: str = None,
        is_active: bool = None
    ) -> Optional[InterviewExperienceSet]:
        """
        更新面经集

        Args:
            set_id: 面经集ID
            name: 新名称
            description: 新描述
            is_active: 是否激活

        Returns:
            更新后的面经集
        """
        experience_set = self.db.query(InterviewExperienceSet).filter_by(id=set_id).first()
        if not experience_set:
            return None

        if name is not None:
            experience_set.name = name
        if description is not None:
            experience_set.description = description
        if is_active is not None:
            experience_set.is_active = is_active

        self.db.commit()
        self.db.refresh(experience_set)

        return experience_set
