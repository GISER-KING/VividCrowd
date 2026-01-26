import json
import fitz  # PyMuPDF
from typing import Dict, Any
from dashscope import Generation
from loguru import logger
from backend.core.config import settings

class ProfileParserService:
    """客户画像解析服务 - 提取文本并用 LLM 结构化解析（支持PDF和Markdown）"""

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """从 PDF 提取文本"""
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise ValueError(f"无法读取 PDF 文件: {e}")

    @staticmethod
    def extract_text_from_markdown(md_path: str) -> str:
        """从 Markdown 文件提取文本"""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Markdown extraction error: {e}")
            raise ValueError(f"无法读取 Markdown 文件: {e}")

    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """根据文件类型自动选择提取方法"""
        if file_path.lower().endswith('.pdf'):
            return ProfileParserService.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.md'):
            return ProfileParserService.extract_text_from_markdown(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_path}")

    @staticmethod
    async def parse_customer_profile(raw_text: str) -> Dict[str, Any]:
        """使用 LLM 解析文本，提取客户画像结构化信息"""

        parse_prompt = """你是一个客户画像分析专家。请从以下文本中提取客户画像信息，并以 JSON 格式返回。

要求提取的字段：
- name: 客户画像名称（必填，例如：企业决策者、年轻创业者等）
- age_range: 年龄段（例如：25-35岁）
- gender: 性别
- occupation: 职业
- industry: 所属行业
- personality_traits: 性格特征（用逗号分隔的关键词，例如：理性、谨慎、追求效率）
- communication_style: 沟通风格描述（例如：直接、注重数据、喜欢案例）
- pain_points: 痛点（客户面临的问题和挑战，换行分隔）
- needs: 需求（客户的核心需求，换行分隔）
- objections: 常见异议（客户可能提出的反对意见，换行分隔）

只返回 JSON，不要有其他文字。"""

        # 限制文本长度，避免超过上下文限制
        max_text_len = 15000
        truncated_text = raw_text[:max_text_len] if len(raw_text) > max_text_len else raw_text

        full_prompt = f"{parse_prompt}\n\n原始文本：\n{truncated_text}"

        try:
            response = Generation.call(
                model=settings.MODEL_NAME,
                prompt=full_prompt,
                api_key=settings.DASHSCOPE_API_KEY
            )

            if response.status_code == 200:
                result_text = response.output.text.strip()
                # 尝试提取 JSON（可能被 markdown 代码块包裹）
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                parsed_info = json.loads(result_text)
                logger.info(f"Successfully parsed customer profile: {parsed_info.get('name', 'Unknown')}")
                return parsed_info
            else:
                logger.error(f"LLM API error: {response.message}")
                raise ValueError(f"LLM 解析失败: {response.message}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"LLM 返回的 JSON 格式错误: {e}")
        except Exception as e:
            logger.error(f"Customer profile parsing error: {e}")
            raise ValueError(f"客户画像解析失败: {e}")

    @staticmethod
    def generate_system_prompt(parsed_info: Dict[str, Any]) -> str:
        """根据解析的客户信息生成 System Prompt"""

        name = parsed_info.get("name", "客户")
        age_range = parsed_info.get("age_range", "")
        gender = parsed_info.get("gender", "")
        occupation = parsed_info.get("occupation", "")
        industry = parsed_info.get("industry", "")
        personality_traits = parsed_info.get("personality_traits", "")
        communication_style = parsed_info.get("communication_style", "")
        pain_points = parsed_info.get("pain_points", "")
        needs = parsed_info.get("needs", "")
        objections = parsed_info.get("objections", "")

        system_prompt = f"""你现在要扮演一个名为"{name}"的客户角色，用于销售人员的能力培训。

# 客户基本信息
- 年龄段：{age_range}
- 性别：{gender}
- 职业：{occupation}
- 行业：{industry}

# 性格特征
{personality_traits}

# 沟通风格
{communication_style}

# 痛点
{pain_points}

# 需求
{needs}

# 常见异议
{objections}

# 角色扮演要求
1. 完全沉浸在这个客户角色中，用第一人称回应
2. 根据客户的性格特征和沟通风格来表达
3. 在对话中自然地表现出痛点和需求
4. 当销售人员的方案不够吸引人时，提出相应的异议
5. 保持真实客户的反应，不要过于配合
6. 根据销售人员的表现给出真实的反馈

请始终保持这个角色，不要跳出角色。"""

        return system_prompt


# 创建全局实例
profile_parser_service = ProfileParserService()
