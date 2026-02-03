"""
培训评价报告生成器 - Markdown 格式
"""
from datetime import datetime


def generate_markdown_report(evaluation_data: dict) -> str:
    """
    生成培训评价报告 Markdown

    Args:
        evaluation_data: 评价数据字典，包含所有报告信息

    Returns:
        str: Markdown 格式的报告内容
    """
    # 获取数据
    trainee_name = evaluation_data.get('trainee_name', '未知')
    scenario_name = evaluation_data.get('scenario_name', '销售培训场景')
    completed_at = evaluation_data.get('completed_at', '')
    duration_minutes = evaluation_data.get('duration_minutes', 0)

    scores = evaluation_data.get('scores', {})
    total_score = scores.get('total_score', 0)
    performance_level = scores.get('performance_level', 'average')

    # 性能等级映射
    level_map = {
        'excellent': '优秀 ⭐⭐⭐⭐⭐',
        'good': '良好 ⭐⭐⭐⭐',
        'average': '一般 ⭐⭐⭐',
        'poor': '需改进 ⭐⭐'
    }
    level_text = level_map.get(performance_level, '一般')

    # 格式化时间
    if completed_at:
        try:
            dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            completed_at_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            completed_at_str = completed_at
    else:
        completed_at_str = '未完成'

    overall_strengths = evaluation_data.get('overall_strengths', [])
    overall_weaknesses = evaluation_data.get('overall_weaknesses', [])
    key_improvements = evaluation_data.get('key_improvements', [])
    uncompleted_tasks = evaluation_data.get('uncompleted_tasks', [])
    stage_details = evaluation_data.get('stage_details', [])

    # 任务名称映射
    task_names = {
        'trust_building_score': '信任与关系建立',
        'needs_diagnosis_score': '信息探索与需求诊断',
        'value_presentation_score': '价值呈现与方案链接',
        'objection_handling_score': '异议/顾虑处理管理',
        'progress_management_score': '进程推进与节奏管理',
    }

    # 构建 Markdown
    md = f"""# 销售培训评价报告

---

## 基本信息

- **学员姓名**: {trainee_name}
- **培训场景**: {scenario_name}
- **完成时间**: {completed_at_str}
- **培训时长**: {duration_minutes} 分钟

---

## 总体评分

### 🎯 综合得分: {total_score}/25

**表现等级**: {level_text}

---

## 各项得分详情

"""

    # 添加各项得分
    for key, name in task_names.items():
        score = scores.get(key, 0)
        stars = '⭐' * score + '☆' * (5 - score)
        md += f"### {name}\n\n"
        md += f"**得分**: {score}/5 {stars}\n\n"

    md += "---\n\n"

    # 核心优势
    if overall_strengths:
        md += "## ✅ 核心优势\n\n"
        for i, strength in enumerate(overall_strengths, 1):
            md += f"{i}. {strength}\n"
        md += "\n---\n\n"

    # 主要不足
    if overall_weaknesses:
        md += "## ⚠️ 主要不足\n\n"
        for i, weakness in enumerate(overall_weaknesses, 1):
            md += f"{i}. {weakness}\n"
        md += "\n---\n\n"

    # 关键改进建议
    if key_improvements:
        md += "## 💡 关键改进建议\n\n"
        for i, improvement in enumerate(key_improvements, 1):
            md += f"{i}. {improvement}\n"
        md += "\n---\n\n"

    # 未完成任务
    if uncompleted_tasks:
        md += "## ❌ 未完成任务\n\n"
        for i, task in enumerate(uncompleted_tasks, 1):
            md += f"{i}. {task}\n"
        md += "\n---\n\n"

    # 各阶段详细评价
    if stage_details:
        md += "## 📊 各阶段详细评价\n\n"
        for stage in stage_details:
            stage_num = stage.get('stage', 0)
            stage_name = stage.get('stage_name', '')
            stage_score = stage.get('score', 0)
            rounds_used = stage.get('rounds_used', 0)
            strengths = stage.get('strengths', [])
            weaknesses = stage.get('weaknesses', [])
            suggestions = stage.get('suggestions', [])

            stars = '⭐' * stage_score + '☆' * (5 - stage_score)
            md += f"### 阶段 {stage_num}: {stage_name}\n\n"
            md += f"**得分**: {stage_score}/5 {stars} | **用时**: {rounds_used} 轮\n\n"

            if strengths:
                md += "#### ✓ 优点\n\n"
                for s in strengths:
                    md += f"- {s}\n"
                md += "\n"

            if weaknesses:
                md += "#### ⚠ 不足\n\n"
                for w in weaknesses:
                    md += f"- {w}\n"
                md += "\n"

            if suggestions:
                md += "#### 💡 建议\n\n"
                for sg in suggestions:
                    md += f"- {sg}\n"
                md += "\n"

            md += "---\n\n"

    # 页脚
    md += f"""
---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**系统**: VividCrowd 销售培训系统
"""

    return md
