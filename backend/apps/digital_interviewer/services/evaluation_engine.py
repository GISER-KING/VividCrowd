"""
面试评估引擎 - 多维度评估候选人表现
"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI


class InterviewEvaluationEngine:
    """面试评估引擎"""

    def __init__(self, api_key: str = None, base_url: str = None):
        """初始化评估引擎"""
        self.client = AsyncOpenAI(
            api_key=api_key or "sk-xxx",
            base_url=base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen-max"

        # 评估维度定义
        self.evaluation_dimensions = {
            "technical": "专业能力",
            "communication": "沟通表达",
            "problem_solving": "问题解决",
            "cultural_fit": "文化契合"
        }

    async def evaluate_answer(
        self,
        question: str,
        answer: str,
        interview_type: str = "technical"
    ) -> Dict[str, Any]:
        """
        评估单个回答

        Args:
            question: 面试问题
            answer: 候选人回答
            interview_type: 面试类型

        Returns:
            评估结果
        """
        prompt = self._build_evaluation_prompt(question, answer, interview_type)

        messages = [
            {"role": "system", "content": "你是一位专业的面试评估专家。"},
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
            result = self._get_default_evaluation()

        return result

    def _build_evaluation_prompt(
        self,
        question: str,
        answer: str,
        interview_type: str
    ) -> str:
        """构建评估提示词"""
        prompt = f"""请评估以下面试回答的质量。

面试类型：{interview_type}
面试问题：{question}
候选人回答：{answer}

请从以下维度评分（1-10分）：
1. 专业能力（technical_score）
2. 沟通表达（communication_score）
3. 问题解决（problem_solving_score）
4. 文化契合（cultural_fit_score）

同时评估：
- 整体质量（quality）：excellent/good/fair/poor
- 是否需要追问（should_followup）：true/false
- 追问原因（followup_reason）：如果需要追问，说明原因

请以JSON格式返回结果。"""

        return prompt

    def _get_default_evaluation(self) -> Dict[str, Any]:
        """获取默认评估结果"""
        return {
            "technical_score": 5,
            "communication_score": 5,
            "problem_solving_score": 5,
            "cultural_fit_score": 5,
            "quality": "fair",
            "should_followup": False,
            "followup_reason": ""
        }

    async def generate_final_evaluation(
        self,
        rounds: List[Dict[str, Any]],
        interview_type: str
    ) -> Dict[str, Any]:
        """
        生成最终综合评估

        Args:
            rounds: 所有轮次的数据
            interview_type: 面试类型

        Returns:
            最终评估结果
        """
        # 计算平均分
        total_technical = 0
        total_communication = 0
        total_problem_solving = 0
        total_cultural_fit = 0
        count = 0

        for round_data in rounds:
            eval_data = round_data.get('evaluation_data', {})
            if eval_data:
                total_technical += eval_data.get('technical_score', 0)
                total_communication += eval_data.get('communication_score', 0)
                total_problem_solving += eval_data.get('problem_solving_score', 0)
                total_cultural_fit += eval_data.get('cultural_fit_score', 0)
                count += 1

        if count == 0:
            return self._get_default_final_evaluation()

        avg_technical = round(total_technical / count)
        avg_communication = round(total_communication / count)
        avg_problem_solving = round(total_problem_solving / count)
        avg_cultural_fit = round(total_cultural_fit / count)

        total_score = avg_technical + avg_communication + avg_problem_solving + avg_cultural_fit

        # 确定表现等级
        if total_score >= 35:
            performance_level = "优秀"
        elif total_score >= 28:
            performance_level = "良好"
        elif total_score >= 20:
            performance_level = "合格"
        else:
            performance_level = "待提升"

        return {
            "technical_score": avg_technical,
            "communication_score": avg_communication,
            "problem_solving_score": avg_problem_solving,
            "cultural_fit_score": avg_cultural_fit,
            "total_score": total_score,
            "performance_level": performance_level,
            "strengths": await self._generate_strengths(rounds, avg_technical, avg_communication, avg_problem_solving, avg_cultural_fit),
            "weaknesses": await self._generate_weaknesses(rounds, avg_technical, avg_communication, avg_problem_solving, avg_cultural_fit),
            "suggestions": await self._generate_suggestions(rounds, interview_type, performance_level)
        }

    async def _generate_strengths(
        self,
        rounds: List[Dict[str, Any]],
        avg_technical: float,
        avg_communication: float,
        avg_problem_solving: float,
        avg_cultural_fit: float
    ) -> List[str]:
        """使用LLM生成优势分析"""
        rounds_summary = "\n\n".join([
            f"第{i+1}轮:\n问题: {r['question']}\n回答: {r['answer']}\n评分: 技术{r.get('evaluation_data', {}).get('technical_score', 0)}/10, "
            f"沟通{r.get('evaluation_data', {}).get('communication_score', 0)}/10, "
            f"问题解决{r.get('evaluation_data', {}).get('problem_solving_score', 0)}/10"
            for i, r in enumerate(rounds)
        ])

        prompt = f"""
