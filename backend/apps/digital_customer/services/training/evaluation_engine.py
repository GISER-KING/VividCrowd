"""
评价引擎 - 实时分析和最终评分
"""
from typing import Dict, List, Any
from loguru import logger
import json
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.db_models import TrainingSession, ConversationRound, StageEvaluation, CustomerChunk
from backend.core.config import settings
from dashscope import Generation


# 评分标准映射表
SCORING_CRITERIA = {
    1: {  # 信任与关系建立
        "task_name": "信任与关系建立",
        "score_1": "未判断客户是否具备沟通意愿；在明显防御状态下直接推进",
        "score_2": "意识到互动问题但未调整沟通方式",
        "score_3": "建立基本沟通条件但不稳定",
        "score_4": "能根据互动状态调整沟通方式",
        "score_5": "明确判断是否具备继续沟通条件并据此决策"
    },
    2: {  # 信息探索与需求诊断
        "task_name": "信息探索与需求诊断",
        "score_1": "未形成任何需求判断",
        "score_2": "收集零散信息但未结构化",
        "score_3": "形成初步问题判断但存在关键缺口",
        "score_4": "判断结构基本完整，个别要素不清",
        "score_5": "形成清晰、可用于决策的需求诊断结构"
    },
    3: {  # 价值呈现与方案链接
        "task_name": "价值呈现与方案链接",
        "score_1": "未建立需求与方案关系",
        "score_2": "仅介绍方案内容，无对应逻辑",
        "score_3": "存在对应尝试但逻辑不完整",
        "score_4": "对应关系基本清晰但边界模糊",
        "score_5": "清晰完成需求—方案映射并说明适用边界"
    },
    4: {  # 异议/顾虑处理管理
        "task_name": "异议/顾虑处理管理",
        "score_1": "忽视明显异议或顾虑",
        "score_2": "注意到异议但未区分类型",
        "score_3": "识别异议但回应方式不匹配",
        "score_4": "异议得到回应但仍存在残留不确定",
        "score_5": "异议被正确识别、分类并得到澄清或确认"
    },
    5: {  # 进程推进与节奏管理
        "task_name": "进程推进与节奏管理",
        "score_1": "多次在信息不足或不匹配时推进",
        "score_2": "出现明显过早或滞后推进",
        "score_3": "推进节奏偶有偏差",
        "score_4": "节奏整体合理，个别节点判断不稳",
        "score_5": "推进/放缓/终止均基于当下信息状态判断"
    }
}


