"""
面试报告生成器 - 生成Markdown和PDF格式的面试报告
"""
import os
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.models.db_models import (
    InterviewSession,
    InterviewRound,
    InterviewEvaluation
)


class InterviewReportGenerator:
    """面试报告生成器"""

    def __init__(self, db: Session):
        """初始化报告生成器"""
        self.db = db

    async def generate_report(
        self,
        session_id: str,
        format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        生成面试报告

        Args:
            session_id: 会话ID
            format: 格式 (markdown/pdf)

        Returns:
            报告数据
        """
        # 获取会话信息
        session = self.db.query(InterviewSession).filter_by(session_id=session_id).first()
        if not session:
            raise ValueError("会话不存在")

        # 获取所有轮次
        rounds = self.db.query(InterviewRound).filter_by(session_id=session.id).all()

        # 获取最终评估
        evaluation = self.db.query(InterviewEvaluation).filter_by(session_id=session.id).first()

        # 生成Markdown报告
        markdown_content = self._generate_markdown_report(session, rounds, evaluation)

        if format == "markdown":
            return {
                "format": "markdown",
                "content": markdown_content
            }
        elif format == "pdf":
            # PDF生成（简化版，实际应使用WeasyPrint）
            return {
                "format": "pdf",
                "content": markdown_content,
                "message": "PDF生成功能待实现"
            }
        else:
            raise ValueError(f"不支持的格式: {format}")

    def _generate_markdown_report(
        self,
        session: InterviewSession,
        rounds: List[InterviewRound],
        evaluation: InterviewEvaluation
    ) -> str:
        """生成Markdown格式的报告"""
        report = f"""# 面试评估报告

## 基本信息

- **候选人**: {session.candidate_name or '未提供'}
- **面试官**: {session.interviewer_name}
- **面试类型**: {session.interview_type}
- **面试时间**: {session.started_at.strftime('%Y-%m-%d %H:%M:%S') if session.started_at else '未知'}
- **面试时长**: {session.duration_seconds // 60 if session.duration_seconds else 0} 分钟

---

## 综合评估

"""
        if evaluation:
            report += f"""
### 评分概览

| 维度 | 得分 |
|------|------|
| 专业能力 | {evaluation.technical_score}/10 |
| 沟通表达 | {evaluation.communication_score}/10 |
| 问题解决 | {evaluation.problem_solving_score}/10 |
| 文化契合 | {evaluation.cultural_fit_score}/10 |
| **总分** | **{evaluation.total_score}/40** |

**表现等级**: {evaluation.performance_level}

"""

        # 添加面试详情
        report += """
---

## 面试详情

"""
        for i, round_obj in enumerate(rounds, 1):
            report += f"""
### 第 {i} 轮

**问题**: {round_obj.question}

**回答**: {round_obj.answer}

**评估**: {round_obj.answer_quality or '未评估'}

---
"""

        report += """
## 报告生成时间

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return report


