"""
简历解析服务 - 支持PDF、Word、图片格式的简历解析
"""
import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document
from PIL import Image
import io

from backend.core.llm_client import get_llm_client


class ResumeParser:
    """简历解析器 - 支持多种格式的简历解析"""

    def __init__(self):
        self.llm_client = get_llm_client()
        self.supported_formats = {
            'pdf': self._parse_pdf,
            'docx': self._parse_word,
            'doc': self._parse_word,
            'jpg': self._parse_image,
            'jpeg': self._parse_image,
            'png': self._parse_image,
        }

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件

        Args:
            file_path: 简历文件路径

        Returns:
            解析结果字典，包含：
            - success: 是否成功
            - raw_text: 原始文本
            - structured_data: 结构化数据
            - error: 错误信息（如果失败）
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"文件不存在: {file_path}"
                }

            # 获取文件扩展名
            file_ext = Path(file_path).suffix.lower().lstrip('.')

            if file_ext not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"不支持的文件格式: {file_ext}"
                }

            # 解析文件获取原始文本
            raw_text = self.supported_formats[file_ext](file_path)

            if not raw_text or len(raw_text.strip()) < 50:
                return {
                    "success": False,
                    "error": "简历内容过少或解析失败"
                }

            # 使用LLM提取结构化信息
            structured_data = self._extract_structured_info(raw_text)

            # 计算文件哈希
            file_hash = self._calculate_file_hash(file_path)

            return {
                "success": True,
                "raw_text": raw_text,
                "structured_data": structured_data,
                "file_hash": file_hash
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"解析失败: {str(e)}"
            }

    def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF解析失败: {str(e)}")

    def _parse_word(self, file_path: str) -> str:
        """解析Word文件"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Word文档解析失败: {str(e)}")

    def _parse_image(self, file_path: str) -> str:
        """解析图片文件（使用OCR）"""
        try:
            # 注意：这里需要集成OCR服务（如PaddleOCR或云服务）
            # 暂时返回提示信息
            return "图片OCR功能待实现，请使用PDF或Word格式"
        except Exception as e:
            raise Exception(f"图片解析失败: {str(e)}")

    def _extract_structured_info(self, raw_text: str) -> Dict[str, Any]:
        """使用LLM提取结构化信息"""

        prompt = f"""请从以下简历文本中提取结构化信息，以JSON格式返回。

简历文本：
{raw_text}

请提取以下信息（如果没有相关信息，对应字段返回null）：
1. 基本信息：姓名、电话、邮箱、地址
2. 教育背景：学校、专业、学历、入学时间、毕业时间
3. 工作经历：公司、职位、开始时间、结束时间、工作内容
4. 项目经历：项目名称、角色、时间、项目描述、技术栈
5. 技能：技能列表
6. 证书：证书名称、获得时间

返回格式示例：
{{
    "name": "张三",
    "contact": {{
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "address": "北京市朝阳区"
    }},
    "education": [
        {{
            "school": "清华大学",
            "major": "计算机科学与技术",
            "degree": "本科",
            "start_date": "2015-09",
            "end_date": "2019-06"
        }}
    ],
    "work_experience": [
        {{
            "company": "某科技公司",
            "position": "软件工程师",
            "start_date": "2019-07",
            "end_date": "2022-12",
            "description": "负责后端开发..."
        }}
    ],
    "projects": [
        {{
            "name": "电商平台",
            "role": "后端负责人",
            "start_date": "2020-01",
            "end_date": "2020-12",
            "description": "项目描述...",
            "tech_stack": ["Python", "Django", "MySQL"]
        }}
    ],
    "skills": ["Python", "Java", "MySQL", "Redis"],
    "certifications": [
        {{
            "name": "PMP项目管理认证",
            "date": "2021-06"
        }}
    ]
}}

