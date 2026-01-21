import os
import json
import fitz  # PyMuPDF
from typing import Optional, Dict, Any
from dashscope import Generation
from loguru import logger
from backend.app.core.config import settings

class PDFParserService:
    """PDF 解析服务 - 提取文本并用 LLM 结构化解析"""

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
    async def parse_celebrity_info(raw_text: str, source_type: str = "person") -> Dict[str, Any]:
        """使用 LLM 解析 PDF 文本，提取结构化信息"""

        if source_type == "person":
            parse_prompt = """你是一个信息提取专家。请从以下文本中提取人物信息，并以 JSON 格式返回。

要求提取的字段：
- name: 人物姓名（必填）
- birth_year: 出生年份（整数，可选）
- death_year: 去世年份（整数，可选，在世则留空）
- nationality: 国籍
- occupation: 职业/身份
- biography: 个人简介（100-200字）
- famous_works: 代表作品或主要成就（列举，换行分隔）
- famous_quotes: 著名语录或金句（列举，换行分隔）
- personality_traits: 性格特点（用逗号分隔的关键词）
- speech_style: 说话风格描述（例如：直接、幽默、学术性强等）

只返回 JSON，不要有其他文字。"""

        elif source_type == "book":
            parse_prompt = """你是一个信息提取专家。请从以下书籍内容中提取信息，并以 JSON 格式返回。

要求提取的字段：
- name: 书名（必填）
- author: 作者
- biography: 书籍简介（100-200字）
- famous_quotes: 书中金句或核心观点（列举，换行分隔）
- personality_traits: 作者的思维特点（用逗号分隔）
- speech_style: 书中的表达风格

只返回 JSON，不要有其他文字。"""

        else:  # topic
            parse_prompt = """你是一个信息提取专家。请从以下课程/专题内容中提取信息，并以 JSON 格式返回。

要求提取的字段：
- name: 课程/专题名称（必填）
- author: 讲师/作者
- occupation: 讲师身份
- biography: 课程简介（100-200字）
- famous_quotes: 核心观点或金句（列举，换行分隔）
- personality_traits: 内容特点（用逗号分隔）
- speech_style: 表达风格

只返回 JSON，不要有其他文字。"""

        # 限制文本长度，避免超过上下文限制
        max_text_len = 15000
        truncated_text = raw_text[:max_text_len] if len(raw_text) > max_text_len else raw_text

        full_prompt = f"{parse_prompt}\n\n原始文本：\n{truncated_text}"

        try:
            response = Generation.call(
                model=settings.MODEL_NAME,
                prompt=full_prompt,
                api_key=settings.DASHSCOPE_API_KEY,
                temperature=0.3,
                max_tokens=2000,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试从返回中提取 JSON
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                parsed = json.loads(content.strip())
                return parsed
            else:
                logger.error(f"LLM parse error: {response.code} - {response.message}")
                raise ValueError(f"LLM 解析失败: {response.message}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            raise ValueError("LLM 返回的内容无法解析为 JSON")
        except Exception as e:
            logger.error(f"Parse celebrity info error: {e}")
            raise

    @staticmethod
    def generate_system_prompt(info: Dict[str, Any], source_type: str = "person") -> str:
        """根据提取的信息生成 System Prompt"""

        name = info.get("name", "未知")
        occupation = info.get("occupation", "")
        biography = info.get("biography", "")
        speech_style = info.get("speech_style", "")
        personality_traits = info.get("personality_traits", "")
        famous_quotes = info.get("famous_quotes", "")

        if source_type == "person":
            prompt = f"""你是 {name}，{occupation}。

【背景】
{biography}

【性格特点】
{personality_traits}

【说话风格】
{speech_style}

【经典语录参考】
{famous_quotes}

【核心指令】
1. 完全以 {name} 的身份进行对话，使用第一人称。
2. 保持 {name} 的说话风格和思维方式。
3. 回答应基于 {name} 的已知知识和经历，如果被问到不了解的话题，请坦诚说明。
4. 在回答末尾标注信息来源，格式：[来源: {name}语录/著作/课程]
5. 说话要自然、口语化，避免机械感。"""

        elif source_type == "book":
            author = info.get("author", "未知作者")
            prompt = f"""你是《{name}》这本书的化身，能够以作者 {author} 的视角回答问题。

【书籍简介】
{biography}

【核心观点】
{famous_quotes}

【表达风格】
{speech_style}

【核心指令】
1. 以《{name}》书中的知识和观点回答问题。
2. 使用书中的思维框架和表达方式。
3. 如果问题超出书本内容范围，请明确说明。
4. 在回答末尾标注：[来源: 《{name}》]"""

        else:  # topic
            author = info.get("author", "讲师")
            prompt = f"""你是"{name}"课程的 AI 助教，熟悉课程的全部内容。

【课程简介】
{biography}

【核心观点】
{famous_quotes}

【讲师风格】
{speech_style}

【核心指令】
1. 以课程内容为基础回答问题。
2. 使用 {author} 的思维方式和表达风格。
3. 如果问题超出课程范围，请说明。
4. 在回答末尾标注：[来源: {name}课程]"""

        return prompt


pdf_parser_service = PDFParserService()
