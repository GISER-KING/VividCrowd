"""
产品文档需求分析脚本
"""
import re

def analyze_algorithm_doc():
    """分析算法文档需求"""
    with open('algorithm.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    requirements = []

    # 提取关键需求点
    if '简历深度解析' in content:
        requirements.append('简历深度解析与动态提问')
    if '10个面试问题' in content:
        requirements.append('生成10个阶梯式面试问题')
    if '追问设计' in content or '追问逻辑' in content:
        requirements.append('智能追问机制')
    if '评分' in content:
        requirements.append('回答评分系统')
    if '语音' in content:
        requirements.append('语音识别与处理')
    if '情感' in content or '表情' in content:
        requirements.append('情感分析')
    if '作弊' in content or '防作弊' in content:
        requirements.append('作弊检测')
    if '视频' in content:
        requirements.append('视频流处理')

    return requirements

def analyze_resume_doc():
    """分析简历文档需求"""
    with open('resume.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    requirements = []

    if 'PDF' in content or 'Word' in content:
        requirements.append('多格式简历解析')
    if '提取' in content or '解析' in content:
        requirements.append('信息提取与结构化')
    if '评分' in content:
        requirements.append('简历评分系统')
    if '匹配' in content:
        requirements.append('简历职位匹配')
    if '质量' in content:
        requirements.append('简历质量评估')
    if '优化建议' in content:
        requirements.append('简历优化建议')
    if '检索' in content or '搜索' in content:
        requirements.append('简历库检索')

    return requirements

def analyze_user_admin_doc():
    """分析用户端管理端文档需求"""
    with open('user_admin.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    requirements = []

    if '准备' in content or '指南' in content:
        requirements.append('面试准备指南')
    if '进度' in content:
        requirements.append('实时进度显示')
    if '中断' in content or '恢复' in content:
        requirements.append('面试中断恢复')
    if '重新录制' in content or '重录' in content:
        requirements.append('重新录制功能')
    if '批量导入' in content:
        requirements.append('批量导入候选人')
    if '模板' in content:
        requirements.append('面试模板管理')
    if '导出' in content:
        requirements.append('数据导出功能')
    if '统计' in content or '仪表板' in content:
        requirements.append('统计仪表板')
    if '权限' in content:
        requirements.append('权限管理')
    if '通知' in content:
        requirements.append('通知系统')

    return requirements

if __name__ == "__main__":
    print("=== 产品文档需求分析 ===\n")

    print("【算法文档需求】")
    algo_reqs = analyze_algorithm_doc()
    for i, req in enumerate(algo_reqs, 1):
        print(f"{i}. {req}")

    print("\n【简历文档需求】")
    resume_reqs = analyze_resume_doc()
    for i, req in enumerate(resume_reqs, 1):
        print(f"{i}. {req}")

    print("\n【用户端管理端文档需求】")
    user_reqs = analyze_user_admin_doc()
    for i, req in enumerate(user_reqs, 1):
        print(f"{i}. {req}")

    print(f"\n总计需求数: {len(algo_reqs) + len(resume_reqs) + len(user_reqs)}")
