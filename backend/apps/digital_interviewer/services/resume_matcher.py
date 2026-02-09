"""
简历职位匹配服务 - 计算简历与职位的匹配度
"""
from typing import Dict, Any, List, Set
from sqlalchemy.orm import Session

from backend.models.db_models import CandidateResume, ResumeAnalysis, JobPosition, ResumeJobMatch


class ResumeMatcher:
    """简历职位匹配器"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_match(
        self,
        resume_id: int,
        job_id: int
    ) -> Dict[str, Any]:
        """
        计算简历与职位的匹配度

        Args:
            resume_id: 简历ID
            job_id: 职位ID

        Returns:
            匹配结果字典
        """
        # 获取简历和职位信息
        resume = self.db.query(CandidateResume).filter(CandidateResume.id == resume_id).first()
        if not resume:
            raise ValueError(f"简历不存在: {resume_id}")

        analysis = self.db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_id).first()
        if not analysis:
            raise ValueError(f"简历分析结果不存在: {resume_id}")

        job = self.db.query(JobPosition).filter(JobPosition.id == job_id).first()
        if not job:
            raise ValueError(f"职位不存在: {job_id}")

        # 计算各维度匹配度
        skill_match = self._calculate_skill_match(analysis, job)
        experience_match = self._calculate_experience_match(analysis, job)
        education_match = self._calculate_education_match(analysis, job)

        # 计算综合匹配度（加权平均）
        weights = {
            'skill': 0.5,
            'experience': 0.3,
            'education': 0.2
        }

        match_score = int(
            skill_match['score'] * weights['skill'] +
            experience_match['score'] * weights['experience'] +
            education_match['score'] * weights['education']
        )

        # 确定优先级
        priority = self._determine_priority(match_score)

        # 生成建议
        recommendations = self._generate_recommendations(
            skill_match, experience_match, education_match, match_score
        )

        return {
            "match_score": match_score,
            "skill_match_score": skill_match['score'],
            "experience_match_score": experience_match['score'],
            "education_match_score": education_match['score'],
            "matched_skills": skill_match['matched'],
            "missing_skills": skill_match['missing'],
            "match_details": {
                "skill_details": skill_match,
                "experience_details": experience_match,
                "education_details": education_match
            },
            "priority": priority,
            "recommendations": recommendations
        }

    def _calculate_skill_match(
        self,
        analysis: ResumeAnalysis,
        job: JobPosition
    ) -> Dict[str, Any]:
        """计算技能匹配度"""
        candidate_skills = set(analysis.skill_tags or [])
        required_skills = set(job.skills_required or [])
        preferred_skills = set(job.skills_preferred or [])

        # 计算匹配的技能
        matched_required = candidate_skills & required_skills
        matched_preferred = candidate_skills & preferred_skills
        missing_required = required_skills - candidate_skills

        # 计算分数
        if not required_skills:
            score = 100  # 没有技能要求，默认满分
        else:
            required_match_rate = len(matched_required) / len(required_skills)
            preferred_match_rate = len(matched_preferred) / len(preferred_skills) if preferred_skills else 0
            score = int(required_match_rate * 80 + preferred_match_rate * 20)

        return {
            "score": score,
            "matched": list(matched_required | matched_preferred),
            "missing": list(missing_required),
            "candidate_skills": list(candidate_skills),
            "required_skills": list(required_skills),
            "preferred_skills": list(preferred_skills)
        }

    def _calculate_experience_match(
        self,
        analysis: ResumeAnalysis,
        job: JobPosition
    ) -> Dict[str, Any]:
        """计算工作经验匹配度"""
        candidate_years = analysis.total_work_years or 0
        min_years = job.experience_years_min or 0
        max_years = job.experience_years_max or 999

        # 计算分数
        if candidate_years < min_years:
            # 经验不足
            gap = min_years - candidate_years
            score = max(0, int(100 - gap * 20))  # 每差1年扣20分
        elif candidate_years > max_years:
            # 经验过多（可能overqualified）
            score = 80
        else:
            # 经验符合要求
            score = 100

        return {
            "score": score,
            "candidate_years": candidate_years,
            "required_min": min_years,
            "required_max": max_years,
            "is_qualified": min_years <= candidate_years <= max_years
        }

    def _calculate_education_match(
        self,
        analysis: ResumeAnalysis,
        job: JobPosition
    ) -> Dict[str, Any]:
        """计算学历匹配度"""
        # 学历等级映射
        education_levels = {
            "博士": 5,
            "硕士": 4,
            "本科": 3,
            "专科": 2,
            "高中": 1,
            "其他": 0
        }

        candidate_level = analysis.education_level or "其他"
        required_level = job.education_required or "不限"

        # 获取学历等级
        candidate_score_level = education_levels.get(candidate_level, 0)
        required_score_level = education_levels.get(required_level, 0)

        # 计算分数
        if required_level == "不限":
            score = 100
        elif candidate_score_level >= required_score_level:
            score = 100
        else:
            # 学历不足
            gap = required_score_level - candidate_score_level
            score = max(0, int(100 - gap * 30))  # 每差一级扣30分

        return {
            "score": score,
            "candidate_education": candidate_level,
            "required_education": required_level,
            "is_qualified": candidate_score_level >= required_score_level
        }

    def _determine_priority(self, match_score: int) -> str:
        """根据匹配度确定优先级"""
        if match_score >= 80:
            return "high"
        elif match_score >= 60:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(
        self,
        skill_match: Dict[str, Any],
        experience_match: Dict[str, Any],
        education_match: Dict[str, Any],
        match_score: int
    ) -> List[str]:
        """生成匹配建议"""
        recommendations = []

        # 技能建议
        if skill_match['score'] < 80:
            missing = skill_match['missing']
            if missing:
                recommendations.append(f"候选人缺少以下关键技能：{', '.join(missing[:3])}")

        # 经验建议
        if not experience_match['is_qualified']:
            if experience_match['candidate_years'] < experience_match['required_min']:
                recommendations.append(
                    f"候选人工作经验不足，需要至少{experience_match['required_min']}年经验"
                )
            else:
                recommendations.append("候选人可能资历过高（overqualified）")

        # 学历建议
        if not education_match['is_qualified']:
            recommendations.append(
                f"候选人学历不符合要求，需要{education_match['required_education']}及以上学历"
            )

        # 综合建议
        if match_score >= 80:
            recommendations.append("强烈推荐面试，候选人与职位高度匹配")
        elif match_score >= 60:
            recommendations.append("建议面试，候选人基本符合要求")
        else:
            recommendations.append("不建议面试，匹配度较低")

        return recommendations

    def save_match_result(
        self,
        resume_id: int,
        job_id: int,
        match_result: Dict[str, Any]
    ) -> ResumeJobMatch:
        """保存匹配结果到数据库"""
        # 检查是否已存在匹配记录
        existing = self.db.query(ResumeJobMatch).filter(
            ResumeJobMatch.resume_id == resume_id,
            ResumeJobMatch.job_id == job_id
        ).first()

        if existing:
            # 更新现有记录
            for key, value in match_result.items():
                setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # 创建新记录
            match = ResumeJobMatch(
                resume_id=resume_id,
                job_id=job_id,
                **match_result
            )
            self.db.add(match)
            self.db.commit()
            self.db.refresh(match)
            return match

    def batch_match(
        self,
        resume_id: int,
        job_ids: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        批量匹配：将一份简历与多个职位进行匹配

        Args:
            resume_id: 简历ID
            job_ids: 职位ID列表，如果为None则匹配所有活跃职位

        Returns:
            匹配结果列表，按匹配度降序排列
        """
        if job_ids is None:
            # 获取所有活跃职位
            jobs = self.db.query(JobPosition).filter(JobPosition.is_active == True).all()
            job_ids = [job.id for job in jobs]

        results = []
        for job_id in job_ids:
            try:
                match_result = self.calculate_match(resume_id, job_id)
                match_result['job_id'] = job_id
                results.append(match_result)
            except Exception as e:
                print(f"匹配失败 (resume_id={resume_id}, job_id={job_id}): {str(e)}")
                continue

        # 按匹配度降序排列
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results

