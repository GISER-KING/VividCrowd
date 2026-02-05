"""
面经PDF解析器 - 从PDF文件中提取面试问题
"""
import json
import re
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from openai import AsyncOpenAI
from loguru import logger


class ExperienceParser:
    """面经PDF解析器"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """初始化解析器"""
        self.client = AsyncOpenAI(
            api_key=api_key or "sk-xxx",
            base_url=base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen-max"

    async def parse_pdf(
        self,
        file_path: str,
        progress_callback: Callable[[int, int, str], None] = None
    ) -> Dict[str, Any]:
        """
        解析PDF面经文件

        Args:
            file_path: PDF文件路径
            progress_callback: 进度回调函数 (current, total, message)

        Returns:
            解析结果，包含标题、公司、职位和问题列表
        """
        # 1. 提取PDF文本（按页）
        pages = self._extract_pdf_pages(file_path)
        if not pages:
            raise ValueError("无法从PDF中提取文本")

        total_chars = sum(len(p) for p in pages)
        logger.info(f"从PDF提取了 {len(pages)} 页，共 {total_chars} 个字符")

        if progress_callback:
            progress_callback(0, len(pages), f"提取了 {len(pages)} 页文本")

        # 2. 分批处理页面，每批处理5页
        all_questions = []
        batch_size = 5
        metadata = {"title": None, "company": None, "position": None, "interview_type": "technical"}
        total_batches = (len(pages) + batch_size - 1) // batch_size

        for batch_idx, i in enumerate(range(0, len(pages), batch_size)):
            batch_pages = pages[i:i + batch_size]
            batch_text = "\n\n".join(batch_pages)
            current_page = min(i + batch_size, len(pages))

            logger.info(f"处理第 {i+1}-{current_page} 页...")

            if progress_callback:
                progress_callback(
                    current_page,
                    len(pages),
                    f"正在解析第 {i+1}-{current_page} 页 ({batch_idx+1}/{total_batches})"
                )

            # 解析这批页面
            result = await self._parse_batch(batch_text, i == 0)

            # 提取元数据（只从第一批）
            if i == 0:
                metadata["title"] = result.get("title")
                metadata["company"] = result.get("company")
                metadata["position"] = result.get("position")
                if result.get("interview_type"):
                    metadata["interview_type"] = result.get("interview_type")

            # 收集问题
            questions = result.get("questions", [])
            all_questions.extend(questions)
            logger.info(f"本批次提取了 {len(questions)} 个问题")

        # 3. 去重（基于问题内容）
        unique_questions = self._deduplicate_questions(all_questions)
        logger.info(f"去重后共 {len(unique_questions)} 个问题")

        if progress_callback:
            progress_callback(len(pages), len(pages), f"解析完成，共 {len(unique_questions)} 个问题")

        return {
            **metadata,
            "questions": unique_questions
        }

    async def parse_pdf_stream(self, file_path: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式解析PDF，用于SSE

        Yields:
            进度信息和最终结果
        """
        # 1. 提取PDF文本（按页）
        pages = self._extract_pdf_pages(file_path)
        if not pages:
            yield {"type": "error", "message": "无法从PDF中提取文本"}
            return

        total_chars = sum(len(p) for p in pages)
        logger.info(f"从PDF提取了 {len(pages)} 页，共 {total_chars} 个字符")

        yield {
            "type": "progress",
            "current": 0,
            "total": len(pages),
            "message": f"提取了 {len(pages)} 页文本，开始解析..."
        }

        # 2. 分批处理页面
        all_questions = []
        batch_size = 5
        metadata = {"title": None, "company": None, "position": None, "interview_type": "technical"}
        total_batches = (len(pages) + batch_size - 1) // batch_size

        for batch_idx, i in enumerate(range(0, len(pages), batch_size)):
            batch_pages = pages[i:i + batch_size]
            batch_text = "\n\n".join(batch_pages)
            current_page = min(i + batch_size, len(pages))

            yield {
                "type": "progress",
                "current": current_page,
                "total": len(pages),
                "message": f"正在解析第 {i+1}-{current_page} 页 ({batch_idx+1}/{total_batches})",
                "questions_found": len(all_questions)
            }

            # 解析这批页面
            result = await self._parse_batch(batch_text, i == 0)

            # 提取元数据
            if i == 0:
                metadata["title"] = result.get("title")
                metadata["company"] = result.get("company")
                metadata["position"] = result.get("position")
                if result.get("interview_type"):
                    metadata["interview_type"] = result.get("interview_type")

            questions = result.get("questions", [])
            all_questions.extend(questions)

        # 3. 去重
        unique_questions = self._deduplicate_questions(all_questions)

        yield {
            "type": "complete",
            "current": len(pages),
            "total": len(pages),
            "message": f"解析完成，共 {len(unique_questions)} 个问题",
            "result": {
                **metadata,
                "questions": unique_questions
            }
        }

    def _extract_pdf_pages(self, file_path: str) -> List[str]:
        """使用PyMuPDF提取PDF文本，按页返回"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF未安装，请运行: pip install pymupdf")
            raise ImportError("请安装PyMuPDF: pip install pymupdf")

        pages = []
        try:
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():
                    pages.append(f"=== 第{page_num + 1}页 ===\n{page_text}")
            doc.close()
        except Exception as e:
            logger.error(f"PDF解析失败: {e}")
            raise

        return pages

    def _deduplicate_questions(self, questions: List[Dict]) -> List[Dict]:
        """去除重复问题"""
        seen = set()
        unique = []
        for q in questions:
            # 使用问题内容的前100个字符作为去重key
            question_text = q.get("question", "")[:100].strip().lower()
            if question_text and question_text not in seen:
                seen.add(question_text)
                unique.append(q)
        return unique

    async def _parse_batch(self, text: str, is_first_batch: bool) -> Dict[str, Any]:
        """解析一批页面的文本"""
        # 限制单批文本长度
        max_length = 8000
        if len(text) > max_length:
            text = text[:max_length] + "\n...(文本已截断)"

        if is_first_batch:
            prompt = f"""请仔细分析以下面经文本，提取其中的**所有**面试问题。

