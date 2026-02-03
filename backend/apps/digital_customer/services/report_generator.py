"""
培训评价报告生成器
使用 xhtml2pdf 将 HTML 模板转换为 PDF
"""
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime


def generate_pdf_report(evaluation_data: dict) -> BytesIO:
    """
    生成培训评价报告 PDF

    Args:
        evaluation_data: 评价数据字典，包含所有报告信息

    Returns:
        BytesIO: PDF 文件的字节流
    """
    html_content = _generate_html_template(evaluation_data)

    # 创建 PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        html_content.encode('utf-8'),
        dest=pdf_buffer,
        encoding='utf-8'
    )

    if pisa_status.err:
        raise Exception(f"PDF 生成失败: {pisa_status.err}")

    pdf_buffer.seek(0)
    return pdf_buffer


def _generate_html_template(data: dict) -> str:
    """生成 HTML 模板"""

    # 获取数据
    trainee_name = data.get('trainee_name', '未知')
    scenario_name = data.get('scenario_name', '销售培训场景')
    completed_at = data.get('completed_at', '')
    duration_minutes = data.get('duration_minutes', 0)

    scores = data.get('scores', {})
    total_score = scores.get('total_score', 0)
    performance_level = scores.get('performance_level', 'average')

    # 性能等级映射
    level_map = {
        'excellent': '优秀',
        'good': '良好',
        'average': '一般',
        'poor': '需改进'
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

    overall_strengths = data.get('overall_strengths', [])
    overall_weaknesses = data.get('overall_weaknesses', [])
    key_improvements = data.get('key_improvements', [])
    uncompleted_tasks = data.get('uncompleted_tasks', [])
    stage_details = data.get('stage_details', [])

    # 任务名称映射
    task_names = {
        'trust_building_score': '信任与关系建立',
        'needs_diagnosis_score': '信息探索与需求诊断',
        'value_presentation_score': '价值呈现与方案链接',
        'objection_handling_score': '异议/顾虑处理管理',
        'progress_management_score': '进程推进与节奏管理',
    }

    # 构建 HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}

        body {{
            font-family: "SimSun", "Microsoft YaHei", sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}

        .header h1 {{
            color: #667eea;
            font-size: 24pt;
            margin: 0 0 10px 0;
        }}

        .header .meta {{
            color: #666;
            font-size: 10pt;
        }}

        .score-box {{
            background: #f0f4ff;
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }}

        .score-box .total {{
            font-size: 36pt;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}

        .score-box .level {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14pt;
            font-weight: bold;
        }}

        .section {{
            margin: 25px 0;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 16pt;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #667eea;
        }}

        .score-item {{
            margin: 12px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
        }}

        .score-item .name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}

        .score-item .value {{
            color: #667eea;
            font-weight: bold;
            float: right;
        }}

        .score-bar {{
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }}

        .score-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}

        ul {{
            list-style: none;
            padding: 0;
        }}

        ul li {{
            margin: 8px 0;
            padding-left: 25px;
            position: relative;
        }}

        ul li:before {{
            content: "●";
            position: absolute;
            left: 0;
            color: #667eea;
        }}

        .strength-section {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 15px 0;
        }}

        .weakness-section {{
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 15px 0;
        }}

        .improvement-section {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 15px 0;
        }}

        .stage-box {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            page-break-inside: avoid;
        }}

        .stage-header {{
            font-weight: bold;
            font-size: 14pt;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .stage-score {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11pt;
            margin-left: 10px;
        }}

        .subsection {{
            margin: 10px 0;
        }}

        .subsection-title {{
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #999;
            font-size: 9pt;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>销售培训评价报告</h1>
        <div class="meta">
            学员：{trainee_name} | 场景：{scenario_name}<br>
            完成时间：{completed_at_str} | 培训时长：{duration_minutes} 分钟
        </div>
    </div>

    <div class="score-box">
        <div>总体评分</div>
        <div class="total">{total_score}/25</div>
        <div class="level">{level_text}</div>
    </div>

    <div class="section">
        <div class="section-title">各项得分详情</div>
"""

    # 添加各项得分
    for key, name in task_names.items():
        score = scores.get(key, 0)
        percentage = (score / 5) * 100
        html += f"""
        <div class="score-item">
            <div class="name">{name}<span class="value">{score}/5</span></div>
            <div class="score-bar">
                <div class="score-bar-fill" style="width: {percentage}%;"></div>
            </div>
        </div>
"""

    html += """
    </div>
"""

    # 核心优势
    if overall_strengths:
        html += """
    <div class="section">
        <div class="section-title">核心优势</div>
        <div class="strength-section">
            <ul>
"""
        for strength in overall_strengths:
            html += f"                <li>{strength}</li>\n"
        html += """
            </ul>
        </div>
    </div>
"""

    # 主要不足
    if overall_weaknesses:
        html += """
    <div class="section">
        <div class="section-title">主要不足</div>
        <div class="weakness-section">
            <ul>
"""
        for weakness in overall_weaknesses:
            html += f"                <li>{weakness}</li>\n"
        html += """
            </ul>
        </div>
    </div>
"""

    # 关键改进建议
    if key_improvements:
        html += """
    <div class="section">
        <div class="section-title">关键改进建议</div>
        <div class="improvement-section">
            <ul>
"""
        for improvement in key_improvements:
            html += f"                <li>{improvement}</li>\n"
        html += """
            </ul>
        </div>
    </div>
"""

    # 未完成任务
    if uncompleted_tasks:
        html += """
    <div class="section">
        <div class="section-title">未完成任务</div>
        <div class="weakness-section">
            <ul>
"""
        for task in uncompleted_tasks:
            html += f"                <li>{task}</li>\n"
        html += """
            </ul>
        </div>
    </div>
"""

    # 各阶段详细评价
    if stage_details:
        html += """
    <div class="section">
        <div class="section-title">各阶段详细评价</div>
"""
        for stage in stage_details:
            stage_num = stage.get('stage', 0)
            stage_name = stage.get('stage_name', '')
            stage_score = stage.get('score', 0)
            rounds_used = stage.get('rounds_used', 0)
            strengths = stage.get('strengths', [])
            weaknesses = stage.get('weaknesses', [])
            suggestions = stage.get('suggestions', [])

            html += f"""
        <div class="stage-box">
            <div class="stage-header">
                阶段 {stage_num}：{stage_name}
                <span class="stage-score">{stage_score}/5</span>
                <span style="color: #999; font-size: 10pt; margin-left: 10px;">用时 {rounds_used} 轮</span>
            </div>
"""

            if strengths:
                html += """
            <div class="subsection">
                <div class="subsection-title" style="color: #4caf50;">✓ 优点</div>
                <ul>
"""
                for s in strengths:
                    html += f"                    <li>{s}</li>\n"
                html += """
                </ul>
            </div>
"""

            if weaknesses:
                html += """
            <div class="subsection">
                <div class="subsection-title" style="color: #ff9800;">⚠ 不足</div>
                <ul>
"""
                for w in weaknesses:
                    html += f"                    <li>{w}</li>\n"
                html += """
                </ul>
            </div>
"""

            if suggestions:
                html += """
            <div class="subsection">
                <div class="subsection-title" style="color: #2196f3;">💡 建议</div>
                <ul>
"""
                for sg in suggestions:
                    html += f"                    <li>{sg}</li>\n"
                html += """
                </ul>
            </div>
"""

            html += """
        </div>
"""

        html += """
    </div>
"""

    # 页脚
    html += f"""
    <div class="footer">
        报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        VividCrowd 销售培训系统
    </div>
</body>
</html>
"""

    return html
