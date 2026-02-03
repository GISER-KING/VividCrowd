# VividCrowd

> **基于 LLM 的高仿真沉浸式拟人群聊环境 + AI 数字分身智库 + 智能客服系统**

https://github.com/user-attachments/assets/26936c51-f9d9-4590-896c-8e093f7a41ff

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)

[English Version](README_EN.md)

---

## 📖 项目简介

**VividCrowd** 是一个多模态 AI 对话平台，提供四种独特的交互体验：

| 模式 | 描述 | 特点 |
|------|------|------|
| **智能群聊** | 你是唯一的真人，与多个 AI Agent 组成的虚拟群聊 | 深度拟人化、混合路由、防穿帮 |
| **数字分身** | 上传 PDF 创建名人/书籍/课程的 AI 数字分身 | 知识提取、私聊/群聊、数字人视频 |
| **数字客服** | 基于知识库的智能客服系统 | BM25+Embedding 混合匹配、置信度分层、话术控制 |
| **销售演练** | 模拟真实客户进行销售全流程实战演练 | 5阶段流程、实时评价、AI助手、雷达图分析 |

与传统的"一问一答"机器人不同，本项目通过复杂的**编排算法**和**拟人化策略**，模拟了真实的社交直觉和专业服务体验。

---

## 🌟 核心功能

### 一、智能群聊 (Group Chat)

#### 1.1 深度拟人化 Agent

每个群友都基于 `agents_profiles.json` 定义，拥有独立的灵魂：

```json
{
  "id": "xiaolin",
  "name": "小林",
  "age": 22,
  "occupation": "中医院校学生",
  "personality_traits": ["热心", "话痨", "有点迷信"],
  "interests": ["舌诊", "养生茶", "节气食疗"],
  "speech_style": "用'姐妹''宝子'称呼别人，爱发波浪号～"
}
```

**核心特性：**

| 特性 | 说明 |
|------|------|
| **严格人设模式** | Agent 严格遵守人设，中医学生不会回答 Python 问题 |
| **反 AI 指令注入** | System Prompt 强制忘记 AI 身份，使用口语化表达 |
| **每日消息限制** | 每个 Agent 每天最多发 10 条，模拟真人活跃度 |
| **领域拒答** | 超出专业领域的问题会说"这题超纲了" |

#### 1.2 智能混合路由架构

采用 **Fast & Slow** 双路径分发机制：

```
用户消息
    │
    ▼
┌─────────────────────────────────────┐
│  ⚡ Fast Path (规则层 - 毫秒级)      │
│  ├─ 显式提及: @张遥 → 直接锁定       │
│  └─ 焦点保持: 上一轮发言者优先回复   │
└─────────────────────────────────────┘
    │ (未命中)
    ▼
┌─────────────────────────────────────┐
│  🐢 Slow Path (语义层 - 秒级)        │
│  └─ LLM Router (Qwen-Turbo) 分析意图│
│     "谁能帮我看个代码？" → 张遥      │
└─────────────────────────────────────┘
    │ (未命中)
    ▼
┌─────────────────────────────────────┐
│  🎲 随机补位 (30%概率触发闲聊)       │
│  └─ 深夜模式自动降低活跃度           │
└─────────────────────────────────────┘
```

#### 1.3 真实群聊体验

| 特性 | 实现方式 |
|------|---------|
| **后台并发，前台串行** | 多 Agent 同时思考，但通过队列串行发言 |
| **输入状态模拟** | 显示"xxx 正在输入..."，完整消息一次弹出 |
| **智能去重** | 自动检测复读机行为，掐断无效回复 |
| **深夜模式** | 23:00-07:00 活跃度降至 20%，最多 1 人回复 |
| **打字延迟** | 8-10 秒模拟真人思考时间 |

#### 1.4 多重安全围栏

```python
# 三层防护机制
第1层: 正则匹配 (毫秒级)
  - 关键词: "扮演", "你是AI吗", "机器人"
  - 模式: r"^(如果|假如)你是.*"

第2层: 上下文分析
  - 检测连续追问个人隐私

第3层: LLM意图识别 (10%采样)
  - 精准识别破防企图
```

**防穿帮响应示例：**
```
用户: 你是AI吗？
小林: 啊？你在逗我玩吗～别整这些奇奇怪怪的啦！
```

---

### 二、数字分身智库 (Digital Twins)

#### 2.1 PDF 智能解析

支持三种知识源类型：

| 类型 | 适用场景 | 提取内容 |
|------|---------|---------|
| **人物 (Person)** | 名人传记、人物介绍 | 姓名、生卒年、国籍、职业、性格、语录 |
| **书籍 (Book)** | 经典著作、学术书籍 | 作者、核心观点、名言金句、表达风格 |
| **课程 (Topic)** | 课程讲义、专题资料 | 讲师、核心概念、知识点 |

**解析流程：**

```
PDF上传
    │
    ▼
1. PyMuPDF 提取文本
    │
    ▼
2. LLM 结构化解析 (Qwen)
   {
     "name": "爱因斯坦",
     "occupation": "理论物理学家",
     "famous_quotes": "想象力比知识更重要...",
     "speech_style": "深邃、善于比喻"
   }
    │
    ▼
3. 自动生成 System Prompt
    │
    ▼
4. 存储至数据库
```

#### 2.2 多模态交互体验

| 模态 | 技术实现 | 说明 |
|------|---------|------|
| **语音 (Audio)** | DashScope Paraformer-Realtime | 实时语音识别与合成，支持自然语音对话 |
| **视频 (Video)** | 火山引擎 (Volcano Engine) | 单图音频驱动技术，让静态照片"开口说话" |

#### 2.3 双模式对话

| 模式 | 特点 | 回复长度 |
|------|------|---------|
| **私聊 (Private)** | 一对一深度对话 | 100-200 字 |
| **群聊 (Group)** | 多人思想碰撞，智囊团讨论 | 50 字以内 |

**群聊模式示例：**
```
用户: 如何看待人工智能的未来？

爱因斯坦: 技术本身是中性的，关键在于人类如何运用它...
孔子: 工欲善其事，必先利其器。然而，器之善恶，在于用者之心...
乔布斯: 技术和人文的交汇点，才是真正的创新所在...
```

#### 2.4 知识检索增强

```python
# BM25 + Embedding 混合检索
1. PDF原文智能分块（ChunkingService）
2. 生成 Embedding 向量存储
3. BM25 关键词匹配 + Embedding 语义匹配
4. 混合评分排序
5. Top-K 段落注入 Prompt
6. 回复末尾标注来源
```

---

### 三、销售实战演练 (Sales Training)

#### 3.1 五阶段销售流程控制 (Stage Controller)

系统内置标准的销售全流程管理，指导用户循序渐进地完成销售任务：

1. **信任与关系建立 (Trust Building)**：判断沟通意愿，建立对话基础
2. **信息探索与需求诊断 (Needs Diagnosis)**：挖掘客户痛点，明确预算与时间
3. **价值呈现与方案链接 (Value Presentation)**：建立需求与产品的关联
4. **异议/顾虑处理 (Objection Handling)**：识别并化解客户疑虑
5. **收尾与成交 (Closing)**：明确下一步行动，达成合作意向

#### 3.2 实时评价引擎 (Evaluation Engine)

基于 Qwen-Plus 的智能评价系统，对每一轮对话进行实时分析：

```python
# 评分维度 (1-5分)
SCORING_CRITERIA = {
    "trust": "信任与关系建立",
    "needs": "信息探索与需求诊断",
    "value": "价值呈现与方案链接",
    "objection": "异议/顾虑处理管理",
    "closing": "进程推进与节奏管理"
}

# 分析输出
{
    "quality": "good",  # fair/good/excellent
    "issues": ["未确认客户预算", "回应异议不够坚定"],
    "suggestions": ["试着询问：您的预算范围大概是多少？"],
    "score": 4
}
```

#### 3.3 AI 销售助手 (Sales Copilot)

基于 RAG 的智能销售知识库系统：

**功能特性：**
- **知识库上传**：支持 PDF/XLSX 格式的销售资料
- **智能检索**：BM25 + Embedding 混合检索
- **实时建议**：根据对话上下文生成销售话术建议
- **材料推荐**：按阶段推荐 SOP、话术、Q&A、价格表等

**建议生成流程：**
```python
1. 分析当前对话上下文
2. 检索相关销售知识
3. 生成 3 条具体建议
4. 附带使用理由和注意事项
```

#### 3.4 沉浸式客户模拟

Customer Agent 基于详细画像模拟真实客户反应：
- **性格特征**：保守/开放/挑剔
- **痛点需求**：具体的业务痛点
- **防御机制**：模拟真实客户的拒绝和迟疑

---

#### 3.5 综合评价报告

训练结束后生成详细的评价报告：

**评价维度：**
- **总分**：25 分制（5 个阶段各 5 分）
- **表现等级**：优秀/良好/一般/较差
- **雷达图**：5 维能力可视化
- **优势分析**：核心优势总结
- **改进建议**：具体提升方向
- **未完成任务**：待改进事项

---

### 四、数字客服 (Customer Service)

#### 4.1 系统概述

数字客服采用**"代码控制流程，LLM只负责改写"**的设计理念，通过硬性代码规则确保话术遵循度和服务质量。

```
┌─────────────────────────────────────────────────────────┐
│                    核心设计理念                          │
├─────────────────────────────────────────────────────────┤
│  ✗ 传统方式: 让 LLM 自由发挥 → 不可控                   │
│  ✓ 本系统: 代码控制决策 + LLM 只负责改写 → 高可控       │
└─────────────────────────────────────────────────────────┘
```

