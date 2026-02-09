"""
面试官Agent - 负责提问、分析回答、决策下一步
"""
import json
import random
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI


class InterviewerAgent:
    """面试官AI Agent"""

    def __init__(
        self,
        profile_data: Dict[str, Any],
        interview_type: str = "technical",
        reference_questions: List[Dict] = None,
        experience_mode: str = "none",  # none/reference/strict/mixed
        resume_data: Dict[str, Any] = None,  # 新增：简历数据
        api_key: str = None,
        base_url: str = None
    ):
        """
        初始化面试官Agent

        Args:
            profile_data: 面试官画像数据
            interview_type: 面试类型 (technical/hr/behavioral)
            reference_questions: 参考问题列表（来自面经）
            experience_mode: 面经使用模式
            resume_data: 候选人简历数据
            api_key: API密钥
            base_url: API基础URL
        """
        self.profile_data = profile_data
        self.interview_type = interview_type
        self.system_prompt = profile_data.get('system_prompt', '')

        # 面经相关
        self.reference_questions = reference_questions or []
        self.experience_mode = experience_mode
        self.used_question_indices = []  # 已使用的问题索引

        # 简历相关
        self.resume_data = resume_data or {}

        # 难度调整相关
        self.current_difficulty = "medium"  # 初始难度：easy/medium/hard
        self.performance_history = []  # 记录表现历史

        # 初始化OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=api_key or "sk-xxx",
            base_url=base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen-max"

        # 对话历史
        self.conversation_history: List[Dict[str, str]] = []

    async def generate_question(
        self,
        round_number: int,
        previous_answer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成面试问题

        Args:
            round_number: 当前轮次
            previous_answer: 上一轮的回答
            context: 额外上下文（如RAG检索结果）

        Returns:
            包含问题和元数据的字典
        """
        # 构建提示词
        prompt = self._build_question_prompt(round_number, previous_answer, context)

        # 调用LLM生成问题
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history[-5:],  # 保留最近5轮对话
            {"role": "user", "content": prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )

        question = response.choices[0].message.content.strip()

        # 记录到对话历史
        self.conversation_history.append({"role": "assistant", "content": question})

        return {
            "question": question,
            "round_number": round_number,
            "question_type": self._infer_question_type(question),
            "is_followup": previous_answer is not None
        }

    async def analyze_answer(self, answer: str) -> Dict[str, Any]:
        """
        分析候选人的回答

        Args:
            answer: 候选人的回答

        Returns:
            分析结果
        """
        # 记录到对话历史
        self.conversation_history.append({"role": "user", "content": answer})

        # 构建分析提示词
        prompt = f"""请分析候选人的回答质量，从以下维度评估：
1. 专业能力（1-10分）
2. 沟通表达（1-10分）
3. 逻辑思维（1-10分）

候选人回答：{answer}

请以JSON格式返回评估结果，包含：
- technical_score: 专业能力分数
- communication_score: 沟通表达分数
- logic_score: 逻辑思维分数
- quality: 整体质量（excellent/good/fair/poor）
- should_followup: 是否需要追问（true/false）
- followup_reason: 追问原因（如果需要追问）
"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3
        )

        result_text = response.choices[0].message.content.strip()

        try:
            result = json.loads(result_text)
        except:
            result = {
                "technical_score": 5,
                "communication_score": 5,
                "logic_score": 5,
                "quality": "fair",
                "should_followup": False
            }

        return result

    def _build_question_prompt(
        self,
        round_number: int,
        previous_answer: Optional[str],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """构建问题生成提示词，根据面经模式决定策略"""
        # 根据模式决定问题生成策略
        if self.experience_mode == "none" or not self.reference_questions:
            # 完全动态生成
            return self._build_dynamic_prompt(round_number, previous_answer, context)

        elif self.experience_mode == "strict":
            # 严格模式：直接使用面经原题
            return self._build_strict_prompt(round_number)

        elif self.experience_mode == "mixed":
            # 混合模式：第一轮用原题，后续灵活追问
            if round_number == 1 or not previous_answer:
                return self._build_strict_prompt(round_number)
            else:
                return self._build_followup_prompt(round_number, previous_answer)

        else:  # reference
            # 参考模式：AI可改编
            return self._build_reference_prompt(round_number, previous_answer, context)

    def _build_dynamic_prompt(
        self,
        round_number: int,
        previous_answer: Optional[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建动态问题生成提示词（原有逻辑）"""
        # 构建简历上下文
        resume_context = ""
        if self.resume_data:
            resume_context = self._format_resume_context()

        # 构建难度提示
        difficulty_hint = f"\n\n当前问题难度级别：{self.current_difficulty}。请根据此难度级别提出相应的问题。"

        if round_number == 1:
            prompt = f"这是面试的第一个问题，请提出一个{self.interview_type}类型的开场问题。"
            if resume_context:
                prompt += f"\n\n{resume_context}"
            prompt += difficulty_hint
        elif previous_answer:
            prompt = f"候选人刚才的回答是：{previous_answer}\n\n请根据回答决定是追问还是进入下一个问题。"
            if resume_context:
                prompt += f"\n\n{resume_context}"
            prompt += difficulty_hint
        else:
            prompt = f"请提出第{round_number}个面试问题。"
            if resume_context:
                prompt += f"\n\n{resume_context}"
            prompt += difficulty_hint

        if context and context.get('suggested_questions'):
            prompt += f"\n\n参考问题：{context['suggested_questions']}"

        return prompt

    def _build_strict_prompt(self, round_number: int) -> str:
        """严格模式：直接返回面经原题"""
        unused = [i for i in range(len(self.reference_questions))
                  if i not in self.used_question_indices]

        if unused:
            idx = random.choice(unused)
            self.used_question_indices.append(idx)
            question = self.reference_questions[idx].get('question', '')
            return f"请直接使用以下问题提问（保持原意，可以稍微调整措辞使其更自然）：\n\n{question}"

        # 如果面经问题用完了，回退到动态生成
        return self._build_dynamic_prompt(round_number, None, None)

    def _build_followup_prompt(self, round_number: int, previous_answer: str) -> str:
        """混合模式的追问提示词"""
        prompt = f"""候选人刚才的回答是：{previous_answer}

请根据候选人的回答进行追问，深入了解其能力。追问可以：
1. 针对回答中的技术细节深入询问
2. 要求候选人举例说明
3. 探讨边界情况或异常处理
4. 了解候选人的思考过程"""

        return prompt

    def _build_reference_prompt(
        self,
        round_number: int,
        previous_answer: Optional[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """参考模式：AI可改编面经问题"""
        # 获取未使用的问题作为参考
        unused = [self.reference_questions[i] for i in range(len(self.reference_questions))
                  if i not in self.used_question_indices]

        prompt = self._build_dynamic_prompt(round_number, previous_answer, context)

        if unused:
            # 随机选择几个问题作为参考
            samples = random.sample(unused, min(3, len(unused)))
            prompt += "\n\n可参考以下面经问题（可以直接使用、改编或受其启发）：\n"
            for i, q in enumerate(samples, 1):
                prompt += f"{i}. {q.get('question', '')}\n"

            # 标记第一个参考问题为已使用（避免重复推荐）
            if samples:
                first_idx = self.reference_questions.index(samples[0])
                if first_idx not in self.used_question_indices:
                    self.used_question_indices.append(first_idx)

        return prompt

    def _infer_question_type(self, question: str) -> str:
        """推断问题类型"""
        if any(keyword in question for keyword in ['如何', '怎么', '实现', '设计']):
            return 'technical'
        elif any(keyword in question for keyword in ['为什么', '经历', '情况']):
            return 'behavioral'
        else:
            return 'general'

    def _format_resume_context(self) -> str:
        """格式化简历上下文信息"""
        if not self.resume_data:
            return ""

        context_parts = ["候选人简历信息："]

        # 工作经验
        if self.resume_data.get('work_experience'):
            context_parts.append("\n工作经历：")
            for exp in self.resume_data['work_experience'][:3]:  # 只取前3条
                company = exp.get('company', '未知公司')
                position = exp.get('position', '未知职位')
                context_parts.append(f"- {company} - {position}")

        # 技能
        if self.resume_data.get('skills'):
            skills = self.resume_data['skills'][:10]  # 只取前10个技能
            context_parts.append(f"\n技能：{', '.join(skills)}")

        # 项目经验
        if self.resume_data.get('projects'):
            context_parts.append("\n项目经历：")
            for proj in self.resume_data['projects'][:2]:  # 只取前2个项目
                name = proj.get('name', '未知项目')
                context_parts.append(f"- {name}")

        context_parts.append("\n\n请根据候选人的简历信息，提出针对性的面试问题。")

        return "\n".join(context_parts)

    def adjust_difficulty(self, answer_quality: str) -> None:
        """
        根据回答质量调整问题难度

        Args:
            answer_quality: 回答质量 (excellent/good/fair/poor)
        """
        self.performance_history.append(answer_quality)

        # 只保留最近3次表现
        if len(self.performance_history) > 3:
            self.performance_history = self.performance_history[-3:]

        # 根据最近表现调整难度
        if len(self.performance_history) >= 2:
            recent = self.performance_history[-2:]

            # 连续表现优秀，提高难度
            if all(q in ['excellent', 'good'] for q in recent):
                if self.current_difficulty == "easy":
                    self.current_difficulty = "medium"
                elif self.current_difficulty == "medium":
                    self.current_difficulty = "hard"

            # 连续表现不佳，降低难度
            elif all(q in ['poor', 'fair'] for q in recent):
                if self.current_difficulty == "hard":
                    self.current_difficulty = "medium"
                elif self.current_difficulty == "medium":
                    self.current_difficulty = "easy"

    def get_current_difficulty(self) -> str:
        """获取当前难度级别"""
        return self.current_difficulty
