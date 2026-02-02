# 数字客服系统技术文档

## 目录
- [系统概述](#系统概述)
- [系统架构](#系统架构)
- [代码结构](#代码结构)
- [核心功能](#核心功能)
- [数据流](#数据流)
- [多轮对话逻辑](#多轮对话逻辑)
- [API接口](#api接口)
- [配置与部署](#配置与部署)

---

## 系统概述

数字客服是一个基于知识库的智能客服系统，采用**三层混合匹配策略**，实现高度遵循话术的智能回复。

### 设计理念

与传统的"让LLM自由发挥"不同，本系统采用**代码控制流程，LLM只负责改写**的设计：

| 传统方案 | 本系统方案 |
|---------|-----------|
| LLM自己决定是否调用知识库 | 代码强制匹配知识库 |
| LLM自己判断回复内容 | 根据置信度分层处理 |
| 话术遵循靠Prompt祈祷 | 高置信度直接返回原文 |
| 转人工由LLM模糊判断 | 代码硬性规则判断 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (React)                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ CustomerService │  │ useCustomerSer- │  │    config.js    │  │
│  │    Page.jsx     │◄─┤   viceWS.js     │◄─┤  (WebSocket配置) │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端 (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                      main.py                            │    │
│  │  /ws/customer-service (WebSocket)                       │    │
│  │  /customer-service/import-csv (REST)                    │    │
│  │  /customer-service/analytics (REST)                     │    │
│  └───────────────────────────┬─────────────────────────────┘    │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              CustomerServiceOrchestrator                │    │
│  │                   (编排器 - 核心协调)                     │    │
│  └───┬───────────────────┬───────────────────┬─────────────┘    │
│      ▼                   ▼                   ▼                  │
│  ┌─────────┐      ┌─────────────┐      ┌─────────────┐          │
│  │QAMatcher│      │Response     │      │Session      │          │
│  │(匹配引擎)│      │Generator    │      │Manager      │          │
│  │         │      │(回复生成器)  │      │(会话管理)    │          │
│  └────┬────┘      └──────┬──────┘      └──────┬──────┘          │
│       │                  │                    │                 │
│       │                  ▼                    │                 │
│       │           ┌─────────────┐             │                 │
│       │           │  Qwen LLM   │             │                 │
│       │           │ (qwen-turbo)│             │                 │
│       │           └─────────────┘             │                 │
│       ▼                                       ▼                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SQLite 数据库                         │    │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌────────────┐ │    │
│  │  │CustomerServiceQA│ │CustomerService  │ │CustomerSer-│ │    │
│  │  │   (QA知识库)     │ │Session (会话)   │ │viceLog(日志)│ │    │
│  │  └─────────────────┘ └─────────────────┘ └────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 代码结构

### 后端文件

```
backend/app/
├── main.py                          # API入口，WebSocket和REST端点
├── db/
│   └── models.py                    # 数据库模型定义
└── services/
    └── customer_service/
        ├── __init__.py
        ├── orchestrator.py          # 编排器：协调所有组件
        ├── qa_matcher.py            # 匹配引擎：BM25 + TF-IDF
        ├── response_generator.py    # 回复生成器：LLM约束生成
        ├── session_manager.py       # 会话管理：状态和日志
        └── excel_importer.py        # 数据导入：CSV解析和向量化
```

### 前端文件

```
frontend/src/
├── config.js                        # WebSocket配置
├── App.jsx                          # 路由配置
├── components/
│   └── Sidebar.jsx                  # 导航栏（含客服入口）
├── pages/
│   └── CustomerServicePage.jsx      # 客服聊天界面
└── hooks/
    └── useCustomerServiceWS.js      # WebSocket连接Hook
```

### 各文件职责

| 文件 | 职责 |
|------|------|
| `orchestrator.py` | 核心协调器，串联匹配、生成、会话管理 |
| `qa_matcher.py` | BM25+TF-IDF混合匹配，置信度计算 |
| `response_generator.py` | 根据置信度选择策略，LLM约束生成 |
| `session_manager.py` | 会话创建、日志记录、统计分析 |
| `excel_importer.py` | CSV解析、分词、TF-IDF向量化 |
| `models.py` | SQLAlchemy数据模型定义 |
| `useCustomerServiceWS.js` | WebSocket连接、消息收发、状态管理 |
| `CustomerServicePage.jsx` | 聊天UI、消息展示、快捷回复 |

---

## 核心功能

### 1. 三层混合匹配

```
用户问题: "孩子挑食怎么办？"
    │
    ▼
┌─────────────────────────────────────────┐
│ 第1层: BM25关键词匹配 (权重60%)          │
│ - jieba分词: ["孩子", "挑食", "怎么办"]  │
│ - 与QA库的keywords计算BM25分数          │
│ - 捕获精准关键词匹配                     │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 第2层: TF-IDF语义匹配 (权重40%)          │
│ - 用户问题向量化                         │
│ - 与QA库的embedding计算余弦相似度        │
│ - 捕获语义相近的问法                     │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 第3层: 混合评分                          │
│ score = 0.6 × BM25 + 0.4 × Embedding    │
└─────────────────────────────────────────┘
```

### 2. 置信度分层策略

| 置信度范围 | 类型 | 处理策略 | 是否调用LLM |
|-----------|------|---------|------------|
| ≥ 0.9 | high_confidence | 直接返回标准话术 + 风险提示 | 否 |
| 0.6 - 0.9 | mid_confidence | LLM严格改写话术 | 是 |
| < 0.6 | low_confidence | LLM尝试理解 + 引导沟通 | 是 |
| 无匹配 | no_match | 返回引导消息 | 否 |

### 3. 转人工判断

**仅在以下情况转人工（代码硬性规则）：**

```python
# 条件1: 用户明确要求
transfer_keywords = ['人工', '转人工', '客服', '真人', '人工客服', '转接']

# 条件2: 用户表达不满
dissatisfaction_keywords = ['不满意', '投诉', '差评', '退款', '不行', '太差', '垃圾']
```

**注意**：
- 低置信度不会自动转人工，而是继续引导沟通
- `risk_notes` 是回复的上下文提示，不是转人工依据

### 4. 流式回复

WebSocket实时推送，用户可以看到逐字生成效果：

```
消息类型:
├── session_created  → 会话创建通知
├── metadata         → 匹配元数据（置信度、类型）
├── chunk            → 回复内容片段
├── end              → 流式结束
└── error            → 错误信息
```

---

## 数据流

### 1. 数据上传流程

```
CSV文件 (用户上传)
    │
    ▼
┌─────────────────────────────────────────┐
│ POST /customer-service/import-csv       │
│ - 保存文件到服务器                        │
│ - 调用 excel_importer.py                │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ excel_importer.py                       │
│ 1. 读取CSV (pandas)                     │
│ 2. 解析5列数据                           │
│ 3. jieba分词提取keywords                 │
│ 4. TF-IDF向量化生成embedding             │
│ 5. 批量插入数据库                        │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ SQLite: customer_service_qa 表          │
│ - id, question_count, topic_name        │
│ - typical_question, standard_script     │
│ - risk_notes, keywords, embedding       │
└─────────────────────────────────────────┘
```

### 2. CSV数据格式

| 列号 | 字段名 | 说明 | 示例 |
|-----|-------|------|------|
| 1 | question_count | 提问次数 | 15 |
| 2 | topic_name | 主题名称 | 孩子挑食不吃蔬菜 |
| 3 | typical_question | 典型提问 | 孩子不爱吃蔬菜怎么办？ |
| 4 | standard_script | 标准话术 | 可以尝试将蔬菜切碎... |
| 5 | risk_notes | 风险注意事项 | 长期拒食可能导致... |

### 3. 数据入库处理

```python
# excel_importer.py 核心逻辑

# 1. 分词提取关键词 (用于BM25)
keywords = " ".join(jieba.lcut(typical_question + " " + topic_name))

# 2. TF-IDF向量化 (用于语义匹配)
vectorizer = TfidfVectorizer(tokenizer=jieba.lcut, max_features=512)
embeddings = vectorizer.fit_transform(all_questions)

# 3. 存入数据库
qa = CustomerServiceQA(
    topic_name=row['主题名称'],
    typical_question=row['典型提问'],
    standard_script=row['标准话术'],
    risk_notes=row['风险注意事项'],
    keywords=keywords,
    embedding=embedding.tobytes()  # numpy数组序列化
)
```

### 4. 数据更新机制

```
重新上传CSV
    │
    ▼
clear_existing=True (默认)
    │
    ├── 清空现有QA数据
    ├── 重新导入所有数据
    └── 重新初始化匹配引擎
```

### 5. 查询时数据处理

```
用户问题
    │
    ▼
┌─────────────────────────────────────────┐
│ QAMatcher.match()                       │
│ 1. jieba分词用户问题                     │
│ 2. 计算BM25分数 (与所有QA的keywords)     │
│ 3. 计算Embedding相似度                   │
│ 4. 混合评分 + 排序                       │
│ 5. 返回 (qa, score, match_type)         │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ ResponseGenerator.generate_response()   │
│ - high: 直接返回 standard_script        │
│ - mid: LLM改写 (约束Prompt)             │
│ - low: LLM引导                          │
└─────────────────────────────────────────┘
```

---

## 多轮对话逻辑

### 会话生命周期

```
1. 用户连接WebSocket
       │
       ▼
2. 服务端创建Session (UUID)
   └── 存入 customer_service_sessions 表
       │
       ▼
3. 用户发送消息
       │
       ▼
4. 匹配 → 生成 → 流式返回
   └── 记录到 customer_service_logs 表
       │
       ▼
5. 重复步骤3-4 (多轮对话)
       │
       ▼
6. 用户断开连接
   └── 更新Session状态
```

### 单轮对话处理流程

```
用户消息: "孩子挑食怎么办？"
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. Orchestrator.handle_query_stream()   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 2. QAMatcher.match()                    │
│    - BM25匹配                           │
│    - Embedding匹配                      │
│    - 返回: (qa, 0.85, 'mid_confidence') │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 3. 判断是否转人工                        │
│    should_transfer_to_human() → False   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 4. 发送 metadata                        │
│    {type: 'metadata', confidence: 0.85} │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 5. ResponseGenerator.generate_stream()  │
│    - mid_confidence → LLM改写           │
│    - Prompt包含: 用户问题 + 标准话术     │
│    - 流式生成回复                        │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 6. 逐chunk发送                          │
│    {type: 'chunk', content: '家长...'}  │
│    {type: 'chunk', content: '可以...'}  │
│    ...                                  │
│    {type: 'end'}                        │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ 7. SessionManager.log_message()         │
│    - 记录对话日志                        │
│    - 更新会话统计                        │
└─────────────────────────────────────────┘
```

### 会话数据结构

```python
# 会话表 (customer_service_sessions)
{
    "id": 1,
    "session_id": "aabd980d-a5e3-42c0-a94d-d19b715732f5",
    "start_time": "2026-01-20 00:53:00",
    "message_count": 5,
    "avg_confidence": 0.78,
    "transfer_to_human": False,
    "user_rating": None
}

# 对话日志表 (customer_service_logs)
{
    "id": 1,
    "session_id": "aabd980d-...",
    "user_query": "孩子挑食怎么办？",
    "bot_response": "家长，可以尝试...",
    "matched_qa_id": 42,
    "match_type": "mid_confidence",
    "confidence_score": 0.85,
    "response_time_ms": 1523,
    "timestamp": "2026-01-20 00:53:52"
}
```

---

## API接口

### WebSocket端点

**地址**: `ws://localhost:8000/ws/customer-service`

**消息格式**:

```javascript
// 客户端发送
{"message": "用户问题内容"}

// 服务端返回
{"type": "session_created", "session_id": "uuid..."}
{"type": "metadata", "confidence": 0.85, "match_type": "mid_confidence", ...}
{"type": "chunk", "content": "回复内容片段"}
{"type": "end"}
{"type": "error", "content": "错误信息"}
```

### REST API

#### 导入CSV数据
```
POST /customer-service/import-csv
Content-Type: multipart/form-data

参数:
- file: CSV文件
- clear_existing: bool (默认true，是否清空现有数据)

返回:
{
    "success": true,
    "message": "导入完成",
    "total_rows": 499,
    "success_count": 499,
    "error_count": 0
}
```

#### 获取统计分析
```
GET /customer-service/analytics

返回:
{
    "total_sessions": 100,
    "total_messages": 500,
    "avg_confidence": 0.78,
    "transfer_rate": 0.05,
    "avg_rating": 4.2
}
```

#### 获取会话历史
```
GET /customer-service/session/{session_id}/history

返回:
[
    {"user_query": "...", "bot_response": "...", "timestamp": "..."},
    ...
]
```

#### 提交用户评分
```
POST /customer-service/session/{session_id}/rating
Content-Type: multipart/form-data

参数:
- rating: int (1-5)
```

---

## 配置与部署

### 环境变量

```bash
# 阿里云DashScope API密钥 (用于Qwen LLM)
DASHSCOPE_API_KEY=sk-xxxxxxxx
```

### 依赖安装

```bash
# 后端
cd backend
pip install -r requirements.txt

# 关键依赖:
# - rank-bm25: BM25算法
# - jieba: 中文分词
# - scikit-learn: TF-IDF向量化
# - dashscope: 阿里云LLM API
```

### 启动服务

```bash
# 后端
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install
npm run dev
```

### 导入初始数据

1. 访问 http://localhost:8000/docs
2. 找到 `/customer-service/import-csv`
3. 上传CSV文件

---

## 与旧方案对比

| 维度 | 旧方案 (ai_hosting.py) | 新方案 |
|------|----------------------|--------|
| 匹配方式 | 外部LightRAG服务 | 本地BM25+TF-IDF |
| 置信度 | 无 | 有明确分数 |
| 话术遵循 | LLM自由发挥 | 高置信度强制原文 |
| 转人工判断 | LLM模糊判断 | 代码硬性规则 |
| 低置信度处理 | 直接转人工 | 引导继续沟通 |
| 服务依赖 | 需要外部向量库 | 完全本地 |
| 可控性 | 低 | 高 |

**核心改进**: 从"让LLM看着办"变为"代码控制流程，LLM只负责改写"。