#### 4.2 BM25 + Embedding 混合匹配

采用三层混合匹配架构：

```
用户问题: "孩子挑食怎么办？"
    │
    ▼
┌─────────────────────────────────────┐
│  1. BM25 关键词匹配 (权重 60%)       │
│     jieba分词 → 关键词匹配 → 归一化  │
│     得分: 0.8                        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  2. Embedding 语义匹配 (权重 40%)    │
│     text-embedding-v2 → 余弦相似度  │
│     得分: 0.9                        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  3. 混合评分                         │
│     0.6 × 0.8 + 0.4 × 0.9 = 0.84    │
└─────────────────────────────────────┘
```

#### 4.3 置信度分层策略

| 置信度范围 | 类型 | 处理策略 | LLM调用 |
|-----------|------|---------|--------|
| **≥ 0.9** | 高置信度 | 直接返回标准话术 + 风险提示 | 否 |
| **0.6-0.9** | 中置信度 | LLM 严格改写话术 | 是 |
| **< 0.6** | 低置信度 | LLM 尝试理解 + 引导重新提问 | 是 |
| **无匹配** | - | 返回引导消息 | 否 |

**高置信度示例：**
```
用户: 对报告和方案有不清楚的地方怎么办？
置信度: 0.96 (high_confidence)
回复: [直接返回CSV中的标准话术]
```

**中置信度示例：**
```
用户: 宝宝不爱吃蔬菜咋整？
置信度: 0.75 (mid_confidence)
回复: [LLM基于标准话术改写，更口语化]
```

#### 4.4 智能转人工

转人工判断采用**硬性规则**，不依赖置信度：

```python
# 条件1: 用户明确要求
关键词: ['人工', '转人工', '客服', '真人', '转接']

# 条件2: 用户表达不满
关键词: ['不满意', '投诉', '差评', '退款', '垃圾']

# 注意: 低置信度不转人工，而是引导用户重新描述问题
```

#### 4.5 CSV 数据导入

**CSV 格式规范：**

| 列 | 字段名 | 说明 | 示例 |
|---|-------|------|------|
| 1 | question_count | 提问次数 | 15 |
| 2 | topic_name | 主题名称 | 孩子挑食不吃蔬菜 |
| 3 | typical_question | 典型提问 | 孩子不爱吃蔬菜怎么办？ |
| 4 | standard_script | 标准话术 | 可以尝试将蔬菜切碎... |
| 5 | risk_notes | 风险注意事项 | 长期拒食可能导致... |

**导入流程：**

```
CSV上传
    │
    ▼
1. 解析5列数据 + 验证
    │
    ▼
2. jieba分词 → 提取关键词 (Top 20)
    │
    ▼
3. DashScope API → 生成 Embedding (1536维)
    │
    ▼
4. 批量插入数据库
    │
    ▼
5. MD5 注册 (防重复导入)
```

#### 4.6 会话管理与统计

```python
# 会话数据
{
    "session_id": "uuid",
    "start_time": "2026-01-20 10:00:00",
    "message_count": 5,
    "avg_confidence": 0.78,
    "transfer_to_human": False,
    "user_rating": 4
}

# 统计分析
{
    "total_sessions": 100,
    "avg_confidence": 0.78,
    "transfer_rate": 5.0%,
    "match_type_distribution": {
        "high_confidence": 40%,
        "mid_confidence": 50%,
        "low_confidence": 8%,
        "no_match": 2%
    }
}
```

---

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.115 | Web 框架 & WebSocket |
| DashScope | 1.22 | 阿里云 LLM (Qwen-Max/Turbo) + Embedding + Audio |
| Volcano Engine | - | 火山引擎数字人视频生成 (Image to Video) |
| SQLAlchemy | 2.0 | 异步数据库 ORM |
| aiosqlite | 0.19 | 异步 SQLite 驱动 |
| PyMuPDF | - | PDF 文本提取 |
| rank-bm25 | 0.2.2 | BM25 算法实现 |
| jieba | 0.42 | 中文分词 |
| numpy | 1.24 | 向量计算 |
| tenacity | 8.2 | 失败重试机制 |
| Loguru | 0.7 | 日志记录 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18 | UI 框架 |
| Vite | 5 | 构建工具 |
| Material-UI | 5 | UI 组件库 |
| React Router | 6 | 路由管理 |
| react-use-websocket | - | WebSocket 连接 |

---

## 📊 性能指标

### 系统性能基准

基于标准测试环境（Intel i5-10400 / 16GB RAM / Windows 11）的性能数据：

| 指标类别 | 指标项 | 数值 | 说明 |
|---------|--------|------|------|
| **并发性能** | WebSocket 并发连接 | 100+ | 单机支持 100+ 并发 WebSocket 连接 |
| | 同时在线用户 | 50+ | 推荐同时在线用户数 |
| **响应性能** | 客服系统响应延迟 | < 2s | 高置信度匹配（不调用 LLM） |
| | 群聊 Agent 响应延迟 | 3-5s | 包含 LLM 调用和打字延迟 |
| | 数字分身响应延迟 | 2-4s | 包含检索和 LLM 生成 |
| | 销售演练评价延迟 | 2-3s | 实时评价生成 |
| **匹配准确率** | 客服 QA 召回率 | ≥ 80% | 基于混合检索（BM25 + Embedding） |
| | 客服误转人工率 | < 5% | 高置信度直接回复，避免误转 |
| | 群聊路由准确率 | ≥ 85% | Fast Path + LLM Router 组合 |
| **存储性能** | 数据库大小 | ~50MB | 包含示例数据（10个名人 + 100条QA） |
| | 单个数字分身大小 | 2-5MB | 包含 PDF 原文和 Embedding 向量 |
| | 单条 Embedding 向量 | 6KB | 1536 维 float32 向量 |
| **资源占用** | 后端内存占用 | ~500MB | 空闲状态 |
| | 后端内存占用（峰值） | ~1.5GB | 10 并发对话 |
| | 前端内存占用 | ~150MB | 单页面应用 |
| | CPU 占用（空闲） | < 5% | 无请求时 |
| | CPU 占用（对话中） | 20-40% | LLM 调用期间 |
| **API 调用** | Qwen-Max 调用延迟 | 1-3s | 取决于网络和负载 |
| | Embedding 生成延迟 | 0.5-1s | 单次调用（批量更快） |
| | 每日 API 调用成本 | ¥5-20 | 取决于使用频率（100-500 次调用） |

### 性能优化建议

#### 1. 数据库优化
```python
# 使用索引加速查询
CREATE INDEX idx_embedding ON customer_service_qa(embedding);
CREATE INDEX idx_keywords ON customer_service_qa(keywords);

# 定期清理过期数据
DELETE FROM chat_messages WHERE created_at < datetime('now', '-30 days');
```

#### 2. 缓存策略
```python
# 缓存高频 QA 匹配结果（可选实现）
from functools import lru_cache

@lru_cache(maxsize=100)
def get_qa_match(question: str):
    # 缓存最近 100 个问题的匹配结果
    pass
```

#### 3. 并发控制
```python
# 限制并发 LLM 调用数量
import asyncio
semaphore = asyncio.Semaphore(10)  # 最多 10 个并发请求

async def call_llm_with_limit():
    async with semaphore:
        return await call_llm()
```

#### 4. 批量处理
```python
# 批量生成 Embedding（导入知识库时）
embeddings = await generate_embeddings_batch(texts, batch_size=20)
```

### 扩展性考虑

| 场景 | 当前方案 | 扩展方案 |
|------|---------|---------|
| **高并发** | SQLite（写并发有限） | 切换到 PostgreSQL/MySQL |
| **大规模知识库** | 内存加载 BM25 索引 | 使用 Elasticsearch/Milvus |
| **分布式部署** | 单机部署 | 使用 Redis 共享会话状态 |
| **负载均衡** | 单实例 | Nginx + 多后端实例 |
| **高可用** | 无冗余 | 主从数据库 + 健康检查 |

### 成本估算

基于阿里云 DashScope 定价（2026年1月）：

| 模型 | 输入价格 | 输出价格 | 适用场景 | 日均成本估算 |
|------|---------|---------|---------|-------------|
| qwen-max | ¥0.04/1K tokens | ¥0.12/1K tokens | 主回复、评价 | ¥10-30（200-500次调用） |
| qwen-plus | ¥0.008/1K tokens | ¥0.024/1K tokens | 评价、改写 | ¥3-10（500-1000次调用） |
| qwen-turbo | ¥0.003/1K tokens | ¥0.006/1K tokens | 路由、简单任务 | ¥1-3（1000+次调用） |
| text-embedding-v2 | ¥0.0007/1K tokens | - | 向量生成 | ¥0.5-2（1000+次调用） |

**成本优化建议：**
- 路由和简单任务使用 `qwen-turbo`
- 高置信度客服回复不调用 LLM（节省 40-50% 成本）
- 批量生成 Embedding（降低 API 调用次数）
- 缓存常见问题的回复

---

## 🏗️ 系统架构

### 整体架构图