class EvaluationEngine:
    """评价引擎 - 使用Qwen-plus进行智能评价"""

    def _get_stage_criteria(self, stage: int) -> Dict[str, str]:
        """获取阶段评分标准"""
        from .stage_controller import StageController
        controller = StageController()
        stage_info = controller.get_stage_info(stage)
        return {
            "name": stage_info.get("name", f"阶段{stage}"),
            "objectives": ", ".join(stage_info.get("required_tasks", [])),
            "criteria": ", ".join(stage_info.get("completion_criteria", []))
        }

    async def analyze_message(
        self,
        message: str,
        stage: int,
        session: TrainingSession,
        db_session: Session = None
    ) -> Dict[str, Any]:
        """实时分析销售话术质量"""

        stage_criteria = self._get_stage_criteria(stage)

        # 构建客户画像上下文
        customer_context = ""
        if session.customer_profile:
            p = session.customer_profile
            customer_context = f"""
【客户背景知识】
- 客户姓名: {p.name or '未知'}
- 画像类型: {p.profile_type}
- 行业/职业: {p.industry or '未知'} / {p.occupation or '未知'}
- 性格特征: {p.personality_traits or '未知'}
- 痛点: {p.pain_points or '未知'}
- 需求: {p.needs or '未知'}
- 常见异议: {p.objections or '未知'}
"""
            # 如果有db_session，尝试从chunks获取更多上下文（作为补充）
            if db_session:
                try:
                    # 简单获取前2个chunk作为补充背景
                    chunks = db_session.execute(
                        select(CustomerChunk.chunk_text)
                        .where(CustomerChunk.customer_profile_id == p.id)
                        .limit(2)
                    ).scalars().all()
                    if chunks:
                        customer_context += "\n【客户详细背景片段】:\n" + "\n".join([f"- {c[:200]}..." for c in chunks])
                except Exception as e:
                    logger.warning(f"Failed to fetch customer chunks: {e}")

        prompt = f"""你是一位资深销售培训专家。请分析以下销售话术的质量。

{customer_context}

当前阶段：{stage} - {stage_criteria['name']}
阶段目标：{stage_criteria['objectives']}

销售话术：
{message}

【第一步：深度客户画像分析】
请仔细分析客户画像，提取以下关键信息：

1. **客户类型识别**：
   - 如果职位是"总监/总经理/CEO/采购经理/主任"等，这是 **B2B企业采购场景**
   - 如果是"个人/家庭用户"或职位为空，这是 **B2C个人消费场景**

2. **核心痛点提取**（必须引用具体数据）：
   - 客户当前面临的最大问题是什么？
   - 有没有具体的数据或指标（如流失率、成本、时间）？
   - 客户的情绪状态是什么（焦虑/满意/观望）？

3. **决策角色与权限**：
   - 客户在采购决策中的角色（决策者/影响者/使用者）
   - 预算权限和采购周期
   - 需要谁的最终审批

4. **信任建立方式**（客户如何建立信任）：
   - 需要什么样的案例证明（同行业/同规模/三甲医院）
   - 需要什么资质或认证
   - 是否需要试点或试用

5. **常见异议识别**：
   - 客户通常会提出哪些质疑
   - 客户对什么最敏感（价格/质量/服务/资质）

6. **易被说服点**：
   - 什么样的承诺或保证能打动客户
   - 客户最看重什么（数据/案例/培训/退款保证）

7. **沟通禁忌**：
   - 有哪些话题或说法是客户反感的
   - 需要避免什么样的营销话术

【第二步：话术质量评价】
基于客户画像，评价销售话术：

1. 是否使用了正确的职位称呼（总监/主任/女士）
2. 是否引用了客户的具体痛点和数据
3. 是否提供了客户要求的信任证据（案例/资质/试点）
4. 是否回应了客户的常见异议
5. 是否触犯了沟通禁忌
6. 是否符合当前阶段目标
7. 推进节奏是否合理

**重要警告**：
- 客户画像中的数据（如流失率、成本等）是客户的问题数据，不是销售人员的解决方案数据
- 不要建议销售人员引用不存在的案例数据或成果数据
- 如果销售人员需要提供具体案例或数据，应该建议他们说"我们有相关案例"而不是编造具体数字
- 只评价销售人员是否正确理解和引用了客户的痛点，不要要求他们提供不存在的数据

【第三步：生成改进建议】
**重要要求：建议必须高度个性化，引用客户画像的具体信息**

**医疗行业B2B场景**（如：医院总监/主任）：
- 称呼：使用职位（总监、主任）+ 贵院/贵中心
- 必须引用：客户的具体痛点数据（如"18%流失率"）
- 必须提供：同类医院案例 + 具体数据（如"22%提升"）
- 必须回应：资质认证、临床依据、培训支持
- 必须使用：循证医学语言、专业术语
- 必须避免：营销话术、夸大疗效、说"替代传统"
- 示例格式："[称呼]，了解到[具体痛点+数据]，我们的[产品]已在[同类案例]应用，[具体成果数据]。我们可以[信任建立方式]，并提供[易被说服点]。"

**企业HR/总经理场景**：
- 称呼：使用职位 + 贵公司
- 必须引用：员工规模、健康管理成本、缺勤率等数据
- 必须提供：同行业企业案例 + ROI数据
- 必须强调：成本效益、员工福利、团队健康
- 示例格式："[称呼]，考虑到贵公司有[员工数]名员工，[当前痛点]，我们的方案可以[具体收益+数据]..."

**B2C个人场景**：
- 称呼：女士/先生 + 您/您的家人
- 必须引用：家人健康担忧、预算关注
- 必须提供：用户评价、专业认证
- 必须强调：性价比、便利性、家庭关怀
- 示例格式："[称呼]，根据您提到的[具体担忧]，我们的[产品]可以[具体帮助]..."

**每条建议必须包含**：
1. 正确的职位称呼
2. 客户的具体痛点或数据（直接引用）
3. 针对性的解决方案
4. 信任建立证据（案例/资质/试点）
5. 具体的数据支撑
6. 易被说服点（保证/培训/退款）
7. 避免沟通禁忌
8. 每条建议150字以内

返回JSON格式：
{{
    "customer_type": "医疗行业B2B" 或 "企业HR" 或 "B2C个人消费",
    "customer_key_pain": "具体痛点描述（含数据）",
    "customer_trust_method": "信任建立方式",
    "customer_objections": ["常见异议1", "常见异议2"],
    "communication_taboos": ["禁忌1", "禁忌2"],
    "quality": "excellent/good/fair/poor",
    "issues": ["发现的问题（如：未使用职位称呼、未引用痛点数据、触犯禁忌）"],
    "suggestions": [
        {{
            "context": "基于客户是[职位]，当前面临[具体痛点+数据]，需要[信任方式]",
            "suggestion": "具体的改进建议和话术示例（必须包含：称呼+痛点引用+解决方案+案例数据+信任证据+易被说服点）"
        }}
    ]
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_qwen_plus(prompt)

            # 向后兼容：如果 suggestions 是新格式（对象数组），转换为字符串数组供前端显示
            if result.get("suggestions") and isinstance(result["suggestions"], list):
                if len(result["suggestions"]) > 0 and isinstance(result["suggestions"][0], dict):
                    # 新格式：转换为 "context: suggestion" 格式
                    result["suggestions"] = [
                        f"{s.get('context', '')}: {s.get('suggestion', '')}"
                        for s in result["suggestions"]
                    ]

            return result
        except Exception as e:
            logger.error(f"Message analysis failed: {e}")
            return {
                "quality": "fair",
                "issues": [],
                "suggestions": []
            }

    def _get_stage_rounds(self, session: TrainingSession, stage: int) -> List[ConversationRound]:
        """获取指定阶段的所有对话轮次"""
        return [r for r in session.rounds if r.stage == stage]

    def _format_conversation(self, rounds: List[ConversationRound]) -> str:
        """格式化对话内容"""
        return "\n\n".join([
            f"【第{r.round_number}轮】\n销售: {r.trainee_message}\n客户: {r.customer_response}"
            for r in rounds
        ])

    async def evaluate_stage(
        self,
        session: TrainingSession,
        stage: int
    ) -> Dict[str, Any]:
        """评价单个阶段的表现"""

        rounds = self._get_stage_rounds(session, stage)

        if not rounds:
            return {
                "score": 1,
                "strengths": [],
                "weaknesses": ["未进行有效沟通"],
                "suggestions": ["需要主动开启对话"],
                "evidence": "无对话记录"
            }

        # 构建完整对话
        conversation = self._format_conversation(rounds)

        # 获取评分标准
        criteria = SCORING_CRITERIA.get(stage, {})

        prompt = f"""评价销售在"{criteria['task_name']}"阶段的表现。

