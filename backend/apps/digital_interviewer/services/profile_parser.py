"""
面试官画像解析服务
解析PDF/Markdown格式的面试官画像文件，提取关键信息
"""
import re
import json
from typing import Dict, Any, Optional
from pathlib import Path
import PyPDF2
import markdown


class InterviewerProfileParser:
    """面试官画像解析器"""

    def __init__(self):
        self.required_fields = ["name", "expertise_areas"]

    async def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析面试官画像文件

        Args:
            file_path: 文件路径

        Returns:
            解析后的结构化数据
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 根据文件类型选择解析方法
        if file_path_obj.suffix.lower() == '.pdf':
            raw_content = await self._parse_pdf(file_path)
        elif file_path_obj.suffix.lower() in ['.md', '.markdown']:
            raw_content = await self._parse_markdown(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path_obj.suffix}")

        # 提取结构化信息
        profile_data = await self._extract_profile_data(raw_content)
        profile_data['raw_content'] = raw_content
        profile_data['source_file_path'] = file_path

        # 验证必填字段
        self._validate_profile(profile_data)

        return profile_data

    async def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    async def _parse_markdown(self, file_path: str) -> str:
        """解析Markdown文件"""
        from loguru import logger
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        logger.info(f"📄 Markdown文件内容长度: {len(content)} 字符")
        logger.debug(f"📄 文件前200字符: {content[:200]}")
        return content

    async def _extract_profile_data(self, raw_content: str) -> Dict[str, Any]:
        """从原始文本中提取结构化信息"""
        from loguru import logger
        profile_data = {}

        logger.info("🔍 开始提取结构化信息...")

        # 提取姓名 - 支持 **姓名**: xxx 格式
        name_pattern = r'\*{0,2}(?:姓名|名字|Name)\*{0,2}[：:]\s*([^\n]+)'
        name_match = re.search(name_pattern, raw_content, re.IGNORECASE)
        if name_match:
            profile_data['name'] = name_match.group(1).strip()
            logger.info(f"✅ 提取到姓名: {profile_data['name']}")
        else:
            logger.warning(f"⚠️ 未找到姓名字段，使用的正则: {name_pattern}")

        # 提取职位
        title_pattern = r'\*{0,2}(?:职位|Title)\*{0,2}[：:]\s*([^\n]+)'
        title_match = re.search(title_pattern, raw_content, re.IGNORECASE)
        if title_match:
            profile_data['title'] = title_match.group(1).strip()
            logger.info(f"✅ 提取到职位: {profile_data['title']}")
        else:
            logger.warning(f"⚠️ 未找到职位字段")

        # 提取公司
        company_pattern = r'\*{0,2}(?:公司|Company)\*{0,2}[：:]\s*([^\n]+)'
        company_match = re.search(company_pattern, raw_content, re.IGNORECASE)
        if company_match:
            profile_data['company'] = company_match.group(1).strip()
            logger.info(f"✅ 提取到公司: {profile_data['company']}")
        else:
            logger.warning(f"⚠️ 未找到公司字段")

        # 提取专业领域
        expertise_pattern = r'\*{0,2}(?:专业领域|专长|Expertise)\*{0,2}[：:]\s*([^\n]+)'
        expertise_match = re.search(expertise_pattern, raw_content, re.IGNORECASE)
        if expertise_match:
            profile_data['expertise_areas'] = expertise_match.group(1).strip()
            logger.info(f"✅ 提取到专业领域: {profile_data['expertise_areas'][:50]}...")
        else:
            logger.warning(f"⚠️ 未找到专业领域字段，使用的正则: {expertise_pattern}")
            # 打印文件中包含"专业"的行，帮助调试
            lines_with_expertise = [line for line in raw_content.split('\n') if '专业' in line or 'Expertise' in line.lower()]
            logger.debug(f"📋 文件中包含'专业'的行: {lines_with_expertise}")

        logger.info(f"📊 提取完成，共提取到 {len(profile_data)} 个字段")
        return profile_data

    def _validate_profile(self, profile_data: Dict[str, Any]) -> None:
        """验证画像数据的完整性"""
        missing_fields = [field for field in self.required_fields if not profile_data.get(field)]
        if missing_fields:
            raise ValueError(f"缺少必填字段: {', '.join(missing_fields)}")

    async def generate_system_prompt(self, profile_data: Dict[str, Any]) -> str:
        """根据画像数据生成系统提示词"""
        name = profile_data.get('name', '面试官')
        title = profile_data.get('title', '')
        company = profile_data.get('company', '')
        expertise = profile_data.get('expertise_areas', '')

        prompt = f"""你是{name}"""
        if title:
            prompt += f"，担任{title}"
        if company:
            prompt += f"，就职于{company}"

        prompt += f"""。

你的专业领域：{expertise}

作为面试官，你需要：
1. 根据候选人的回答提出有针对性的问题
2. 评估候选人的专业能力、沟通表达和问题解决能力
3. 保持专业、客观、友好的态度
4. 适时追问以深入了解候选人的能力

请始终保持你的角色设定，用专业的方式进行面试。"""

        return prompt