```mermaid
graph TD
    subgraph Frontend["前端 (React)"]
        GroupChat[智能群聊页面]
        Celebrity[数字分身页面]
        SalesCopilot[销售演练页面]
        CustomerService[数字客服页面]
    end

    subgraph Backend["后端 (FastAPI)"]
        WS1["/ws 群聊"]
        WS2["/ws/celebrity 分身"]
        WS3["/ws/customer-service 客服"]
        WS4["/ws/training 演练"]

        subgraph Services["核心服务"]
            Orchestrator[群聊编排器]
            CelebrityOrch[分身编排器]
            CSOrch[客服编排器]
            TrainingOrch[培训编排器]

            Agent[Agent服务]
            CelebrityAgent[分身Agent]
            CustomerAgent[客户Agent]

            QAMatcher[QA匹配引擎]
            ResponseGen[回复生成器]
            EvaluationEng[评价引擎]
            
            Router[LLM路由]
            VideoSvc[视频生成服务]
        end

        subgraph Data["数据层"]
            DB[(SQLite)]
            Embedding[Embedding服务]
        end
    end

    subgraph External["外部服务"]
        QwenMax[Qwen-Max]
        QwenTurbo[Qwen-Turbo]
        EmbeddingAPI[text-embedding-v2]
    end

    GroupChat --> WS1
    Celebrity --> WS2
    CustomerService --> WS3

    WS1 --> Orchestrator
    WS2 --> CelebrityOrch
    WS3 --> CSOrch

    Orchestrator --> Agent
    Orchestrator --> Router
    Orchestrator --> Guardrail

    CelebrityOrch --> CelebrityAgent
    CelebrityOrch --> PDFParser

    CSOrch --> QAMatcher
    CSOrch --> ResponseGen
    CSOrch --> SessionMgr

    Agent --> QwenMax
    CelebrityAgent --> QwenMax
    Router --> QwenTurbo
    ResponseGen --> QwenTurbo

    QAMatcher --> Embedding
    PDFParser --> QwenMax
    Embedding --> EmbeddingAPI

    QAMatcher --> DB
    SessionMgr --> DB
    CelebrityOrch --> DB
```

### 目录结构

```bash
VividCrowd/
├── backend/                              # Python 后端
│   ├── main.py                          # FastAPI 主入口
│   ├── core/
│   │   ├── config.py                    # 全局配置
│   │   └── database.py                  # 数据库连接管理
│   ├── models/
│   │   ├── db_models.py                 # SQLAlchemy 数据库模型
│   │   └── schemas.py                   # Pydantic 数据模型
│   ├── apps/                            # 四大应用模块
│   │   ├── chat/                        # 智能群聊
│   │   │   ├── app.py                   # 群聊应用入口
│   │   │   └── services/
│   │   │       ├── orchestrator.py      # 群聊编排器
│   │   │       ├── agent.py             # Agent 服务
│   │   │       ├── router.py            # LLM 路由
│   │   │       └── guardrail.py         # 安全围栏
│   │   ├── celebrity/                   # 数字分身
│   │   │   ├── app.py                   # 分身应用入口
│   │   │   └── services/
│   │   │       ├── celebrity_orchestrator.py
│   │   │       ├── celebrity_agent.py
│   │   │       ├── celebrity_retriever.py
│   │   │       ├── pdf_parser.py
│   │   │       ├── chunking_service.py
│   │   │       ├── video_service.py     # 数字人视频
│   │   │       ├── audio_service.py     # TTS/ASR
│   │   │       └── session_manager.py
│   │   ├── customer_service/            # 数字客服
│   │   │   ├── app.py                   # 客服应用入口
│   │   │   └── services/
│   │   │       ├── orchestrator.py
│   │   │       ├── qa_matcher.py        # QA 匹配引擎
│   │   │       ├── response_generator.py
│   │   │       ├── session_manager.py
│   │   │       ├── embedding_service.py
│   │   │       ├── excel_importer.py
│   │   │       └── csv_registry.py
│   │   └── digital_customer/            # 销售演练
│   │       ├── app.py                   # 演练应用入口
│   │       └── services/
│   │           ├── customer_orchestrator.py
│   │           ├── customer_agent.py
│   │           ├── customer_retriever.py
│   │           ├── profile_parser.py
│   │           ├── chunking_service.py
│   │           ├── audio_service.py
│   │           └── training/            # 培训模块
│   │               ├── training_orchestrator.py
│   │               ├── evaluation_engine.py
│   │               ├── stage_controller.py
│   │               ├── knowledge_service.py
│   │               └── suggestion_generator.py
│   ├── data/                            # 数据库文件
│   │   ├── celebrity.db                 # 数字分身数据库
│   │   ├── customerService.db           # 客服数据库
│   │   └── digital_customer.db          # 销售演练数据库
│   ├── agents_profiles.json             # 群聊 Agent 人设
│   └── requirements.txt
│
├── frontend/                            # React 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx              # 侧边栏导航
│   │   │   ├── training/                # 销售演练组件
│   │   │   │   ├── StageIndicator.jsx   # 阶段指示器
│   │   │   │   ├── RealTimeFeedback.jsx # 实时反馈
│   │   │   │   ├── SalesCopilot.jsx     # AI 助手
│   │   │   │   ├── SalesMaterialsPanel.jsx
│   │   │   │   └── RadarChart.jsx       # 雷达图
│   │   │   ├── celebrity/               # 数字分身组件
│   │   │   │   ├── CelebrityCard.jsx
│   │   │   │   ├── CelebrityUpload.jsx
│   │   │   │   ├── CelebritySelector.jsx
│   │   │   │   └── ChatModeToggle.jsx
│   │   │   ├── digital_customer/
│   │   │   │   └── DigitalCustomerUpload.jsx
│   │   │   └── common/
│   │   │       ├── AudioInput.jsx       # 语音输入
│   │   │       └── ConnectionStatus.jsx
│   │   ├── hooks/
│   │   │   ├── useCelebrityWebSocket.js
│   │   │   ├── useCustomerServiceWS.js
│   │   │   └── useWebSocketWithRetry.js
│   │   ├── pages/
│   │   │   ├── GroupChatPage.jsx        # 智能群聊
│   │   │   ├── CelebrityPage.jsx        # 数字分身
│   │   │   ├── CustomerServicePage.jsx  # 数字客服
│   │   │   ├── DigitalCustomerPage.jsx  # 销售演练
│   │   │   └── Training/
│   │   │       └── EvaluationReportPage.jsx
│   │   ├── config.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── README.md                            # 中文文档
└── README_EN.md                         # English Documentation
```

---

## 🚀 快速启动

### 前置要求