评分标准（1-5分）：
1分：{criteria['score_1']}
2分：{criteria['score_2']}
3分：{criteria['score_3']}
4分：{criteria['score_4']}
5分：{criteria['score_5']}

对话内容：
{conversation}

返回JSON：
{{
    "score": 1-5,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"],
    "suggestions": ["建议1", "建议2"],
    "evidence": "评分依据"
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_qwen_plus(prompt)
            # 确保score在1-5范围内
            if "score" in result:
                result["score"] = max(1, min(5, result["score"]))
            return result
        except Exception as e:
            logger.error(f"Stage evaluation failed: {e}")
            return {
                "score": 3,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "evidence": "评价失败"
            }

    async def generate_final_report(
        self,
        session: TrainingSession,
        scores: Dict[str, int]
    ) -> Dict[str, Any]:
        """生成最终评价报告"""

        # 收集所有对话
        all_rounds = session.rounds
        full_conversation = self._format_conversation(all_rounds)

        # 收集阶段评价
        stage_evaluations = {}
        for eval in session.stage_evaluations:
            stage_evaluations[eval.stage_number] = {
                "score": eval.score,
                "strengths": eval.strengths or [],
                "weaknesses": eval.weaknesses or []
            }

        prompt = f"""生成销售培训的最终评价报告。

5项核心任务得分：
1. 信任与关系建立：{scores.get('trust_building', 0)}/5
2. 信息探索与需求诊断：{scores.get('needs_diagnosis', 0)}/5
3. 价值呈现与方案链接：{scores.get('value_presentation', 0)}/5
4. 异议处理管理：{scores.get('objection_handling', 0)}/5
5. 进程推进与节奏管理：{scores.get('progress_management', 0)}/5

总分：{scores.get('total', 0)}/25

各阶段详细评价：
{json.dumps(stage_evaluations, ensure_ascii=False, indent=2)}

完整对话记录：
{full_conversation}

请生成：
1. 整体表现总结
2. 核心优势（3-5条）
3. 主要不足（3-5条）
4. 关键改进建议（5-8条）
5. 未完成的任务列表

返回JSON格式：
{{
    "overall_summary": "整体表现总结",
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["不足1", "不足2", "不足3"],
    "improvements": ["建议1", "建议2", "建议3", "建议4", "建议5"],
    "uncompleted_tasks": ["未完成任务1", "未完成任务2"]
}}

只返回JSON，不要其他内容。"""

        try:
            result = await self._call_qwen_plus(prompt)
            return result
        except Exception as e:
            logger.error(f"Final report generation failed: {e}")
            return {
                "overall_summary": "评价报告生成失败",
                "strengths": [],
                "weaknesses": [],
                "improvements": [],
                "uncompleted_tasks": []
            }

    async def _call_qwen_plus(self, prompt: str) -> Dict:
        """调用Qwen-max API（统一使用qwen-max模型）"""
        try:
            response = Generation.call(
                model='qwen-max',
                prompt=prompt,
                api_key=settings.DASHSCOPE_API_KEY,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试解析JSON
                try:
                    # 移除可能的markdown代码块标记
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()

                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {content}")
                    return {}
            else:
                logger.error(f"Qwen API error: {response.message}")
                return {}
        except Exception as e:
            logger.error(f"Qwen API call failed: {e}")
            return {}
