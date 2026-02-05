# 数字面试官子应用 - 功能设计文档

> **版本**: v1.0
> **创建日期**: 2026-02-05
> **设计目标**: 基于现有架构新增数字面试官模块,提供可配置的AI面试训练场景

---

## 📋 目录

1. [系统概述](#系统概述)
2. [核心功能](#核心功能)
3. [数据模型设计](#数据模型设计)
4. [后端API设计](#后端api设计)
5. [AI Agent设计](#ai-agent设计)
6. [前端组件设计](#前端组件设计)
7. [面试流程设计](#面试流程设计)
8. [数字人视频录制指南](#数字人视频录制指南)
9. [路由集成方案](#路由集成方案)
10. [技术决策](#技术决策)
11. [实现优先级](#实现优先级)

---

## 系统概述

### 1.1 功能定位

数字面试官是一个**AI驱动的面试训练系统**,帮助求职者通过模拟真实面试场景提升面试技巧。系统支持:

- ✅ **多种面试类型**: 技术面试、HR面试、行为面试等(可配置)
- ✅ **智能提问**: 基于RAG知识库生成面试问题
- ✅ **实时评估**: 对候选人回答进行多维度评价
- ✅ **数字人交互**: 预录视频片段模拟真实面试官
- ✅ **语音对话**: 支持语音输入输出,沉浸式体验
- ✅ **面试报告**: 生成详细的表现分析和改进建议

### 1.2 与现有模块的关系

| 现有模块 | 可复用内容 | 差异点 |
|---------|-----------|--------|
| **销售演练** | 训练流程、评估引擎、报告生成 | 面试场景更结构化,评估维度不同 |
| **数字客户** | 画像解析、RAG检索、语音服务 | 面试官主动提问,候选人被动回答 |
| **数字分身** | 数字人视频播放逻辑 | 面试官视频状态更丰富 |

### 1.3 技术栈

- **后端**: FastAPI + SQLAlchemy + DashScope (qwen-max)
- **前端**: React + Ant Design + TailwindCSS
- **数据库**: SQLite (独立数据库 `digital_interviewer.db`)
- **AI能力**:
  - LLM: Qwen-Max (问题生成、回答评估)
  - RAG: BM25 + Embedding 混合检索
  - ASR/TTS: DashScope Paraformer + Sambert
- **数字人**: 预录视频片段 (4种状态)

---

## 核心功能

### 2.1 面试官管理

**功能描述**: 上传面试官画像文档,系统自动解析并生成面试官Agent。

**支持格式**: PDF / Markdown

**画像内容**:
```json
{
  "name": "张技术",
  "role": "技术面试官",
  "company": "某互联网公司",
  "experience_years": 10,
  "expertise": ["Python", "系统设计", "算法"],
  "interview_style": "严谨、注重细节、喜欢追问",
  "typical_questions": [
    "请介绍一下你最有挑战性的项目",
    "如何设计一个高并发系统"
  ],
  "evaluation_focus": ["技术深度", "问题解决能力", "沟通表达"]
}
```

**数字人视频**: 用户需为每个面试官录制4种状态视频(详见第8章)

### 2.2 面试训练模式

**流程概览**:
```
选择面试官 → 配置面试类型 → 开始面试 →
实时对话(语音/文字) → 实时反馈 →
面试结束 → 生成报告
```

**面试类型**(可配置编排):
1. **技术面试**: 编程、算法、系统设计
2. **HR面试**: 自我介绍、职业规划、离职原因
3. **行为面试**: STAR法则、团队协作、冲突处理
4. **综合面试**: 混合多种类型

**实时反馈**:
- 回答质量评分 (1-5分)
- 问题识别 (逻辑混乱、答非所问、过于简短等)
- 改进建议 (实时显示在右侧面板)

### 2.3 知识库管理

**面试题库**:
- 存储各类面试问题和参考答案
- 支持按类型、难度、领域分类
- 用于面试官生成问题时的RAG检索

**评估标准库**:
- 存储优秀回答案例
- 评分标准和维度定义
- 用于评估候选人回答质量

**导入方式**: PDF文档上传,自动解析入库

### 2.4 面试报告

**报告内容**:
- 总体评分 (百分制)
- 各维度得分 (雷达图)
- 优势总结
- 待改进点
- 具体问题回放和点评
- 推荐学习资源

**导出格式**: Markdown + PDF

---

## 数据模型设计

### 3.1 数据库表结构

#### 表1: `interviewer_profiles` (面试官画像表)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 面试官姓名 |
| role | VARCHAR(50) | 角色 (技术面试官/HR面试官等) |
| company | VARCHAR(100) | 公司 |
| experience_years | INTEGER | 工作年限 |
| expertise | JSON | 专业领域列表 |
| interview_style | TEXT | 面试风格描述 |
| evaluation_focus | JSON | 评估关注点 |
| system_prompt | TEXT | AI Agent的系统提示词 |
| raw_content | TEXT | 原始文档内容 |
| source_file_path | VARCHAR(255) | 源文件路径 |
| video_idle | VARCHAR(255) | 待机状态视频URL |
| video_speaking | VARCHAR(255) | 说话状态视频URL |
| video_listening | VARCHAR(255) | 倾听状态视频URL |
| video_thinking | VARCHAR(255) | 思考状态视频URL |
| created_at | DATETIME | 创建时间 |

#### 表2: `interview_sessions` (面试会话表)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | INTEGER | 主键 |
| session_id | VARCHAR(36) | UUID会话ID |
| interviewer_id | INTEGER | 面试官ID (FK) |
| user_id | VARCHAR(100) | 用户ID |
| interview_type | VARCHAR(50) | 面试类型 |
| current_question_index | INTEGER | 当前问题索引 |
| total_questions | INTEGER | 总问题数 |
| status | VARCHAR(20) | 状态 (in_progress/completed) |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |

#### 表3: `interview_rounds` (面试轮次表)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | INTEGER | 主键 |
| session_id | VARCHAR(36) | 会话ID (FK) |
| round_number | INTEGER | 轮次编号 |
| question | TEXT | 面试官问题 |
| question_type | VARCHAR(50) | 问题类型 |
| candidate_answer | TEXT | 候选人回答 |
| answer_duration | INTEGER | 回答时长(秒) |
| evaluation_score | INTEGER | 评分 (1-5) |
| evaluation_feedback | TEXT | 评价反馈 |
| issues_found | JSON | 发现的问题列表 |
| suggestions | JSON | 改进建议列表 |
| created_at | DATETIME | 创建时间 |

#### 表4: `interview_evaluations` (面试评估表)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | INTEGER | 主键 |
| session_id | VARCHAR(36) | 会话ID (FK) |
| overall_score | INTEGER | 总分 (0-100) |
| dimension_scores | JSON | 各维度得分 |
| strengths | JSON | 优势列表 |
| weaknesses | JSON | 待改进点列表 |
| detailed_feedback | TEXT | 详细反馈 |
| recommendations | JSON | 推荐资源列表 |
| report_markdown | TEXT | Markdown格式报告 |
| report_pdf_path | VARCHAR(255) | PDF报告路径 |
| created_at | DATETIME | 创建时间 |

#### 表5: `interview_knowledge` (面试知识库表)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | INTEGER | 主键 |
| knowledge_type | VARCHAR(20) | 类型 (question/standard) |
| category | VARCHAR(50) | 分类 (技术/HR/行为) |
| difficulty | VARCHAR(20) | 难度 (easy/medium/hard) |
| question | TEXT | 问题内容 |
| reference_answer | TEXT | 参考答案 |
| evaluation_criteria | TEXT | 评估标准 |
| keywords | TEXT | 关键词 (用于BM25) |
| embedding | BLOB | Embedding向量 |
| created_at | DATETIME | 创建时间 |

#### 表6: `interviewer_profile_registry` (面试官档案注册表)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | INTEGER | 主键 |
| filename | VARCHAR(255) | 文件名 |
| file_hash | VARCHAR(64) | 文件MD5哈希 |
| interviewer_profile_id | INTEGER | 面试官ID (FK) |
| status | VARCHAR(20) | 状态 (success/failed) |
| imported_at | DATETIME | 导入时间 |

### 3.2 数据关系图

```
interviewer_profiles (1) ----< (N) interview_sessions
interview_sessions (1) ----< (N) interview_rounds
interview_sessions (1) ---- (1) interview_evaluations
```

---

## 后端API设计

### 4.1 目录结构

```
backend/apps/digital_interviewer/
├── app.py                          # FastAPI应用入口
├── __init__.py
└── services/
    ├── __init__.py
    ├── interviewer_agent.py        # 面试官AI Agent
    ├── interviewer_orchestrator.py # 面试编排器
    ├── profile_parser.py           # 画像解析服务
    ├── knowledge_service.py        # 知识库服务
    ├── evaluation_engine.py        # 评估引擎
    ├── question_generator.py       # 问题生成器
    ├── audio_service.py            # 语音服务(复用digital_customer)
    └── report_generator.py         # 报告生成器
```

### 4.2 REST API端点

#### 面试官管理

```python
# 获取所有面试官
GET /digital-interviewer/
Response: [
  {
    "id": 1,
    "name": "张技术",
    "role": "技术面试官",
    "company": "某互联网公司",
    "expertise": ["Python", "系统设计"],
    "has_videos": true
  }
]

# 获取指定面试官详情
GET /digital-interviewer/{interviewer_id}
Response: {
  "id": 1,
  "name": "张技术",
  "role": "技术面试官",
  "interview_style": "严谨、注重细节",
  "evaluation_focus": ["技术深度", "问题解决能力"],
  "video_urls": {
    "idle": "https://...",
    "speaking": "https://...",
    "listening": "https://...",
    "thinking": "https://..."
  }
}

# 上传面试官画像
POST /digital-interviewer/upload
Content-Type: multipart/form-data
Body:
  - file: PDF/Markdown文件
  - name: 面试官姓名(可选)
Response: {
  "id": 1,
  "name": "张技术",
  "message": "面试官画像创建成功"
}

# 上传数字人视频
POST /digital-interviewer/{interviewer_id}/videos
Content-Type: multipart/form-data
Body:
  - video_idle: 待机视频文件
  - video_speaking: 说话视频文件
  - video_listening: 倾听视频文件
  - video_thinking: 思考视频文件
Response: {
  "message": "视频上传成功",
  "video_urls": {...}
}

# 删除面试官
DELETE /digital-interviewer/{interviewer_id}
Response: {"message": "删除成功"}
```

#### 知识库管理

```python
# 上传面试知识库
POST /digital-interviewer/knowledge/upload
Content-Type: multipart/form-data
Body:
  - file: PDF文件
  - knowledge_type: "question" | "standard"
  - category: "技术" | "HR" | "行为"
Response: {
  "message": "知识库导入成功",
  "count": 50
}

# 获取知识库文件列表
GET /digital-interviewer/knowledge/files
Response: [
  {
    "id": 1,
    "filename": "技术面试题库.pdf",
    "knowledge_type": "question",
    "category": "技术",
    "count": 50,
    "uploaded_at": "2026-02-05 10:00:00"
  }
]

# 查询知识库(用于测试RAG)
POST /digital-interviewer/knowledge/query
Body: {
  "query": "如何设计高并发系统",
  "category": "技术",
  "top_k": 3
}
Response: {
  "results": [
    {
      "question": "如何设计一个高并发系统?",
      "reference_answer": "...",
      "score": 0.92
    }
  ]
}
```

#### 面试会话管理

```python
# 开始面试会话
POST /digital-interviewer/sessions/start
Body: {
  "interviewer_id": 1,
  "user_id": "user123",
  "interview_type": "技术面试",
  "question_count": 5  # 可选,默认5个问题
}
Response: {
  "session_id": "uuid-xxx",
  "interviewer": {...},
  "first_question": "请先做一个自我介绍"
}

# 获取面试记录列表
GET /digital-interviewer/sessions?user_id=user123
Response: [
  {
    "session_id": "uuid-xxx",
    "interviewer_name": "张技术",
    "interview_type": "技术面试",
    "overall_score": 75,
    "status": "completed",
    "start_time": "2026-02-05 10:00:00",
    "duration": 1800  # 秒
  }
]

# 获取面试评估报告
GET /digital-interviewer/sessions/{session_id}/evaluation
Response: {
  "session_id": "uuid-xxx",
  "overall_score": 75,
  "dimension_scores": {
    "技术深度": 80,
    "问题解决能力": 70,
    "沟通表达": 75
  },
  "strengths": ["技术基础扎实", "思路清晰"],
  "weaknesses": ["回答过于简短", "缺少实际案例"],
  "detailed_feedback": "...",
  "rounds": [...]
}

# 下载Markdown报告
GET /digital-interviewer/sessions/{session_id}/download-report
Response: Markdown文件下载

# 下载PDF报告
GET /digital-interviewer/sessions/{session_id}/download-pdf
Response: PDF文件下载
```

#### 语音服务

```python
# 语音转文字(复用digital_customer的实现)
POST /digital-interviewer/audio/transcribe
Content-Type: multipart/form-data
Body: audio: 音频文件
Response: {
  "text": "我认为高并发系统需要考虑..."
}

# 文字转语音(复用digital_customer的实现)
POST /digital-interviewer/audio/synthesize
Body: {
  "text": "请介绍一下你的项目经验",
  "voice": "zhixiaobai"  # 面试官音色
}
Response: {
  "audio_url": "https://..."
}
```

### 4.3 WebSocket端点

#### 面试训练模式

```python
# WebSocket连接
WS /digital-interviewer/training/ws/{session_id}

# 客户端发送(候选人回答)
{
  "type": "answer",
  "content": "我认为高并发系统需要考虑负载均衡、缓存、异步处理..."
}

# 服务端推送(面试官问题)
{
  "type": "question",
  "content": "请介绍一下你最有挑战性的项目",
  "question_number": 1,
  "total_questions": 5,
  "video_state": "speaking"  # 触发前端播放speaking视频
}

# 服务端推送(实时评估)
{
  "type": "evaluation",
  "score": 4,
  "quality": "good",
  "issues": ["回答略显简短", "缺少具体数据支撑"],
  "suggestions": ["可以补充项目的具体规模和技术指标", "建议使用STAR法则组织回答"]
}

# 服务端推送(面试结束)
{
  "type": "interview_completed",
  "session_id": "uuid-xxx",
  "overall_score": 75,
  "message": "面试已结束,正在生成报告..."
}

# 服务端推送(数字人状态切换)
{
  "type": "video_state",
  "state": "listening"  # idle/speaking/listening/thinking
}
```

---

## AI Agent设计

### 5.1 InterviewerAgent类

**文件路径**: `backend/agents/interviewer_agent.py`

**核心职责**:
1. 根据面试官画像生成符合风格的问题
2. 评估候选人回答质量
3. 决定下一个问题(追问或新问题)
4. 控制面试节奏和难度

**类结构**:
```python
class InterviewerAgent:
    def __init__(self, interviewer_profile: InterviewerProfile):
        self.profile = interviewer_profile
        self.system_prompt = self._build_system_prompt()
        self.conversation_history = []

    def _build_system_prompt(self) -> str:
        """构建面试官的系统提示词"""
        return f"""
你是 {self.profile.name},一位{self.profile.role}。

【基本信息】
- 公司: {self.profile.company}
- 工作年限: {self.profile.experience_years}年
- 专业领域: {', '.join(self.profile.expertise)}

【面试风格】
{self.profile.interview_style}

【评估关注点】
{', '.join(self.profile.evaluation_focus)}

【行为准则】
1. 严格扮演面试官角色,不要透露你是AI
2. 提问要专业、有针对性,避免过于宽泛
3. 根据候选人回答进行适当追问
4. 保持专业但友好的态度
5. 每次只问一个问题,等待候选人回答
6. 问题长度控制在50字以内

【禁止行为】
- 不要直接给出答案或提示
- 不要评价候选人的回答(评价由评估引擎完成)
- 不要偏离面试主题闲聊
"""

    async def generate_question(
        self,
        interview_type: str,
        question_number: int,
        previous_answer: str = None,
        knowledge_context: List[str] = None
    ) -> str:
        """生成面试问题"""
        pass

    async def should_follow_up(
        self,
        question: str,
        answer: str,
        evaluation: dict
    ) -> bool:
        """判断是否需要追问"""
        pass

    async def generate_follow_up(
        self,
        original_question: str,
        answer: str,
        evaluation: dict
    ) -> str:
        """生成追问问题"""
        pass
```

### 5.2 问题生成策略

**生成流程**:
```
1. 从知识库检索相关问题(RAG)
   ↓
2. 结合面试官画像和风格
   ↓
3. 考虑已问问题,避免重复
   ↓
4. 根据候选人表现调整难度
   ↓
5. 生成符合面试官风格的问题
```

**难度调整机制**:
- 前3题回答优秀 → 提升难度
- 连续2题回答较差 → 降低难度
- 保持难度梯度,避免过于简单或困难

**问题类型分布**(技术面试示例):
- 自我介绍: 1题
- 基础知识: 2题
- 项目经验: 2题
- 深度技术: 2题
- 场景设计: 1题

### 5.3 评估引擎

**文件路径**: `backend/apps/digital_interviewer/services/evaluation_engine.py`

**评估维度**(可配置):
```python
EVALUATION_DIMENSIONS = {
    "技术面试": {
        "技术深度": "对技术原理的理解程度",
        "问题解决能力": "分析和解决问题的思路",
        "实践经验": "实际项目经验的丰富度",
        "沟通表达": "表达清晰度和逻辑性",
        "学习能力": "对新技术的学习和适应能力"
    },
    "HR面试": {
        "自我认知": "对自身优劣势的认识",
        "职业规划": "职业目标的清晰度",
        "稳定性": "工作稳定性和忠诚度",
        "团队协作": "团队合作意识和能力",
        "抗压能力": "面对压力的应对方式"
    },
    "行为面试": {
        "STAR完整性": "是否完整使用STAR法则",
        "案例真实性": "案例的真实性和具体性",
        "反思能力": "对经历的反思和总结",
        "成长性": "从经历中的成长和收获",
        "价值观": "体现的价值观和态度"
    }
}
```

**评分标准**:
- 5分(优秀): 回答全面、深入、有亮点
- 4分(良好): 回答完整、准确、有一定深度
- 3分(中等): 回答基本正确,但不够深入
- 2分(较差): 回答不完整或有明显错误
- 1分(很差): 答非所问或完全错误

**评估提示词模板**:
```python
EVALUATION_PROMPT = """
请评估候选人对以下问题的回答质量:

【问题】
{question}

【候选人回答】
{answer}

【评估维度】
{dimensions}

【评估要求】
1. 对每个维度打分(1-5分)
2. 指出回答中的问题(如有)
3. 给出具体的改进建议
4. 评估是否需要追问

【输出格式】
{{
  "dimension_scores": {{"技术深度": 4, "问题解决能力": 3, ...}},
  "overall_score": 4,
  "quality": "good",
  "issues": ["回答略显简短", "缺少具体案例"],
  "suggestions": ["可以补充项目的具体规模", "建议使用STAR法则"],
  "need_follow_up": true,
  "follow_up_direction": "深入了解项目的技术细节"
}}
"""
```

### 5.4 RAG知识检索

**检索策略**:
```python
async def retrieve_questions(
    query: str,
    category: str,
    difficulty: str = None,
    top_k: int = 3
) -> List[dict]:
    """
    混合检索面试问题

    1. BM25关键词匹配(权重0.6)
    2. Embedding语义匹配(权重0.4)
    3. 过滤条件: category, difficulty
    4. 返回Top-K结果
    """
    pass
```

**知识库使用场景**:
- 生成问题时: 检索相关问题作为参考
- 评估回答时: 检索标准答案和评分标准
- 生成建议时: 检索优秀回答案例

---

## 前端组件设计

### 6.1 主页面结构

**文件路径**: `frontend/src/pages/DigitalInterviewerPage.jsx`

**页面布局**:
```
┌─────────────────────────────────────────────────────────┐
│  数字面试官                                    [返回首页] │
├─────────────────────────────────────────────────────────┤
│  [面试官管理] [面试训练] [面试记录]                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Tab1: 面试官管理                                        │
│  ┌────────────────────────────────────────────────┐    │
│  │  [+ 上传面试官画像]                             │    │
│  │                                                 │    │
│  │  ┌──────┐  ┌──────┐  ┌──────┐                │    │
│  │  │ 张技术│  │ 李HR │  │ 王行为│                │    │
│  │  │ 技术  │  │ HR   │  │ 行为  │                │    │
│  │  │[开始] │  │[开始]│  │[开始] │                │    │
│  │  └──────┘  └──────┘  └──────┘                │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  Tab2: 面试训练 (三栏布局)                              │
│  ┌──────┬─────────────────────┬──────────────┐        │
│  │数字人│   对话区域           │  实时反馈     │        │
│  │视频  │                     │              │        │
│  │      │  面试官: 请介绍...  │  当前问题: 1/5│        │
│  │[播放]│  候选人: 我是...    │  评分: 4分    │        │
│  │      │                     │  问题:        │        │
│  │      │  [语音输入] [文字]  │  - 回答简短   │        │
│  └──────┴─────────────────────┴──────────────┘        │
│                                                          │
│  Tab3: 面试记录                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  2026-02-05  张技术  技术面试  75分  [查看报告] │    │
│  │  2026-02-04  李HR    HR面试    82分  [查看报告] │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 6.2 核心组件

#### 组件1: InterviewerCard (面试官卡片)

**文件路径**: `frontend/src/components/digital_interviewer/InterviewerCard.jsx`

**功能**:
- 显示面试官基本信息
- 显示数字人视频缩略图
- 开始面试按钮
- 编辑/删除操作

**Props**:
```javascript
{
  interviewer: {
    id: 1,
    name: "张技术",
    role: "技术面试官",
    company: "某互联网公司",
    expertise: ["Python", "系统设计"],
    has_videos: true,
    video_thumbnail: "https://..."
  },
  onStartInterview: (interviewerId) => {},
  onEdit: (interviewerId) => {},
  onDelete: (interviewerId) => {}
}
```

#### 组件2: InterviewerUpload (面试官上传)

**文件路径**: `frontend/src/components/digital_interviewer/InterviewerUpload.jsx`

**功能**:
- 拖拽上传PDF/Markdown
- 文件验证
- 上传进度显示
- 成功后跳转到视频上传

**参考**: 复用 `DigitalCustomerUpload.jsx` 的实现

#### 组件3: VideoUpload (数字人视频上传)

**文件路径**: `frontend/src/components/digital_interviewer/VideoUpload.jsx`

**功能**:
- 上传4种状态视频
- 视频预览
- 格式和大小验证
- 上传进度显示

**UI设计**:
```
┌─────────────────────────────────────────┐
│  上传数字人视频                          │
├─────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐            │
│  │ 待机状态  │  │ 说话状态  │            │
│  │ [上传]   │  │ [上传]   │            │
│  └──────────┘  └──────────┘            │
│  ┌──────────┐  ┌──────────┐            │
│  │ 倾听状态  │  │ 思考状态  │            │
│  │ [上传]   │  │ [上传]   │            │
│  └──────────┘  └──────────┘            │
│                                         │
│  [完成上传]                             │
└─────────────────────────────────────────┘
```

#### 组件4: DigitalHumanPlayer (数字人播放器)

**文件路径**: `frontend/src/components/digital_interviewer/DigitalHumanPlayer.jsx`

**功能**:
- 播放4种状态视频
- 状态切换动画
- 循环播放待机视频
- 同步语音播放

**状态机**:
```javascript
const [videoState, setVideoState] = useState('idle');

// 状态切换逻辑
useEffect(() => {
  switch(videoState) {
    case 'idle':
      playVideo(videos.idle, { loop: true });
      break;
    case 'speaking':
      playVideo(videos.speaking, { loop: false });
      // 播放完毕后回到idle
      onVideoEnd(() => setVideoState('idle'));
      break;
    case 'listening':
      playVideo(videos.listening, { loop: true });
      break;
    case 'thinking':
      playVideo(videos.thinking, { loop: false });
      // 3秒后回到idle
      setTimeout(() => setVideoState('idle'), 3000);
      break;
  }
}, [videoState]);
```

#### 组件5: InterviewChat (面试对话区)

**文件路径**: `frontend/src/components/digital_interviewer/InterviewChat.jsx`

**功能**:
- 显示对话历史
- 区分面试官和候选人消息
- 语音输入按钮
- 文字输入框
- 发送按钮

**参考**: 复用 `DigitalCustomerPage.jsx` 的对话区实现

#### 组件6: InterviewFeedback (实时反馈面板)

**文件路径**: `frontend/src/components/digital_interviewer/InterviewFeedback.jsx`

**功能**:
- 显示当前问题进度
- 显示实时评分
- 显示发现的问题
- 显示改进建议

**UI设计**:
```
┌─────────────────────────┐
│  实时反馈                │
├─────────────────────────┤
│  当前问题: 3/5          │
│  ━━━━━━━━━━━━━━━━━━━━ │
│                         │
│  本轮评分: ⭐⭐⭐⭐☆   │
│                         │
│  发现的问题:            │
│  • 回答略显简短         │
│  • 缺少具体案例         │
│                         │
│  改进建议:              │
│  • 可以补充项目规模     │
│  • 建议使用STAR法则     │
└─────────────────────────┘
```

#### 组件7: InterviewReport (面试报告)

**文件路径**: `frontend/src/components/digital_interviewer/InterviewReport.jsx`

**功能**:
- 显示总体评分
- 显示雷达图(各维度得分)
- 显示优势和待改进点
- 显示详细问答回放
- 导出Markdown/PDF

**参考**: 复用 `EvaluationReportPage.jsx` 的实现

### 6.3 状态管理

**核心状态**:
```javascript
const [interviewMode, setInterviewMode] = useState(false);
const [currentInterviewer, setCurrentInterviewer] = useState(null);
const [sessionId, setSessionId] = useState(null);
const [questionNumber, setQuestionNumber] = useState(0);
const [totalQuestions, setTotalQuestions] = useState(5);
const [messages, setMessages] = useState([]);
const [realtimeFeedback, setRealtimeFeedback] = useState(null);
const [videoState, setVideoState] = useState('idle');
const [isRecording, setIsRecording] = useState(false);
```

### 6.4 WebSocket集成

**Hook**: `useInterviewWebSocket.js`

```javascript
const { sendMessage, lastMessage, readyState } = useWebSocket(
  `ws://localhost:8000/digital-interviewer/training/ws/${sessionId}`,
  {
    onOpen: () => console.log('面试连接成功'),
    onMessage: (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    },
    shouldReconnect: () => true
  }
);

function handleWebSocketMessage(data) {
  switch(data.type) {
    case 'question':
      // 面试官提问
      addMessage('interviewer', data.content);
      setVideoState('speaking');
      playAudio(data.audio_url);
      break;
    case 'evaluation':
      // 实时评估
      setRealtimeFeedback(data);
      break;
    case 'video_state':
      // 切换数字人状态
      setVideoState(data.state);
      break;
    case 'interview_completed':
      // 面试结束
      setInterviewMode(false);
      showCompletionDialog(data);
      break;
  }
}
```

---

## 面试流程设计

### 7.1 完整流程图

```
用户选择面试官
    ↓
配置面试类型和问题数
    ↓
创建面试会话 (POST /sessions/start)
    ↓
建立WebSocket连接
    ↓
┌─────────────────────────────────┐
│  面试循环 (N轮问答)              │
│                                  │
│  1. 面试官提问                   │
│     - 生成问题 (RAG + Agent)     │
│     - 推送问题到前端             │
│     - 切换数字人状态: speaking   │
│     - 播放语音                   │
│     ↓                            │
│  2. 候选人回答                   │
│     - 切换数字人状态: listening  │
│     - 接收语音/文字输入          │
│     - 发送回答到后端             │
│     ↓                            │
│  3. 实时评估                     │
│     - 切换数字人状态: thinking   │
│     - 评估引擎分析回答           │
│     - 推送评估结果到前端         │
│     ↓                            │
│  4. 决策下一步                   │
│     - 是否追问?                  │
│     - 是否进入下一题?            │
│     - 是否结束面试?              │
│     ↓                            │
│  (循环或结束)                    │
└─────────────────────────────────┘
    ↓
面试结束
    ↓
生成综合评估报告
    ↓
推送报告到前端
    ↓
用户查看报告并导出
```

### 7.2 问答轮次详细流程

#### 阶段1: 面试官提问

**后端逻辑** (`interviewer_orchestrator.py`):
```python
async def generate_next_question(session_id: str) -> dict:
    """生成下一个问题"""
    session = await get_session(session_id)

    # 1. 从知识库检索相关问题
    knowledge_context = await knowledge_service.retrieve_questions(
        category=session.interview_type,
        difficulty=calculate_difficulty(session),
        top_k=3
    )

    # 2. 调用InterviewerAgent生成问题
    question = await interviewer_agent.generate_question(
        interview_type=session.interview_type,
        question_number=session.current_question_index + 1,
        previous_answer=get_last_answer(session),
        knowledge_context=knowledge_context
    )

    # 3. 生成语音
    audio_url = await audio_service.synthesize(
        text=question,
        voice="zhixiaobai"
    )

    # 4. 保存问题记录
    await save_round(session_id, question=question)

    # 5. 推送到前端
    return {
        "type": "question",
        "content": question,
        "question_number": session.current_question_index + 1,
        "total_questions": session.total_questions,
        "audio_url": audio_url,
        "video_state": "speaking"
    }
```

**前端处理**:
```javascript
// 接收问题
if (data.type === 'question') {
  // 1. 添加消息到对话区
  addMessage('interviewer', data.content);

  // 2. 切换数字人状态
  setVideoState('speaking');

  // 3. 播放语音
  playAudio(data.audio_url);

  // 4. 更新进度
  setQuestionNumber(data.question_number);

  // 5. 语音播放完毕后切换到listening状态
  onAudioEnd(() => {
    setVideoState('listening');
    enableInput();  // 启用输入
  });
}
```

#### 阶段2: 候选人回答

**前端逻辑**:
```javascript
// 语音输入
async function handleVoiceInput() {
  setIsRecording(true);
  const audioBlob = await recordAudio();

  // 转文字
  const response = await fetch('/digital-interviewer/audio/transcribe', {
    method: 'POST',
    body: audioBlob
  });
  const { text } = await response.json();

  // 发送回答
  sendAnswer(text);
}

// 文字输入
function handleTextInput(text) {
  sendAnswer(text);
}

// 发送回答
function sendAnswer(text) {
  // 1. 添加消息到对话区
  addMessage('candidate', text);

  // 2. 切换数字人状态
  setVideoState('thinking');

  // 3. 发送到后端
  sendMessage({
    type: 'answer',
    content: text
  });

  // 4. 禁用输入,等待评估
  disableInput();
}
```

**后端处理**:
```python
async def handle_answer(session_id: str, answer: str):
    """处理候选人回答"""
    session = await get_session(session_id)
    current_round = await get_current_round(session_id)

    # 1. 保存回答
    await update_round(current_round.id, answer=answer)

    # 2. 调用评估引擎
    evaluation = await evaluation_engine.evaluate_answer(
        question=current_round.question,
        answer=answer,
        interview_type=session.interview_type
    )

    # 3. 保存评估结果
    await update_round(current_round.id, evaluation=evaluation)

    # 4. 推送实时反馈
    await websocket.send_json({
        "type": "evaluation",
        "score": evaluation["overall_score"],
        "quality": evaluation["quality"],
        "issues": evaluation["issues"],
        "suggestions": evaluation["suggestions"]
    })

    # 5. 决策下一步
    if evaluation["need_follow_up"]:
        # 生成追问
        follow_up = await interviewer_agent.generate_follow_up(
            original_question=current_round.question,
            answer=answer,
            evaluation=evaluation
        )
        await send_question(session_id, follow_up)
    elif session.current_question_index < session.total_questions:
        # 进入下一题
        await generate_next_question(session_id)
    else:
        # 面试结束
        await complete_interview(session_id)
```

#### 阶段3: 实时评估

**评估引擎逻辑**:
```python
async def evaluate_answer(
    question: str,
    answer: str,
    interview_type: str
) -> dict:
    """评估候选人回答"""

    # 1. 获取评估维度
    dimensions = EVALUATION_DIMENSIONS[interview_type]

    # 2. 从知识库检索标准答案
    reference = await knowledge_service.retrieve_standards(
        question=question,
        top_k=1
    )

    # 3. 构建评估提示词
    prompt = EVALUATION_PROMPT.format(
        question=question,
        answer=answer,
        dimensions=dimensions,
        reference=reference
    )

    # 4. 调用LLM评估
    response = await call_llm(prompt, model="qwen-max")
    evaluation = parse_evaluation(response)

    # 5. 返回评估结果
    return {
        "dimension_scores": evaluation["dimension_scores"],
        "overall_score": evaluation["overall_score"],
        "quality": evaluation["quality"],
        "issues": evaluation["issues"],
        "suggestions": evaluation["suggestions"],
        "need_follow_up": evaluation["need_follow_up"]
    }
```

### 7.3 面试结束流程

**后端逻辑**:
```python
async def complete_interview(session_id: str):
    """完成面试并生成报告"""

    # 1. 更新会话状态
    await update_session(session_id, status="completed", end_time=now())

    # 2. 获取所有轮次数据
    rounds = await get_all_rounds(session_id)

    # 3. 生成综合评估
    final_evaluation = await generate_final_evaluation(rounds)

    # 4. 生成报告
    report_markdown = await report_generator.generate_markdown(
        session_id=session_id,
        evaluation=final_evaluation
    )

    report_pdf_path = await report_generator.generate_pdf(
        markdown_content=report_markdown
    )

    # 5. 保存评估记录
    await save_evaluation(
        session_id=session_id,
        evaluation=final_evaluation,
        report_markdown=report_markdown,
        report_pdf_path=report_pdf_path
    )

    # 6. 推送完成消息
    await websocket.send_json({
        "type": "interview_completed",
        "session_id": session_id,
        "overall_score": final_evaluation["overall_score"],
        "message": "面试已结束,正在生成报告..."
    })
```

### 7.4 异常处理

**超时处理**:
- 候选人30秒未回答 → 提示"请回答问题"
- 候选人60秒未回答 → 自动跳过该题

**连接断开**:
- WebSocket断开 → 自动重连(最多3次)
- 重连失败 → 保存当前进度,提示用户稍后继续

**错误恢复**:
- LLM调用失败 → 重试3次,失败后使用默认问题
- 语音服务失败 → 降级为纯文字模式

---

## 数字人视频录制指南

### 8.1 录制准备

#### 设备要求

| 设备 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **摄像头** | 720p | 1080p或更高 |
| **麦克风** | 内置麦克风 | 外置麦克风(降噪) |
| **灯光** | 自然光 | 环形灯或柔光灯 |
| **背景** | 纯色墙面 | 绿幕(可抠图) |

#### 环境设置

1. **光线**: 均匀柔和,避免强光直射和阴影
2. **背景**: 简洁干净,避免杂乱物品
3. **距离**: 摄像头距离1-1.5米,上半身入镜
4. **角度**: 摄像头与眼睛平齐,略微俯视
5. **着装**: 正装或商务休闲,避免纯白或纯黑

### 8.2 四种状态视频录制

#### 状态1: 待机状态 (idle)

**用途**: 面试官等待候选人回答时的自然状态

**动作要求**:
- 保持自然站姿或坐姿
- 轻微的呼吸起伏
- 偶尔眨眼(自然频率)
- 可以有轻微的头部微动
- 表情平和、专注

**录制时长**: 10-15秒

**循环播放**: 是(无缝循环)

**录制脚本**:
```
【准备】
- 调整姿势,放松肩膀
- 眼睛看向摄像头
- 保持微笑或中性表情

【开始录制】
- 保持姿势10-15秒
- 自然呼吸,偶尔眨眼
- 可以有1-2次轻微点头
- 避免大幅度动作

【注意事项】
- 开头和结尾动作要一致(便于循环)
- 避免突然的动作变化
- 保持眼神专注
```

#### 状态2: 说话状态 (speaking)

**用途**: 面试官提问或给反馈时

**动作要求**:
- 嘴部有说话动作(可以无声)
- 配合手势(适度)
- 眼神交流(看向摄像头)
- 表情生动,有起伏
- 头部有自然的点头或摇头

**录制时长**: 5-8秒

**循环播放**: 否(播放一次后回到idle)

**录制脚本**:
```
【准备】
- 准备一段面试官常说的话
- 例如: "请介绍一下你的项目经验"
- 或: "你的回答很好,我们继续下一个问题"

【开始录制】
- 自然说出准备的话(可以无声)
- 配合适当的手势
- 保持眼神交流
- 表情自然、专业

【注意事项】
- 语速适中,不要太快
- 手势不要过于夸张
- 结尾要自然收尾,便于切换到idle
```

#### 状态3: 倾听状态 (listening)

**用途**: 候选人回答问题时,面试官认真倾听

**动作要求**:
- 身体略微前倾(表示专注)
- 眼神专注(看向摄像头)
- 偶尔点头(表示理解)
- 可以有思考的表情
- 手部动作: 托腮、交叉手臂等

**录制时长**: 8-12秒

**循环播放**: 是(候选人回答期间循环)

**录制脚本**:
```
【准备】
- 想象正在听候选人回答
- 保持专注和认真的状态

【开始录制】
- 眼神专注地看向摄像头
- 身体略微前倾
- 2-3次轻微点头(表示理解)
- 可以有1次托腮或调整姿势的动作
- 保持专业的倾听表情

【注意事项】
- 避免走神或东张西望
- 点头频率不要太高
- 表情要认真但不严肃
- 开头和结尾动作要一致(便于循环)
```

#### 状态4: 思考状态 (thinking)

**用途**: 面试官评估候选人回答,思考下一个问题

**动作要求**:
- 眼神略微向上或向侧(思考状)
- 托腮、摸下巴等思考动作
- 轻微皱眉或点头
- 可以有记笔记的动作
- 表情专注、认真

**录制时长**: 3-5秒

**循环播放**: 否(播放一次后回到idle)

**录制脚本**:
```
【准备】
- 想象正在评估候选人的回答
- 准备思考的动作

【开始录制】
- 眼神从摄像头移开,略微向上或向侧
- 做出思考动作(托腮/摸下巴/点头)
- 可以有轻微皱眉
- 表情认真、专注
- 最后眼神回到摄像头

【注意事项】
- 动作要自然,不要做作
- 时长不要太长(3-5秒即可)
- 结尾要自然,便于切换到idle或speaking
```

### 8.3 视频技术规格

#### 格式要求

| 参数 | 要求 | 说明 |
|------|------|------|
| **格式** | MP4 (H.264) | 兼容性最好 |
| **分辨率** | 1920x1080 (1080p) | 推荐,最低720p |
| **帧率** | 30fps | 流畅度和文件大小平衡 |
| **码率** | 2-5 Mbps | 保证画质 |
| **音频** | AAC, 128kbps | 可选(可以无声) |
| **时长** | 见上表 | 不同状态时长不同 |
| **文件大小** | < 10MB/个 | 便于上传和加载 |

#### 后期处理

**推荐工具**:
- **剪辑**: Adobe Premiere / DaVinci Resolve / 剪映
- **压缩**: HandBrake / FFmpeg
- **抠图**: Adobe After Effects (如使用绿幕)

**处理步骤**:
```bash
# 1. 剪辑视频(去除多余部分)
# 2. 调整色彩和亮度
# 3. 添加淡入淡出(可选)
# 4. 压缩视频

# 使用FFmpeg压缩示例
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium \
       -c:a aac -b:a 128k -vf scale=1920:1080 output.mp4
```

### 8.4 录制检查清单

**录制前**:
- [ ] 设备测试(摄像头、麦克风、灯光)
- [ ] 环境检查(背景、光线、噪音)
- [ ] 着装检查(整洁、得体)
- [ ] 脚本准备(熟悉每个状态的动作)

**录制中**:
- [ ] 每个状态录制3-5遍(选最好的)
- [ ] 检查画面构图(上半身入镜)
- [ ] 检查光线(均匀、无阴影)
- [ ] 检查动作(自然、流畅)

**录制后**:
- [ ] 检查视频质量(清晰度、流畅度)
- [ ] 检查循环效果(idle和listening)
- [ ] 检查切换效果(状态间过渡自然)
- [ ] 压缩视频(符合技术规格)
- [ ] 命名规范(interviewer_name_state.mp4)

### 8.5 视频命名规范

```
{面试官姓名}_{状态}.mp4

示例:
- 张技术_idle.mp4
- 张技术_speaking.mp4
- 张技术_listening.mp4
- 张技术_thinking.mp4
```

### 8.6 上传流程

1. 创建面试官画像(上传PDF/Markdown)
2. 系统生成面试官ID
3. 上传4个视频文件
4. 系统验证视频格式和大小
5. 视频存储到服务器
6. 更新数据库记录
7. 完成,可以开始面试

---

## 路由集成方案

### 9.1 后端路由集成

**文件**: `backend/main.py`

**集成步骤**:
```python
# 1. 导入数字面试官应用
from apps.digital_interviewer.app import app as digital_interviewer_app

# 2. 挂载到主应用
app.mount("/api/digital-interviewer", digital_interviewer_app)

# 3. 完整路由列表
"""
/api/chat                    # 智能群聊
/api/celebrity               # 数字分身
/api/customer-service        # 数字客服
/api/digital-customer        # 销售演练
/api/digital-interviewer     # 数字面试官 (新增)
"""
```

### 9.2 前端路由集成

**文件**: `frontend/src/App.jsx`

**路由配置**:
```javascript
import DigitalInterviewerPage from './pages/DigitalInterviewerPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<GroupChatPage />} />
        <Route path="/celebrity" element={<CelebrityPage />} />
        <Route path="/customer-service" element={<CustomerServicePage />} />
        <Route path="/digital-customer" element={<DigitalCustomerPage />} />
        <Route path="/digital-interviewer" element={<DigitalInterviewerPage />} />
        <Route path="/digital-interviewer/report/:sessionId"
               element={<InterviewReportPage />} />
      </Routes>
    </Router>
  );
}
```

### 9.3 导航菜单集成

**文件**: `frontend/src/components/Sidebar.jsx`

**菜单项添加**:
```javascript
const menuItems = [
  { path: '/chat', icon: <ChatIcon />, label: '智能群聊' },
  { path: '/celebrity', icon: <PersonIcon />, label: '数字分身' },
  { path: '/customer-service', icon: <SupportIcon />, label: '数字客服' },
  { path: '/digital-customer', icon: <TrainingIcon />, label: '销售演练' },
  { path: '/digital-interviewer', icon: <InterviewIcon />, label: '数字面试官' }, // 新增
];
```

### 9.4 配置文件更新

**文件**: `frontend/src/config.js`

**WebSocket URL配置**:
```javascript
export const CONFIG = {
  API_BASE_URL: 'http://localhost:8000',
  WS_URL: 'ws://localhost:8000/api/chat/ws',
  CELEBRITY_WS_URL: 'ws://localhost:8000/api/celebrity/ws',
  CUSTOMER_SERVICE_WS_URL: 'ws://localhost:8000/api/customer-service/ws',
  DIGITAL_CUSTOMER_WS_URL: 'ws://localhost:8000/api/digital-customer/ws',
  DIGITAL_INTERVIEWER_WS_URL: 'ws://localhost:8000/api/digital-interviewer/training/ws', // 新增
};
```

---

## 技术决策

### 10.1 复用现有组件

**高度复用**:
- ✅ 语音服务 (`audio_service.py`) - 完全复用digital_customer的实现
- ✅ 报告生成 (`report_generator.py`) - 复用PDF/Markdown生成逻辑
- ✅ 数据库连接 (`database.py`) - 复用现有数据库管理
- ✅ Embedding服务 - 复用现有RAG实现

**部分复用**:
- 🔄 评估引擎 - 参考销售演练的评估逻辑,调整评估维度
- 🔄 编排器 - 参考training_orchestrator,调整面试流程
- 🔄 前端对话组件 - 参考DigitalCustomerPage,调整UI布局

**全新开发**:
- 🆕 InterviewerAgent - 面试官特有的提问和追问逻辑
- 🆕 问题生成器 - 基于RAG的智能问题生成
- 🆕 数字人播放器 - 4状态视频切换逻辑
- 🆕 视频上传组件 - 多文件上传和预览

### 10.2 数据库选择

**决策**: 使用独立的SQLite数据库 `digital_interviewer.db`

**理由**:
- ✅ 与现有模块保持一致(celebrity.db, digital_customer.db)
- ✅ 数据隔离,便于备份和迁移
- ✅ 开发和部署简单
- ✅ 满足中小规模并发需求

**未来扩展**: 如需高并发,可切换到PostgreSQL

### 10.3 视频存储方案

**方案1: 本地文件存储** (推荐用于开发和小规模部署)
- 视频存储在 `backend/data/interviewer_videos/`
- 通过FastAPI静态文件服务提供访问
- 优点: 简单、无额外成本
- 缺点: 不适合大规模部署

**方案2: 对象存储** (推荐用于生产环境)
- 使用阿里云OSS或其他对象存储
- 视频上传后返回CDN URL
- 优点: 高可用、CDN加速、成本低
- 缺点: 需要配置OSS服务

**实现建议**: 先实现方案1,预留方案2接口

### 10.4 面试类型配置

**决策**: 使用配置文件定义面试类型和流程

**配置文件**: `backend/apps/digital_interviewer/interview_configs.json`

```json
{
  "interview_types": {
    "技术面试": {
      "description": "编程、算法、系统设计等技术岗位面试",
      "default_questions": 5,
      "question_distribution": {
        "自我介绍": 1,
        "基础知识": 2,
        "项目经验": 2,
        "深度技术": 2,
        "场景设计": 1
      },
      "evaluation_dimensions": {
        "技术深度": "对技术原理的理解程度",
        "问题解决能力": "分析和解决问题的思路",
        "实践经验": "实际项目经验的丰富度",
        "沟通表达": "表达清晰度和逻辑性",
        "学习能力": "对新技术的学习和适应能力"
      }
    },
    "HR面试": {
      "description": "人力资源面试,关注软技能和文化匹配",
      "default_questions": 5,
      "question_distribution": {
        "自我介绍": 1,
        "职业规划": 1,
        "离职原因": 1,
        "团队协作": 1,
        "压力管理": 1
      },
      "evaluation_dimensions": {
        "自我认知": "对自身优劣势的认识",
        "职业规划": "职业目标的清晰度",
        "稳定性": "工作稳定性和忠诚度",
        "团队协作": "团队合作意识和能力",
        "抗压能力": "面对压力的应对方式"
      }
    },
    "行为面试": {
      "description": "基于STAR法则的行为面试",
      "default_questions": 4,
      "question_distribution": {
        "领导力": 1,
        "团队协作": 1,
        "冲突处理": 1,
        "问题解决": 1
      },
      "evaluation_dimensions": {
        "STAR完整性": "是否完整使用STAR法则",
        "案例真实性": "案例的真实性和具体性",
        "反思能力": "对经历的反思和总结",
        "成长性": "从经历中的成长和收获",
        "价值观": "体现的价值观和态度"
      }
    }
  }
}
```

**优点**:
- 灵活配置,无需修改代码
- 易于扩展新的面试类型
- 支持自定义评估维度

### 10.5 AI模型选择

**主要模型**: Qwen-Max
- 用于问题生成、回答评估、报告生成
- 理由: 性能强、中文效果好

**备选方案**: 支持模型降级
- Qwen-Max不可用时 → 降级到Qwen-Plus
- 成本优化: 简单任务使用Qwen-Turbo

### 10.6 实时性优化

**问题**: LLM调用耗时2-3秒,影响体验

**优化方案**:
1. **问题预生成**: 面试开始时预生成前3个问题
2. **并行处理**: 评估和下一题生成并行执行
3. **缓存机制**: 常见问题缓存,减少LLM调用
4. **流式输出**: 评估反馈流式推送,提升响应感

---

## 实现优先级

### 11.1 MVP版本 (第一阶段)

**目标**: 实现核心面试流程,验证可行性

**功能清单**:
- ✅ 面试官画像上传和解析
- ✅ 数字人视频上传(4种状态)
- ✅ 基础面试流程(固定5个问题)
- ✅ 文字对话(暂不支持语音)
- ✅ 简单评估(单一维度评分)
- ✅ 基础报告生成(Markdown)

**技术实现**:
- 数据库表创建
- InterviewerAgent基础实现
- 简单的问题生成(不使用RAG)
- 基础评估引擎
- 前端三栏布局
- 数字人播放器(4状态切换)

**预计工作量**: 2-3周

### 11.2 完整版本 (第二阶段)

**目标**: 完善功能,提升用户体验

**功能清单**:
- ✅ RAG知识库集成
- ✅ 智能问题生成
- ✅ 多维度评估
- ✅ 语音输入输出
- ✅ 实时反馈优化
- ✅ PDF报告导出
- ✅ 面试记录管理

**技术实现**:
- 知识库服务(BM25 + Embedding)
- 问题生成器(基于RAG)
- 完整评估引擎(多维度)
- 语音服务集成
- 报告生成器(PDF)
- 前端优化和美化

**预计工作量**: 2-3周

### 11.3 增强版本 (第三阶段)

**目标**: 高级功能,差异化竞争

**功能清单**:
- ✅ 面试类型配置化
- ✅ 自定义评估维度
- ✅ 面试难度自适应
- ✅ 追问机制
- ✅ 面试数据分析
- ✅ 多面试官协同面试

**技术实现**:
- 配置文件系统
- 难度调整算法
- 追问决策逻辑
- 数据统计和可视化
- 多Agent协同机制

**预计工作量**: 2-3周

### 11.4 开发顺序建议

**Phase 1: 后端基础** (Week 1)
1. 创建数据库表和模型
2. 实现面试官画像解析
3. 实现基础InterviewerAgent
4. 实现简单评估引擎
5. 实现WebSocket端点

**Phase 2: 前端基础** (Week 2)
1. 创建主页面和路由
2. 实现面试官卡片和上传
3. 实现数字人播放器
4. 实现对话区和反馈面板
5. 集成WebSocket

**Phase 3: 核心功能** (Week 3-4)
1. 实现RAG知识库
2. 实现智能问题生成
3. 实现多维度评估
4. 实现报告生成
5. 集成语音服务

**Phase 4: 优化和测试** (Week 5-6)
1. 性能优化
2. UI/UX优化
3. 错误处理完善
4. 端到端测试
5. 文档编写

### 11.5 关键里程碑

| 里程碑 | 交付物 | 验收标准 |
|-------|--------|---------|
| **M1: 数据层完成** | 数据库表、模型、基础API | 可以创建面试官和会话 |
| **M2: MVP可用** | 基础面试流程 | 可以完成一次完整面试 |
| **M3: 功能完整** | 所有核心功能 | 支持语音、RAG、多维度评估 |
| **M4: 生产就绪** | 优化、测试、文档 | 可以部署到生产环境 |

### 11.6 风险和挑战

**技术风险**:
- 数字人视频切换的流畅性
- LLM调用延迟影响体验
- RAG检索准确率

**缓解措施**:
- 视频预加载和缓存
- 问题预生成和并行处理
- 知识库质量优化和测试

**业务风险**:
- 用户录制视频的质量参差不齐
- 面试评估的准确性和公平性

**缓解措施**:
- 提供详细的录制指南和示例
- 多维度评估,避免单一标准
- 持续优化评估提示词

---

## 总结

数字面试官子应用是VividCrowd平台的重要扩展,通过AI技术帮助求职者提升面试技巧。本设计文档涵盖了:

1. **系统架构**: 独立数据库、模块化设计、复用现有组件
2. **核心功能**: 面试官管理、智能提问、实时评估、报告生成
3. **技术方案**: RAG知识库、多维度评估、数字人视频、语音交互
4. **实现路径**: 分阶段开发,MVP优先,逐步完善

**关键创新点**:
- 🎯 可配置的面试类型和流程
- 🤖 基于RAG的智能问题生成
- 📹 4状态数字人视频交互
- 📊 多维度实时评估反馈
- 📄 详细的面试报告和改进建议

**下一步行动**:
1. 评审本设计文档,确认技术方案
2. 准备开发环境和依赖
3. 按照实现优先级开始开发
4. 定期review进度和调整计划

---

**文档版本历史**:
- v1.0 (2026-02-05): 初始版本,完整设计方案