- **Python 3.9+**
- **Node.js 16+**
- **阿里云 DashScope API Key** ([申请地址](https://dashscope.console.aliyun.com/))

### 5 分钟快速体验

#### 方式一：一键启动脚本（推荐新手）

**Windows 用户：**
```bash
# 1. 下载项目
git clone https://github.com/your-username/VividCrowd.git
cd VividCrowd

# 2. 运行一键启动脚本
start.bat
```

**Linux/Mac 用户：**
```bash
# 1. 下载项目
git clone https://github.com/your-username/VividCrowd.git
cd VividCrowd

# 2. 赋予执行权限并运行
chmod +x start.sh
./start.sh
```

脚本会自动完成：
- ✅ 检查 Python 和 Node.js 环境
- ✅ 安装后端依赖
- ✅ 安装前端依赖
- ✅ 引导配置 API Key
- ✅ 启动后端和前端服务
- ✅ 自动打开浏览器

---

#### 方式二：手动安装（推荐开发者）

**1. 克隆项目**

```bash
git clone https://github.com/your-username/VividCrowd.git
cd VividCrowd
```

**2. 配置环境变量**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# Windows: notepad .env
# Linux/Mac: nano .env
```

在 `.env` 文件中设置：
```bash
DASHSCOPE_API_KEY=your_api_key_here
```

**3. 后端设置**

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**4. 前端设置**

打开新的终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**5. 访问应用**

浏览器打开 `http://localhost:5173`

**6. 验证启动成功**

- ✅ 后端：访问 `http://localhost:8000/docs` 查看 API 文档（应显示 Swagger UI）
- ✅ 前端：页面正常显示四个功能模块入口（智能群聊、数字分身、数字客服、销售演练）
- ✅ WebSocket：进入任意聊天页面，右上角连接状态显示"已连接"（绿色）
- ✅ 功能测试：在智能群聊中发送"大家好"，应收到 Agent 回复

**7. 首次使用建议**

体验顺序（从简单到复杂）：
1. **智能群聊**：直接发送消息，体验多 Agent 对话
2. **数字客服**：需要先导入知识库（CSV 文件）
3. **数字分身**：需要先上传 PDF 创建分身
4. **销售演练**：需要先上传客户档案和销售知识库

---

## 🚀 生产环境部署指南

### Docker 部署（推荐）

#### 1. 使用 Docker Compose

**创建 `docker-compose.yml`：**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - VOLCENGINE_ACCESS_KEY=${VOLCENGINE_ACCESS_KEY}
      - VOLCENGINE_SECRET_KEY=${VOLCENGINE_SECRET_KEY}
      - OSS_ACCESS_KEY_ID=${OSS_ACCESS_KEY_ID}
      - OSS_ACCESS_KEY_SECRET=${OSS_ACCESS_KEY_SECRET}
      - OSS_BUCKET_NAME=${OSS_BUCKET_NAME}
      - OSS_ENDPOINT=${OSS_ENDPOINT}
    volumes:
      - ./backend/data:/app/data
      - ./backend/logs:/app/logs
    restart: unless-stopped
    networks:
      - vividcrowd

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - vividcrowd

networks:
  vividcrowd:
    driver: bridge

volumes:
  backend_data:
  backend_logs:
```

**创建后端 `Dockerfile`（`backend/Dockerfile`）：**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**创建前端 `Dockerfile`（`frontend/Dockerfile`）：**
```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install --registry=https://registry.npmmirror.com

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**创建 Nginx 配置（`frontend/nginx.conf`）：**
```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # 前端路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_read_timeout 86400;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**启动服务：**
```bash
# 1. 创建 .env 文件
cp .env.example .env
# 编辑 .env 填入实际配置

# 2. 构建并启动
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down

# 5. 重新构建
docker-compose up -d --build
```

---

### 传统部署方式

#### 1. 使用 PM2 管理后端进程

**安装 PM2：**
```bash
npm install -g pm2
```

**创建 `ecosystem.config.js`：**
```javascript
module.exports = {
  apps: [{
    name: 'vividcrowd-backend',
    script: 'uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000',
    cwd: './backend',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      DASHSCOPE_API_KEY: 'your-api-key'
    },
    error_file: './logs/backend-error.log',
    out_file: './logs/backend-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
```

**启动服务：**
```bash
# 启动
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs vividcrowd-backend

# 重启
pm2 restart vividcrowd-backend

# 停止
pm2 stop vividcrowd-backend

# 开机自启
pm2 startup
pm2 save
```

#### 2. 使用 Systemd 管理（Linux）

**创建服务文件 `/etc/systemd/system/vividcrowd.service`：**
```ini
[Unit]
Description=VividCrowd Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/vividcrowd/backend
Environment="DASHSCOPE_API_KEY=your-api-key"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务：**
```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start vividcrowd

# 开机自启
sudo systemctl enable vividcrowd

# 查看状态
sudo systemctl status vividcrowd

# 查看日志
sudo journalctl -u vividcrowd -f
```

---

### Nginx 反向代理配置

**创建配置文件 `/etc/nginx/sites-available/vividcrowd`：**
```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 前端静态文件
    location / {
        root /var/www/vividcrowd/frontend/dist;
        try_files $uri $uri/ /index.html;

        # 缓存配置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;

        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 86400s;  # WebSocket 长连接

        # 缓冲配置
        proxy_buffering off;
    }

    # 文件上传大小限制
    client_max_body_size 50M;

    # 访问日志
    access_log /var/log/nginx/vividcrowd-access.log;
    error_log /var/log/nginx/vividcrowd-error.log;
}
```

**启用配置：**
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/vividcrowd /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx
```

---

### HTTPS 证书配置（Let's Encrypt）

**使用 Certbot 自动获取证书：**
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书（自动配置 Nginx）
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 测试自动续期
sudo certbot renew --dry-run

# 证书会自动续期，无需手动操作
```

---

### 数据库备份策略

**创建备份脚本 `backup.sh`：**
```bash
#!/bin/bash

# 配置
BACKUP_DIR="/var/backups/vividcrowd"
DATA_DIR="/var/www/vividcrowd/backend/data"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份文件名（带时间戳）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# 压缩备份
tar -czf $BACKUP_FILE -C $DATA_DIR .

# 删除旧备份（保留最近 30 天）
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
```

**设置定时备份（Crontab）：**
```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨 2 点备份
0 2 * * * /var/www/vividcrowd/backup.sh >> /var/log/vividcrowd-backup.log 2>&1
```

---

### 监控与日志

#### 1. 日志轮转配置

**创建 `/etc/logrotate.d/vividcrowd`：**
```
/var/www/vividcrowd/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload vividcrowd > /dev/null 2>&1 || true
    endscript
}
```

#### 2. 系统监控

**使用 htop 监控资源：**
```bash
sudo apt install htop
htop
```

**监控磁盘空间：**
```bash
# 查看磁盘使用情况
df -h

# 查看目录大小
du -sh /var/www/vividcrowd/backend/data
```

**监控进程：**
```bash
# 查看后端进程
ps aux | grep uvicorn

# 查看端口占用
netstat -tulpn | grep 8000
```

---

### 性能优化建议

#### 1. 数据库优化
```bash
# 定期清理过期数据
sqlite3 backend/data/celebrity.db "DELETE FROM chat_messages WHERE created_at < datetime('now', '-30 days');"

# 优化数据库
sqlite3 backend/data/celebrity.db "VACUUM;"
```

#### 2. 启用 Gzip 压缩（Nginx）
```nginx
# 在 nginx.conf 中添加
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

#### 3. 使用 CDN 加速静态资源
- 将前端静态文件上传到 CDN
- 修改 `frontend/src/config.js` 中的资源路径

---

### 安全加固

#### 1. 防火墙配置（UFW）
```bash
# 启用防火墙
sudo ufw enable

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status
```

#### 2. 限制 API 访问频率（Nginx）
```nginx
# 在 http 块中添加
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# 在 location /api/ 中添加
limit_req zone=api_limit burst=20 nodelay;
```

#### 3. 禁用不必要的端口
```bash
# 确保后端只监听 127.0.0.1（通过 Nginx 代理）
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 🔧 安装故障排查

### 常见问题与解决方案

#### 1. Python 依赖安装失败

**问题现象：**
```bash
ERROR: Could not find a version that satisfies the requirement...
```

**解决方案：**
```bash
# 使用国内镜像源加速（推荐清华源）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或配置永久镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2. Node.js 依赖安装失败

**问题现象：**
```bash
npm ERR! network timeout
```

**解决方案：**
```bash
# 使用淘宝镜像源
npm install --registry=https://registry.npmmirror.com

# 或使用 yarn
yarn install --registry=https://registry.npmmirror.com

# 配置永久镜像源
npm config set registry https://registry.npmmirror.com
```

#### 3. 数据库初始化错误

**问题现象：**
```bash
sqlite3.OperationalError: unable to open database file
```

**解决方案：**
```bash
# 确保 backend/data 目录存在
mkdir -p backend/data

# 检查目录权限
chmod 755 backend/data
```

#### 4. WebSocket 连接失败

**问题现象：**
- 前端显示"连接失败"或"断开连接"
- 浏览器控制台报错：`WebSocket connection failed`

**解决方案：**
```bash
# 1. 检查后端是否正常运行
curl http://localhost:8000/docs

# 2. 检查防火墙设置（Windows）
# 允许 Python 通过防火墙

# 3. 检查前端配置文件 frontend/src/config.js
# 确保 WebSocket URL 正确：ws://localhost:8000
```

#### 5. API Key 配置错误

**问题现象：**
```bash
dashscope.common.error.AuthenticationError: Invalid API-key
```

**解决方案：**
```bash
# 1. 检查环境变量是否设置
echo $DASHSCOPE_API_KEY  # Linux/Mac
echo %DASHSCOPE_API_KEY%  # Windows CMD
$env:DASHSCOPE_API_KEY    # Windows PowerShell

# 2. 确认 API Key 有效性
# 访问 https://dashscope.console.aliyun.com/ 查看密钥

# 3. 重新设置环境变量后重启后端服务
```

#### 6. 端口占用问题

**问题现象：**
```bash
ERROR: [Errno 48] Address already in use
```

**解决方案：**
```bash
# 查找占用端口的进程
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -i :8000
kill -9 <进程ID>

# 或使用其他端口启动
uvicorn app.main:app --port 8001
```

#### 7. CORS 跨域问题

**问题现象：**
- 浏览器控制台报错：`Access-Control-Allow-Origin`

**解决方案：**
```python
# backend/main.py 已配置 CORS，确保包含以下代码：
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 8. 前端页面空白

**问题现象：**
- 浏览器显示空白页面
- 控制台报错：`Failed to fetch`

**解决方案：**
```bash
# 1. 检查后端是否启动
curl http://localhost:8000/api/chat/agents

# 2. 清除浏览器缓存并刷新
# Chrome: Ctrl+Shift+Delete

# 3. 检查前端配置文件
# frontend/src/config.js 中的 API_BASE_URL 是否正确

# 4. 重新构建前端
cd frontend
rm -rf node_modules dist
npm install
npm run dev
```

#### 9. PDF 上传失败

**问题现象：**
```bash
PyMuPDF error: cannot open file
```

**解决方案：**
```bash
# 1. 检查文件大小（建议 < 10MB）
# 2. 确认 PDF 文件未加密
# 3. 尝试使用其他 PDF 文件测试
# 4. 检查后端日志获取详细错误信息
```

#### 10. 模型调用超时

**问题现象：**
```bash
httpx.ReadTimeout: timed out
```

**解决方案：**
```python
# 增加超时时间（backend/core/config.py）
REQUEST_TIMEOUT = 60  # 秒

# 或检查网络连接
# 确保能访问 dashscope.aliyuncs.com
```

---

## 📡 API 接口文档

### REST API

#### 智能群聊 (`/api/chat`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/chat/agents` | 获取所有群聊 Agent 信息 |

#### 数字分身 (`/api/celebrity`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/celebrity` | 获取所有数字分身列表 |
| GET | `/api/celebrity/{id}` | 获取指定数字分身详情 |
| POST | `/api/celebrity/upload` | 上传 PDF 创建数字分身 |
| DELETE | `/api/celebrity/{id}` | 删除数字分身 |
| POST | `/api/celebrity/digital-human/generate-video` | 生成数字人视频 |
| POST | `/api/celebrity/digital-human/transcribe-audio` | 语音转文字 |

#### 数字客服 (`/api/customer-service`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/customer-service/stats` | 获取统计数据 |
| GET | `/api/customer-service/qa/count` | 获取 QA 记录数 |
| POST | `/api/customer-service/session` | 创建新会话 |
| GET | `/api/customer-service/session/{id}/history` | 获取会话历史 |
| POST | `/api/customer-service/session/{id}/rating` | 提交用户评分 |

#### 销售演练 (`/api/digital-customer`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/digital-customer` | 获取所有客户档案 |
| GET | `/api/digital-customer/{id}` | 获取客户详情 |
| POST | `/api/digital-customer/upload` | 上传客户档案 |
| DELETE | `/api/digital-customer/{id}` | 删除客户档案 |
| POST | `/api/digital-customer/knowledge/upload` | 上传销售知识库 |
| GET | `/api/digital-customer/knowledge/files` | 获取知识文件列表 |
| POST | `/api/digital-customer/knowledge/query` | 查询知识库 |
| POST | `/api/digital-customer/training/sessions/start` | 开始培训会话 |
| GET | `/api/digital-customer/training/sessions` | 获取培训记录 |
| GET | `/api/digital-customer/training/sessions/{id}/evaluation` | 获取评价报告 |
| POST | `/api/digital-customer/audio/transcribe` | 语音转文字 |
| POST | `/api/digital-customer/audio/synthesize` | 文字转语音 |

### WebSocket 端点

#### 智能群聊 (`/api/chat/ws`)

**发送：** 纯文本消息

**接收：**
```json
{"type": "stream_start", "sender": "小林", "content": ""}
{"type": "stream_chunk", "sender": "小林", "content": "姐妹"}
{"type": "stream_end", "sender": "小林", "content": ""}
```

#### 数字分身 (`/api/celebrity/ws`)

**发送：**
```json
{
  "message": "如何看待人工智能？",
  "celebrity_ids": [1, 2, 3],
  "mode": "private|group"
}
```

**接收：** 同上

#### 数字客服 (`/api/customer-service/ws`)

**发送：**
```json
{"message": "孩子挑食怎么办？"}
```

**接收：**
```json
{"type": "session_created", "session_id": "uuid"}
{"type": "response", "content": "...", "confidence": 0.85, "match_type": "mid_confidence"}
```

#### 销售演练 - 客户对话 (`/api/digital-customer/ws`)

**发送：**
```json
{"message": "你好，我想了解一下你们的产品"}
```

**接收：** 同群聊格式

#### 销售演练 - 培训模式 (`/api/digital-customer/training/ws/{session_id}`)

**发送：**
```json
{"message": "您好，请问您最近在业务上有什么困扰吗？"}
```

**接收：**
```json
{
  "type": "evaluation",
  "quality": "good",
  "issues": ["未确认预算"],
  "suggestions": ["询问预算范围"],
  "score": 4
}
{
  "type": "customer_response",
  "content": "...",
  "audio_url": "https://..."
}
{
  "type": "stage_completed",
  "stage": 1,
  "next_stage": 2
}
```

### API 使用示例

#### Python 示例

**1. 获取数字分身列表**
```python
import requests

# 获取所有数字分身
response = requests.get("http://localhost:8000/api/celebrity")
celebrities = response.json()

for celebrity in celebrities:
    print(f"ID: {celebrity['id']}, 名称: {celebrity['name']}")
```

**2. 上传 PDF 创建数字分身**
```python
import requests

# 上传 PDF 文件
with open("einstein.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "source_type": "person",  # person/book/topic
        "name": "爱因斯坦"
    }
    response = requests.post(
        "http://localhost:8000/api/celebrity/upload",
        files=files,
        data=data
    )

result = response.json()
print(f"创建成功！ID: {result['id']}")
```

**3. 导入客服知识库（CSV）**
```python
import requests

# 上传 CSV 文件
with open("customer_service_qa.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/customer-service/qa/import",
        files=files
    )

result = response.json()
print(f"导入成功！共 {result['count']} 条记录")
```

**4. 获取客服统计数据**
```python
import requests

response = requests.get("http://localhost:8000/api/customer-service/stats")
stats = response.json()

print(f"总会话数: {stats['total_sessions']}")
print(f"平均置信度: {stats['avg_confidence']:.2f}")
print(f"转人工率: {stats['transfer_rate']:.1f}%")
```

**5. WebSocket 连接示例（智能群聊）**
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/api/chat/ws"

    async with websockets.connect(uri) as websocket:
        # 发送消息
        await websocket.send("大家好，有人在吗？")

        # 接收流式响应
        full_message = ""
        current_sender = None

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if data["type"] == "stream_start":
                    current_sender = data["sender"]
                    print(f"\n{current_sender}: ", end="", flush=True)

                elif data["type"] == "stream_chunk":
                    content = data["content"]
                    print(content, end="", flush=True)
                    full_message += content

                elif data["type"] == "stream_end":
                    print()  # 换行
                    full_message = ""

            except websockets.exceptions.ConnectionClosed:
                break

# 运行
asyncio.run(chat())
```

**6. WebSocket 连接示例（数字分身）**
```python
import asyncio
import websockets
import json

async def chat_with_celebrity():
    uri = "ws://localhost:8000/api/celebrity/ws"

    async with websockets.connect(uri) as websocket:
        # 发送消息（与多个名人对话）
        message = {
            "message": "如何看待人工智能的未来？",
            "celebrity_ids": [1, 2, 3],  # 爱因斯坦、孔子、乔布斯
            "mode": "group"  # private 或 group
        }
        await websocket.send(json.dumps(message))

        # 接收响应
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)

                if data["type"] == "stream_chunk":
                    print(data["content"], end="", flush=True)
                elif data["type"] == "stream_end":
                    print("\n")

            except websockets.exceptions.ConnectionClosed:
                break

asyncio.run(chat_with_celebrity())
```

#### JavaScript 示例

**1. 获取群聊 Agent 列表**
```javascript
// 使用 fetch API
async function getAgents() {
    const response = await fetch('http://localhost:8000/api/chat/agents');
    const agents = await response.json();

    agents.forEach(agent => {
        console.log(`${agent.name} - ${agent.occupation}`);
    });
}

getAgents();
```

**2. 创建客服会话**
```javascript
async function createSession() {
    const response = await fetch('http://localhost:8000/api/customer-service/session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const session = await response.json();
    console.log('会话ID:', session.session_id);
    return session.session_id;
}
```

**3. WebSocket 连接示例（智能群聊）**
```javascript
// 连接 WebSocket
const ws = new WebSocket('ws://localhost:8000/api/chat/ws');

// 连接成功
ws.onopen = () => {
    console.log('WebSocket 连接成功');
    // 发送消息
    ws.send('大家好！');
};

// 接收消息
let currentMessage = '';
let currentSender = '';

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch(data.type) {
        case 'stream_start':
            currentSender = data.sender;
            currentMessage = '';
            console.log(`\n${currentSender}: `);
            break;

        case 'stream_chunk':
            currentMessage += data.content;
            process.stdout.write(data.content);  // Node.js
            // 或在浏览器中: document.getElementById('chat').innerText += data.content;
            break;

        case 'stream_end':
            console.log('\n');
            break;
    }
};

// 错误处理
ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);
};

// 连接关闭
ws.onclose = () => {
    console.log('WebSocket 连接已关闭');
};
```

**4. WebSocket 连接示例（客服系统）**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/customer-service/ws');

ws.onopen = () => {
    // 发送客户问题
    const message = {
        message: '孩子挑食怎么办？'
    };
    ws.send(JSON.stringify(message));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'session_created') {
        console.log('会话ID:', data.session_id);
    } else if (data.type === 'response') {
        console.log('回复:', data.content);
        console.log('置信度:', data.confidence);
        console.log('匹配类型:', data.match_type);
    }
};
```

**5. React Hook 示例（使用 react-use-websocket）**
```javascript
import { useWebSocket } from 'react-use-websocket';
import { useState, useEffect } from 'react';

function ChatComponent() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');

    const { sendMessage, lastMessage, readyState } = useWebSocket(
        'ws://localhost:8000/api/chat/ws',
        {
            onOpen: () => console.log('连接成功'),
            onClose: () => console.log('连接关闭'),
            shouldReconnect: () => true,  // 自动重连
        }
    );

    // 处理接收到的消息
    useEffect(() => {
        if (lastMessage !== null) {
            const data = JSON.parse(lastMessage.data);

            if (data.type === 'stream_chunk') {
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMsg = newMessages[newMessages.length - 1];

                    if (lastMsg && lastMsg.sender === data.sender) {
                        lastMsg.content += data.content;
                    } else {
                        newMessages.push({
                            sender: data.sender,
                            content: data.content
                        });
                    }

                    return newMessages;
                });
            }
        }
    }, [lastMessage]);

    // 发送消息
    const handleSend = () => {
        sendMessage(inputValue);
        setInputValue('');
    };

    return (
        <div>
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx}>
                        <strong>{msg.sender}:</strong> {msg.content}
                    </div>
                ))}
            </div>
            <input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend}>发送</button>
        </div>
    );
}
```

#### cURL 示例

**1. 获取数字分身列表**
```bash
curl -X GET http://localhost:8000/api/celebrity
```

**2. 上传 PDF 创建数字分身**
```bash
curl -X POST http://localhost:8000/api/celebrity/upload \
  -F "file=@einstein.pdf" \
  -F "source_type=person" \
  -F "name=爱因斯坦"
```

**3. 删除数字分身**
```bash
curl -X DELETE http://localhost:8000/api/celebrity/1
```

**4. 获取客服统计数据**
```bash
curl -X GET http://localhost:8000/api/customer-service/stats
```

**5. 导入客服知识库**
```bash
curl -X POST http://localhost:8000/api/customer-service/qa/import \
  -F "file=@customer_qa.csv"
```

**6. 开始销售培训会话**
```bash
curl -X POST http://localhost:8000/api/digital-customer/training/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "user_id": "user123"
  }'
```

**7. 获取培训评价报告**
```bash
curl -X GET http://localhost:8000/api/digital-customer/training/sessions/1/evaluation
```

**8. 查看 API 文档（Swagger UI）**
```bash
# 在浏览器中打开
open http://localhost:8000/docs

# 或使用 curl 获取 OpenAPI JSON
curl -X GET http://localhost:8000/openapi.json
```

---

## ⚙️ 配置指南

### 后端配置 (`backend/core/config.py`)

```python
# API 密钥
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")  # 阿里云 DashScope

# LLM 模型配置
MODEL_NAME = "qwen-max"                    # 主回复模型
ROUTER_MODEL_NAME = "qwen-turbo"           # 路由模型
EVALUATION_MODEL = "qwen-plus"             # 评价模型

# 群聊配置
STRICT_PERSONA_CHECK = True                # 严格人设检查
ENABLE_LLM_ROUTING = True                  # LLM 语义路由
MIN_TYPING_DELAY = 8.0                     # 最小打字延迟 (秒)
MAX_TYPING_DELAY = 10.0                    # 最大打字延迟 (秒)
MAX_AGENTS_PER_ROUND = 3                   # 每轮最多回复人数

# 深夜模式
NIGHT_MODE_START_HOUR = 23
NIGHT_MODE_END_HOUR = 7
NIGHT_MODE_PROBABILITY = 0.2               # 深夜活跃概率

# 客服配置
HIGH_CONFIDENCE_THRESHOLD = 0.9            # 高置信度阈值
MID_CONFIDENCE_THRESHOLD = 0.6             # 中置信度阈值
BM25_WEIGHT = 0.6                          # BM25 权重
EMBEDDING_WEIGHT = 0.4                     # Embedding 权重

# 数字人配置（火山引擎）
CELEBRITY_VOLCENGINE_ACCESS_KEY = os.getenv("VOLCENGINE_ACCESS_KEY")
CELEBRITY_VOLCENGINE_SECRET_KEY = os.getenv("VOLCENGINE_SECRET_KEY")

# OSS 配置（阿里云对象存储）
CELEBRITY_OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
CELEBRITY_OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
CELEBRITY_OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME")
CELEBRITY_OSS_ENDPOINT = os.getenv("OSS_ENDPOINT")
```

### 前端配置 (`frontend/src/config.js`)

```javascript
export const CONFIG = {
  API_BASE_URL: 'http://localhost:8000',
  WS_URL: 'ws://localhost:8000/api/chat/ws',
  CELEBRITY_WS_URL: 'ws://localhost:8000/api/celebrity/ws',
  CUSTOMER_SERVICE_WS_URL: 'ws://localhost:8000/api/customer-service/ws',
  DIGITAL_CUSTOMER_WS_URL: 'ws://localhost:8000/api/digital-customer/ws',
  TRAINING_WS_URL: 'ws://localhost:8000/api/digital-customer/training/ws'
};
```

### 环境变量完整列表

创建 `.env` 文件或设置系统环境变量：

#### 必需变量

| 变量名 | 说明 | 示例值 | 获取方式 |
|--------|------|--------|---------|
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API 密钥 | `sk-xxx` | [申请地址](https://dashscope.console.aliyun.com/) |

#### 可选变量（数字人功能）

| 变量名 | 说明 | 示例值 | 用途 |
|--------|------|--------|------|
| `VOLCENGINE_ACCESS_KEY` | 火山引擎访问密钥 | `AKxxx` | 数字人视频生成 |
| `VOLCENGINE_SECRET_KEY` | 火山引擎密钥 | `xxx` | 数字人视频生成 |
| `OSS_ACCESS_KEY_ID` | 阿里云 OSS 访问密钥 ID | `LTAI5xxx` | 视频文件存储 |
| `OSS_ACCESS_KEY_SECRET` | 阿里云 OSS 访问密钥 | `xxx` | 视频文件存储 |
| `OSS_BUCKET_NAME` | OSS Bucket 名称 | `my-bucket` | 视频文件存储 |
| `OSS_ENDPOINT` | OSS 端点 | `oss-cn-hangzhou.aliyuncs.com` | 视频文件存储 |

#### 服务器配置（可选）

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `HOST` | 监听地址 | `0.0.0.0` | 生产环境建议 `0.0.0.0` |
| `PORT` | 监听端口 | `8000` | 确保端口未被占用 |
| `LOG_LEVEL` | 日志级别 | `INFO` | DEBUG/INFO/WARNING/ERROR |
| `RELOAD` | 热重载 | `False` | 开发环境可设为 `True` |

#### 数据库配置（可选）

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `DATABASE_PATH` | 数据库文件路径 | `./data` | SQLite 数据库存储目录 |
| `DATABASE_URL` | 数据库连接 URL | - | 切换到 PostgreSQL 时使用 |

#### 模型配置（可选）

| 变量名 | 说明 | 默认值 | 备注 |
|--------|------|--------|------|
| `MODEL_NAME` | 主回复模型 | `qwen-max` | qwen-max/plus/turbo |
| `ROUTER_MODEL_NAME` | 路由模型 | `qwen-turbo` | 建议使用 turbo 降低成本 |
| `EVALUATION_MODEL` | 评价模型 | `qwen-plus` | 用于销售演练评价 |

#### 示例 `.env` 文件

```bash
# ============================================
# VividCrowd 环境变量配置
# ============================================

# -------------------- 必需配置 --------------------
# 阿里云 DashScope API Key（必需）
DASHSCOPE_API_KEY=sk-your-api-key-here

# -------------------- 数字人功能（可选）--------------------
# 火山引擎配置（用于数字人视频生成）
# VOLCENGINE_ACCESS_KEY=your-access-key
# VOLCENGINE_SECRET_KEY=your-secret-key

# 阿里云 OSS 配置（用于视频文件存储）
# OSS_ACCESS_KEY_ID=your-access-key-id
# OSS_ACCESS_KEY_SECRET=your-access-key-secret
# OSS_BUCKET_NAME=your-bucket-name
# OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# -------------------- 服务器配置（可选）--------------------
# HOST=0.0.0.0
# PORT=8000
# LOG_LEVEL=INFO

# -------------------- 数据库配置（可选）--------------------
# DATABASE_PATH=./data

# -------------------- 模型配置（可选）--------------------
# MODEL_NAME=qwen-max
# ROUTER_MODEL_NAME=qwen-turbo
# EVALUATION_MODEL=qwen-plus
```

**使用方式：**

```bash
# 方法一：使用 .env 文件（推荐）
# 1. 复制示例文件
cp .env.example .env

# 2. 编辑 .env 文件填入实际值
nano .env

# 3. 启动服务（自动加载 .env）
uvicorn app.main:app --reload

# 方法二：直接设置环境变量
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your-api-key"

# Linux/Mac
export DASHSCOPE_API_KEY="your-api-key"

# 方法三：启动时指定
DASHSCOPE_API_KEY="your-api-key" uvicorn app.main:app --reload
```

---

## 🔒 安全注意事项

### 1. API Key 安全管理

#### ❌ 错误做法
```python
# 不要硬编码 API Key
DASHSCOPE_API_KEY = "sk-1234567890abcdef"  # 危险！

# 不要提交到 Git
git add .env  # 危险！
```

#### ✅ 正确做法
```python
# 使用环境变量
import os
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 添加 .env 到 .gitignore
echo ".env" >> .gitignore
```

**最佳实践：**
- 使用环境变量或密钥管理服务（如 AWS Secrets Manager）
- 定期轮换 API Key
- 为不同环境使用不同的 API Key（开发/测试/生产）
- 监控 API Key 使用情况，及时发现异常

---

### 2. 数据库访问控制

#### 文件权限设置
```bash
# 限制数据库文件权限（仅所有者可读写）
chmod 600 backend/data/*.db

# 限制数据目录权限
chmod 700 backend/data
```

#### 数据加密
```python
# 敏感字段加密存储（可选实现）
from cryptography.fernet import Fernet

# 生成密钥
key = Fernet.generate_key()
cipher = Fernet(key)

# 加密
encrypted_data = cipher.encrypt(b"sensitive data")

# 解密
decrypted_data = cipher.decrypt(encrypted_data)
```

---

### 3. CORS 配置建议

#### 开发环境（宽松）
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 生产环境（严格）
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],  # 仅允许特定域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

### 4. 输入验证与防注入

#### SQL 注入防护
```python
# ✅ 使用 ORM（SQLAlchemy）自动防护
from sqlalchemy import select
stmt = select(User).where(User.name == user_input)  # 安全

# ❌ 避免拼接 SQL
query = f"SELECT * FROM users WHERE name = '{user_input}'"  # 危险！
```

#### XSS 防护
```python
# 前端：对用户输入进行转义
import html
safe_content = html.escape(user_input)

# 后端：验证输入格式
from pydantic import BaseModel, validator

class MessageInput(BaseModel):
    content: str

    @validator('content')
    def validate_content(cls, v):
        if len(v) > 1000:
            raise ValueError('消息长度不能超过 1000 字符')
        return v.strip()
```

#### 文件上传安全
```python
# 验证文件类型
ALLOWED_EXTENSIONS = {'.pdf', '.csv', '.xlsx'}

def validate_file(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {ext}")

    # 限制文件大小（10MB）
    if file.size > 10 * 1024 * 1024:
        raise ValueError("文件大小不能超过 10MB")
```

---

### 5. 敏感信息脱敏

#### 日志脱敏
```python
import re
from loguru import logger

def sanitize_log(message: str) -> str:
    """脱敏日志中的敏感信息"""
    # 脱敏 API Key
    message = re.sub(r'sk-[a-zA-Z0-9]{32}', 'sk-***', message)

    # 脱敏手机号
    message = re.sub(r'1[3-9]\d{9}', '***', message)

    # 脱敏身份证号
    message = re.sub(r'\d{17}[\dXx]', '***', message)

    return message

# 使用
logger.info(sanitize_log(f"User API key: {api_key}"))
```

#### 响应数据脱敏
```python
# 不要在 API 响应中返回敏感信息
class UserResponse(BaseModel):
    id: int
    name: str
    # password: str  # ❌ 不要返回密码
    # api_key: str   # ❌ 不要返回 API Key
```

---

### 6. 访问频率限制

#### 使用 slowapi 限流
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 应用到路由
@app.post("/api/chat/message")
@limiter.limit("10/minute")  # 每分钟最多 10 次请求
async def send_message(request: Request):
    pass
```

#### Nginx 限流
```nginx
# 在 nginx.conf 中配置
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    limit_req_status 429;
}
```

---

### 7. WebSocket 安全

#### 连接认证
```python
# 使用 Token 认证 WebSocket 连接
@app.websocket("/api/chat/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # 验证 Token
    if not verify_token(token):
        await websocket.close(code=1008, reason="Invalid token")
        return

    await websocket.accept()
    # ... 处理消息
```

#### 消息大小限制
```python
# 限制 WebSocket 消息大小
MAX_MESSAGE_SIZE = 10 * 1024  # 10KB

async def receive_message(websocket: WebSocket):
    data = await websocket.receive_text()

    if len(data) > MAX_MESSAGE_SIZE:
        await websocket.close(code=1009, reason="Message too large")
        return

    return data
```

---

### 8. 依赖安全

#### 定期更新依赖
```bash
# 检查过期依赖
pip list --outdated

# 更新依赖
pip install --upgrade -r requirements.txt

# 检查安全漏洞
pip install safety
safety check
```

#### 使用依赖锁定
```bash
# 生成精确版本的依赖文件
pip freeze > requirements.lock

# 使用锁定文件安装
pip install -r requirements.lock
```

---

### 9. 错误处理与信息泄露

#### ❌ 错误做法
```python
# 不要暴露详细错误信息
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),  # 可能泄露敏感信息
            "traceback": traceback.format_exc()  # 危险！
        }
    )