面经文本：
{text}

请以JSON格式返回解析结果：
{{
    "title": "面经标题（如果能识别）",
    "company": "公司名称（如果能识别）",
    "position": "职位名称（如果能识别）",
    "interview_type": "面试类型（technical/hr/behavioral）",
    "questions": [
        {{
            "question": "问题内容",
            "answer": "参考答案（如果有）",
            "category": "问题类别",
            "difficulty": "难度（easy/medium/hard）",
            "tags": ["标签"]
        }}
    ]
}}

**重要提示**：
1. 请仔细识别文本中的每一个面试问题，不要遗漏
2. 面试问题通常以"问："、"Q："、数字编号、或问号结尾的句子形式出现
3. 也要识别隐含的问题，如"面试官问了XXX"、"被问到XXX"等描述
4. 如果问题后面有回答或解析，提取作为参考答案
5. 只返回JSON，不要有其他内容"""
        else:
            prompt = f"""请继续分析以下面经文本，提取其中的**所有**面试问题。

面经文本：
{text}

请以JSON格式返回，只需要返回questions数组：
{{
    "questions": [
        {{
            "question": "问题内容",
            "answer": "参考答案（如果有）",
            "category": "问题类别",
            "difficulty": "难度（easy/medium/hard）",
            "tags": ["标签"]
        }}
    ]
}}

**重要提示**：
1. 请仔细识别文本中的每一个面试问题，不要遗漏
2. 面试问题通常以"问："、"Q："、数字编号、或问号结尾的句子形式出现
3. 也要识别隐含的问题，如"面试官问了XXX"、"被问到XXX"等描述
4. 只返回JSON，不要有其他内容"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的面试题解析助手，擅长从面经文本中提取结构化的面试问题。请尽可能多地识别出所有面试问题，不要遗漏。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            result_text = response.choices[0].message.content.strip()

            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)

            if "questions" not in result:
                result["questions"] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return {"questions": []}
        except Exception as e:
            logger.error(f"LLM解析失败: {e}")
            return {"questions": []}

    async def parse_text(self, text: str) -> Dict[str, Any]:
        """直接解析文本内容"""
        return await self._parse_batch(text, True)