作为面试官，请基于以下面试表现，总结候选人的3个主要优势。

平均评分：
- 技术能力: {avg_technical}/10
- 沟通能力: {avg_communication}/10
- 问题解决: {avg_problem_solving}/10
- 文化匹配: {avg_cultural_fit}/10

面试详情：
{rounds_summary}

请以JSON数组格式返回3个具体的优势，每个优势要具体指出候选人表现好的地方：
["优势1", "优势2", "优势3"]

要求：
1. 优势要具体，结合实际回答内容
2. 突出候选人的亮点
3. 每个优势控制在30字以内
"""

        try:
            response = await self.client.chat.completions.create(
                model="qwen-max",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return ["表现稳定", "回答清晰", "态度积极"]

    async def _generate_weaknesses(
        self,
        rounds: List[Dict[str, Any]],
        avg_technical: float,
        avg_communication: float,
        avg_problem_solving: float,
        avg_cultural_fit: float
    ) -> List[str]:
        """使用LLM生成劣势分析"""
        rounds_summary = "\n\n".join([
            f"第{i+1}轮:\n问题: {r['question']}\n回答: {r['answer']}\n评分: 技术{r.get('evaluation_data', {}).get('technical_score', 0)}/10, "
            f"沟通{r.get('evaluation_data', {}).get('communication_score', 0)}/10, "
            f"问题解决{r.get('evaluation_data', {}).get('problem_solving_score', 0)}/10"
            for i, r in enumerate(rounds)
        ])

        prompt = f"""
作为面试官，请基于以下面试表现，客观指出候选人的2-3个待改进方面。

平均评分：
- 技术能力: {avg_technical}/10
- 沟通能力: {avg_communication}/10
- 问题解决: {avg_problem_solving}/10
- 文化匹配: {avg_cultural_fit}/10

面试详情：
{rounds_summary}

请以JSON数组格式返回2-3个需要改进的方面：
["待改进1", "待改进2"]

要求：
1. 客观指出不足，不要过于严厉
2. 结合实际表现
3. 每个点控制在30字以内
"""

        try:
            response = await self.client.chat.completions.create(
                model="qwen-max",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return ["部分回答可以更深入", "表达可以更简洁"]

    async def _generate_suggestions(
        self,
        rounds: List[Dict[str, Any]],
        interview_type: str,
        performance_level: str
    ) -> List[str]:
        """使用LLM生成改进建议"""
        rounds_summary = "\n\n".join([
            f"第{i+1}轮:\n问题: {r['question']}\n回答: {r['answer']}"
            for i, r in enumerate(rounds)
        ])

        prompt = f"""
作为面试官，请基于以下{interview_type}面试表现（整体水平：{performance_level}），给出3个具体的提升建议。

面试详情：
{rounds_summary}

请以JSON数组格式返回3个可操作的建议：
["建议1", "建议2", "建议3"]

要求：
1. 建议要具体可操作
2. 针对候选人的实际情况
3. 每个建议控制在40字以内
"""

        try:
            response = await self.client.chat.completions.create(
                model="qwen-max",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return ["多练习类似问题", "加强基础知识学习", "提升表达能力"]

    def _get_default_final_evaluation(self) -> Dict[str, Any]:
        """获取默认最终评估"""
        return {
            "technical_score": 5,
            "communication_score": 5,
            "problem_solving_score": 5,
            "cultural_fit_score": 5,
            "total_score": 20,
            "performance_level": "合格",
            "strengths": [],
            "weaknesses": [],
            "suggestions": []
        }