```

#### ✅ 正确做法
```python
# 生产环境返回通用错误信息
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    # 记录详细错误到日志
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # 返回通用错误信息
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误，请稍后重试"}
    )
```

---

### 10. 安全检查清单

#### 部署前检查

- [ ] **API Key 管理**
  - [ ] 所有 API Key 使用环境变量
  - [ ] .env 文件已添加到 .gitignore
  - [ ] 生产环境使用独立的 API Key

- [ ] **CORS 配置**
  - [ ] 生产环境限制了允许的域名
  - [ ] 不使用 `allow_origins=["*"]`

- [ ] **HTTPS**
  - [ ] 已配置 SSL 证书
  - [ ] 强制 HTTP 重定向到 HTTPS
  - [ ] 启用 HSTS 头

- [ ] **输入验证**
  - [ ] 所有用户输入都经过验证
  - [ ] 文件上传有类型和大小限制
  - [ ] 使用 Pydantic 模型验证

- [ ] **访问控制**
  - [ ] 数据库文件权限正确（600）
  - [ ] 敏感目录权限正确（700）
  - [ ] 配置了访问频率限制

- [ ] **日志安全**
  - [ ] 日志中不包含 API Key
  - [ ] 日志中不包含密码
  - [ ] 敏感信息已脱敏

- [ ] **依赖安全**
  - [ ] 依赖已更新到最新版本
  - [ ] 运行了安全漏洞扫描
  - [ ] 使用了依赖锁定文件

- [ ] **错误处理**
  - [ ] 生产环境不返回详细错误信息
  - [ ] 错误已记录到日志
  - [ ] 配置了错误监控

- [ ] **备份**
  - [ ] 配置了自动备份
  - [ ] 测试了恢复流程
  - [ ] 备份文件加密存储

- [ ] **监控**
  - [ ] 配置了日志轮转
  - [ ] 配置了资源监控
  - [ ] 配置了异常告警

---

### 11. 安全事件响应

#### 发现 API Key 泄露
```bash
# 1. 立即撤销泄露的 API Key
# 访问 https://dashscope.console.aliyun.com/ 删除密钥