请只返回JSON，不要包含其他说明文字。"""

        try:
            response = self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )

            # 提取JSON内容
            content = response.strip()

            # 尝试解析JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            structured_data = json.loads(content.strip())
            return structured_data

        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}")
            return {}
        except Exception as e:
            print(f"LLM提取失败: {str(e)}")
            return {}

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def evaluate_quality(self, structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """
        评估简历质量

        Returns:
            包含质量评分和问题的字典
        """
        quality_score = 0
        completeness_score = 0
        professionalism_score = 0
        issues = []
        suggestions = []
        risk_flags = []

        # 1. 完整性评分（40分）
        required_fields = {
            'name': 5,
            'contact': 10,
            'education': 10,
            'work_experience': 10,
            'skills': 5
        }

        for field, score in required_fields.items():
            if field in structured_data and structured_data[field]:
                if isinstance(structured_data[field], list) and len(structured_data[field]) > 0:
                    completeness_score += score
                elif isinstance(structured_data[field], dict) and structured_data[field]:
                    completeness_score += score
                elif isinstance(structured_data[field], str) and structured_data[field].strip():
                    completeness_score += score
            else:
                issues.append(f"缺少{field}信息")

        # 2. 专业性评分（30分）
        # 检查文本长度
        if len(raw_text) > 500:
            professionalism_score += 10
        else:
            issues.append("简历内容过于简短")

        # 检查是否有项目经历
        if 'projects' in structured_data and structured_data['projects']:
            professionalism_score += 10
        else:
            suggestions.append("建议添加项目经历")

        # 检查是否有技能描述
        if 'skills' in structured_data and len(structured_data.get('skills', [])) >= 3:
            professionalism_score += 10
        else:
            suggestions.append("建议补充更多技能信息")

        # 3. 一致性检查（30分）
        consistency_score = 30

        # 检查工作经历时间线
        if 'work_experience' in structured_data and structured_data['work_experience']:
            work_exp = structured_data['work_experience']
            if len(work_exp) > 5:
                risk_flags.append("频繁跳槽（超过5份工作）")
                consistency_score -= 10

            # 检查时间断层（简化版）
            # TODO: 实现更复杂的时间线检查

        quality_score = completeness_score + professionalism_score + consistency_score

        return {
            "quality_score": min(quality_score, 100),
            "completeness_score": completeness_score,
            "professionalism_score": professionalism_score,
            "issues": issues,
            "suggestions": suggestions,
            "risk_flags": risk_flags
        }

    def extract_tags(self, structured_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        从结构化数据中提取标签

        Returns:
            包含技能标签、行业标签、职位标签的字典
        """
        skill_tags = []
        industry_tags = []
        position_tags = []

        # 提取技能标签
        if 'skills' in structured_data:
            skill_tags = structured_data['skills'] if isinstance(structured_data['skills'], list) else []

        # 从工作经历提取行业和职位标签
        if 'work_experience' in structured_data:
            for exp in structured_data['work_experience']:
                if 'position' in exp and exp['position']:
                    position_tags.append(exp['position'])
                # 可以根据公司名称推断行业（需要行业数据库）

        # 去重
        skill_tags = list(set(skill_tags))
        industry_tags = list(set(industry_tags))
        position_tags = list(set(position_tags))

        return {
            "skill_tags": skill_tags,
            "industry_tags": industry_tags,
            "position_tags": position_tags
        }

    def calculate_work_years(self, structured_data: Dict[str, Any]) -> float:
        """
        计算总工作年限

        Returns:
            工作年限（年）
        """
        # 简化版本：统计工作经历的数量
        # TODO: 实现基于时间的精确计算
        if 'work_experience' in structured_data:
            return len(structured_data['work_experience']) * 1.5  # 假设每份工作平均1.5年
        return 0.0

    def detect_risks(self, structured_data: Dict[str, Any], raw_text: str) -> List[str]:
        """
        检测简历中的风险点

        Returns:
            风险标记列表
        """
        risks = []

        # 1. 检测夸大词汇
        exaggeration_words = [
            '精通', '精通掌握', '深度掌握', '完全掌握', '极其熟练',
            '全面负责', '独立完成', '主导', '核心', '唯一'
        ]

        for word in exaggeration_words:
            if word in raw_text:
                risks.append(f"检测到夸大词汇: {word}")

        # 2. 检测工作经历频繁跳槽
        if 'work_experience' in structured_data:
            work_exp = structured_data['work_experience']
            if len(work_exp) > 5:
                risks.append("频繁跳槽（超过5份工作）")

        # 3. 检测技能过多
        if 'skills' in structured_data:
            skills = structured_data['skills']
            if isinstance(skills, list) and len(skills) > 20:
                risks.append("技能列表过多（超过20项），可能存在堆砌")

        return risks