# 2. 生成新的 API Key

# 3. 更新环境变量
export DASHSCOPE_API_KEY="new-api-key"

# 4. 重启服务
pm2 restart vividcrowd-backend

# 5. 检查日志，确认是否有异常调用
grep "API" /var/log/vividcrowd/*.log
```

#### 发现异常访问
```bash
# 1. 查看访问日志
tail -f /var/log/nginx/vividcrowd-access.log

# 2. 封禁恶意 IP（Nginx）
# 在 nginx.conf 中添加
deny 192.168.1.100;

# 3. 重载 Nginx
sudo nginx -s reload

# 4. 使用 fail2ban 自动封禁
sudo apt install fail2ban
```

---

## 📊 数据库架构

### 三个独立数据库

本项目采用**三数据库分离架构**，每个业务模块使用独立的 SQLite 数据库：

#### 1. celebrity.db（数字分身数据库）

| 表名 | 用途 |
|------|------|
| `knowledge_sources` | 名人/专家档案 |
| `celebrity_chunks` | 文档分块与 Embedding |
| `chat_sessions` | 会话记录 |
| `chat_messages` | 对话消息 |

**关键字段 (knowledge_sources):**
```sql
id, name, source_type, author, birth_year, death_year,
nationality, occupation, biography, famous_works, famous_quotes,
personality_traits, speech_style, system_prompt, raw_content
```

#### 2. customerService.db（客服数据库）

| 表名 | 用途 |
|------|------|
| `customer_service_qa` | QA 知识库 |
| `customer_service_sessions` | 会话记录 |
| `customer_service_logs` | 对话日志 |
| `csv_registry` | CSV 文件去重注册 |

**关键字段 (customer_service_qa):**
```sql
id, question_count, topic_name, typical_question,
standard_script, risk_notes, keywords, embedding, created_at
```

#### 3. digital_customer.db（销售演练数据库）

| 表名 | 用途 |
|------|------|
| `customer_profiles` | 客户画像档案 |
| `customer_chunks` | 客户档案分块 |
| `training_sessions` | 培训会话 |
| `conversation_rounds` | 对话轮次记录 |
| `stage_evaluations` | 阶段评价 |
| `final_evaluations` | 综合评价报告 |
| `sales_knowledge` | 销售知识库 |
| `customer_profile_registry` | 客户档案去重注册 |

**关键字段 (training_sessions):**
```sql
id, customer_id, user_id, current_stage, stage_completion_rates,
start_time, end_time, status
```

---

## 🎯 使用场景

| 场景 | 推荐模式 | 说明 |
|------|---------|------|
| 娱乐社交 | 智能群聊 | 与虚拟群友闲聊、讨论 |
| 学习研究 | 数字分身（私聊） | 与历史人物、书籍、专家深度对话 |
| 头脑风暴 | 数字分身（群聊） | 多位专家思想碰撞 |
| 企业客服 | 数字客服 | 基于知识库的智能问答 |
| 产品咨询 | 数字客服 | 标准话术 + 智能引导 |
| 销售培训 | 销售演练 | 模拟真实客户，实战演练销售技巧 |
| 话术优化 | 销售演练 + AI 助手 | 获取实时建议，优化沟通策略 |

---

## 🤝 参与贡献

欢迎提交 Pull Requests！请确保：

1. Python 代码符合 PEP 8 规范
2. 新功能包含必要的测试
3. 更新相关文档
4. **不要**提交包含敏感信息的配置文件

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [阿里云 DashScope](https://dashscope.console.aliyun.com/) - LLM 和 Embedding 服务
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Web 框架
- [React](https://react.dev/) - 前端 UI 框架
- [Material-UI](https://mui.com/) - UI 组件库

---

## ❓ 常见问题 FAQ

### 1. 如何更换 LLM 模型？

**问题：** 我想使用其他 Qwen 模型或调整模型配置。

**解答：**
```python
# 编辑 backend/core/config.py
MODEL_NAME = "qwen-max"           # 主回复模型（可选：qwen-plus, qwen-turbo）
ROUTER_MODEL_NAME = "qwen-turbo"  # 路由模型（建议使用 turbo 降低成本）
EVALUATION_MODEL = "qwen-plus"    # 评价模型

# 重启后端服务生效
```

**模型选择建议：**
- `qwen-max`：最强性能，适合复杂对话和评价
- `qwen-plus`：性价比高，适合一般场景
- `qwen-turbo`：速度快成本低，适合路由和简单任务

---

### 2. 如何添加新的群聊 Agent？

**问题：** 我想在智能群聊中添加自定义角色。

**解答：**
```json
// 编辑 backend/agents_profiles.json，添加新 Agent
{
  "id": "custom_agent",
  "name": "自定义角色",
  "age": 25,
  "occupation": "职业描述",
  "personality_traits": ["性格特点1", "性格特点2"],
  "interests": ["兴趣1", "兴趣2", "兴趣3"],
  "speech_style": "说话风格描述",
  "expertise": ["专业领域1", "专业领域2"]
}
```

**注意事项：**
- `id` 必须唯一
- `expertise` 字段用于 LLM 路由匹配
- 重启后端服务后生效
- 建议先测试 Agent 回复质量

---

### 3. 如何导入自定义客服知识库？

**问题：** 我有自己的客服 QA 数据，如何导入系统？

**解答：**

**方法一：CSV 导入（推荐）**
```csv
question_count,topic_name,typical_question,standard_script,risk_notes
15,产品退换货,如何申请退货？,您可以在订单页面点击退货按钮...,退货需在7天内
```

**CSV 格式要求：**
- 必须包含 5 列（顺序固定）
- 使用 UTF-8 编码
- 第一行为标题行（会被跳过）

**方法二：API 导入**
```bash
curl -X POST http://localhost:8000/api/customer-service/qa/import \
  -F "file=@knowledge.csv"
```

**导入后验证：**
```bash
# 查看 QA 记录数
curl http://localhost:8000/api/customer-service/qa/count
```

---

### 4. 数据库文件在哪里？

**问题：** 我想备份或查看数据库。

**解答：**

数据库文件位于 `backend/data/` 目录：

```bash
backend/data/
├── celebrity.db           # 数字分身数据（名人档案、对话记录）
├── customerService.db     # 客服数据（QA知识库、会话记录）
└── digital_customer.db    # 销售演练数据（客户档案、培训记录）
```

**查看数据库内容：**
```bash
# 安装 sqlite3
# Windows: 下载 https://www.sqlite.org/download.html
# Linux: sudo apt install sqlite3
# Mac: brew install sqlite3

# 打开数据库
sqlite3 backend/data/celebrity.db

# 查看所有表
.tables

# 查询数据
SELECT * FROM knowledge_sources;

# 退出
.quit
```

---

### 5. 如何备份数据？

**问题：** 如何备份系统数据以防丢失？

**解答：**

**方法一：直接复制数据库文件**
```bash
# 备份所有数据库
cp -r backend/data backend/data_backup_$(date +%Y%m%d)

# Windows
xcopy backend\data backend\data_backup_%date:~0,4%%date:~5,2%%date:~8,2% /E /I
```

**方法二：导出 SQL 脚本**
```bash
# 导出数据库为 SQL 文件
sqlite3 backend/data/celebrity.db .dump > celebrity_backup.sql

# 恢复数据
sqlite3 backend/data/celebrity.db < celebrity_backup.sql
```

**自动备份脚本（Linux/Mac）：**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp backend/data/*.db $BACKUP_DIR/
echo "Backup completed: $BACKUP_DIR"
```

**建议：**
- 定期备份（每周或每月）
- 保留多个版本
- 测试恢复流程

---

### 6. 支持哪些 LLM 提供商？

**问题：** 除了阿里云 DashScope，还能用其他 LLM 吗？

**解答：**

**当前支持：**
- ✅ **阿里云 DashScope**（Qwen 系列）- 默认且推荐
- ✅ **OpenAI API**（需修改代码）

**如何切换到 OpenAI：**
```python
# backend/core/config.py
USE_OPENAI = True
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"

# 修改相关服务代码，将 dashscope 调用替换为 openai 调用
```

**其他提供商：**
- 理论上支持任何兼容 OpenAI API 的服务
- 需要修改 `backend/apps/*/services/` 中的模型调用代码
- 建议保持 Embedding 服务使用 DashScope（中文效果好）

---

### 7. 如何调整群聊活跃度？

**问题：** 群聊太活跃或太冷清，如何调整？

**解答：**
```python
# 编辑 backend/core/config.py

# 调整每轮最多回复人数
MAX_AGENTS_PER_ROUND = 3  # 默认3人，可改为 1-5

# 调整随机回复概率
RANDOM_RESPONSE_PROBABILITY = 0.3  # 30%概率触发闲聊

# 调整深夜模式
NIGHT_MODE_START_HOUR = 23  # 深夜开始时间
NIGHT_MODE_END_HOUR = 7     # 深夜结束时间
NIGHT_MODE_PROBABILITY = 0.2  # 深夜活跃度降至20%

# 调整打字延迟（模拟真人思考）
MIN_TYPING_DELAY = 8.0   # 最小延迟（秒）
MAX_TYPING_DELAY = 10.0  # 最大延迟（秒）
```

**效果对比：**
- 提高活跃度：增加 `MAX_AGENTS_PER_ROUND` 和 `RANDOM_RESPONSE_PROBABILITY`
- 降低活跃度：减少上述参数，或增加 `MIN_TYPING_DELAY`

---

### 8. 如何自定义销售演练评价标准？

**问题：** 我想修改销售演练的评分维度和标准。

**解答：**
```python
# 编辑 backend/apps/digital_customer/services/training/evaluation_engine.py

# 修改评分维度
SCORING_CRITERIA = {
    "trust": "信任与关系建立",
    "needs": "需求诊断",
    "value": "价值呈现",
    "objection": "异议处理",
    "closing": "成交推进",
    # 可添加自定义维度
    "custom": "自定义维度"
}

# 修改评分提示词
EVALUATION_PROMPT = """
请根据以下标准评价销售人员的表现：
1. 信任建立：是否建立良好的沟通氛围
2. 需求诊断：是否准确识别客户痛点
... (自定义评价标准)
"""
```

**修改阶段流程：**
```python
# 编辑 backend/apps/digital_customer/services/training/stage_controller.py

STAGES = {
    1: {"name": "信任建立", "description": "..."},
    2: {"name": "需求诊断", "description": "..."},
    # 可添加或修改阶段
}
```

---

### 9. 如何提高客服系统的匹配准确率？

**问题：** 客服系统经常匹配不到正确答案。

**解答：**

**方法一：调整置信度阈值**
```python
# backend/core/config.py
HIGH_CONFIDENCE_THRESHOLD = 0.9  # 降低到 0.85
MID_CONFIDENCE_THRESHOLD = 0.6   # 降低到 0.5
```

**方法二：调整混合检索权重**
```python
# backend/core/config.py
BM25_WEIGHT = 0.6        # 关键词匹配权重（可调整为 0.5-0.7）
EMBEDDING_WEIGHT = 0.4   # 语义匹配权重（可调整为 0.3-0.5）
```

**方法三：优化知识库质量**
- 增加同义问法（一个答案对应多个问题）
- 丰富关键词（在 `typical_question` 中包含常见表达）
- 标准化术语（统一专业名词）

**方法四：查看匹配日志**
```python
# 在 backend/apps/customer_service/services/qa_matcher.py 中
# 启用详细日志查看匹配过程
logger.debug(f"BM25 score: {bm25_score}, Embedding score: {embedding_score}")
```

---

### 10. 数字分身回复太长或太短怎么办？

**问题：** 数字分身的回复长度不符合预期。

**解答：**
```python
# 编辑 backend/apps/celebrity/services/celebrity_agent.py

# 在 System Prompt 中添加长度控制
system_prompt = f"""
你是 {celebrity.name}...

回复要求：
- 私聊模式：回复长度控制在 100-200 字
- 群聊模式：回复长度控制在 30-50 字以内
- 避免过度展开，保持简洁有力
"""
```

**动态调整：**
```python
# 根据模式动态设置
if mode == "private":
    max_tokens = 300  # 私聊允许更长回复
else:
    max_tokens = 100  # 群聊限制长度
```

---

### 11. 如何查看系统日志？

**问题：** 遇到问题时如何查看详细日志？

**解答：**

**后端日志：**
```bash
# 日志默认输出到控制台
# 查看实时日志
uvicorn app.main:app --reload

# 保存日志到文件
uvicorn app.main:app --reload > logs/backend.log 2>&1
```

**配置日志级别：**
```python
# backend/core/config.py
LOG_LEVEL = "DEBUG"  # DEBUG/INFO/WARNING/ERROR
```

**前端日志：**
```javascript
// 浏览器控制台（F12）
// 查看 WebSocket 连接状态
console.log("WebSocket status:", readyState);

// 查看 API 请求
// Network 标签页
```

---

### 12. 系统支持多用户并发吗？

**问题：** 多个用户同时使用会有问题吗？

**解答：**

**当前状态：**
- ✅ 支持多用户并发访问
- ✅ 每个 WebSocket 连接独立管理
- ✅ 数据库支持并发读写（SQLite 有写锁限制）

**并发限制：**
- SQLite 写并发有限（建议 < 10 并发写入）
- 高并发场景建议切换到 PostgreSQL/MySQL

**切换到 PostgreSQL：**
```python
# backend/core/config.py
DATABASE_URL = "postgresql://user:password@localhost/vividcrowd"

# 安装依赖
pip install asyncpg

# 修改 database.py 中的引擎配置
```

---

## 📬 联系方式

如有问题或建议，请提交 [Issue](https://github.com/your-username/VividCrowd/issues) 或发起 [Discussion](https://github.com/your-username/VividCrowd/discussions)。
