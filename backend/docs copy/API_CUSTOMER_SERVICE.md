# 数字客服模块 API 文档

## 概述

数字客服模块提供智能客服问答功能，基于 BM25 + Embedding 混合匹配和 LLM 约束生成技术。

**基础路径**: `/api/customer-service`

---

## 核心特性

1. **三层匹配架构**
   - BM25 关键词匹配（权重 60%）
   - Embedding 语义匹配（权重 40%）
   - 混合评分决定置信度

2. **三级响应策略**
   - 高置信度（≥0.9）：直接返回标准话术
   - 中置信度（0.6-0.9）：LLM 改写话术
   - 低置信度（<0.6）：引导用户重新描述

3. **会话管理**
   - 自动创建会话
   - 对话历史记录
   - 用户评分系统

---

## HTTP 接口

### 获取系统统计

**请求**
```
GET /api/customer-service/stats
```

**响应**
```json
{
    "analytics": {
        "total_sessions": 100,
        "total_messages": 500,
        "avg_confidence": 0.75,
        "transfer_rate": 5.5,
        "avg_rating": 4.2,
        "match_type_distribution": {
            "high_confidence": 200,
            "mid_confidence": 250,
            "low_confidence": 50
        }
    },
    "matcher": {
        "total_qa_records": 150,
        "embedding_dim": 1536,
        "is_loaded": true,
        "high_confidence_threshold": 0.9,
        "mid_confidence_threshold": 0.6,
        "bm25_weight": 0.6,
        "embedding_weight": 0.4
    }
}
```

---

### 获取 QA 记录数量

**请求**
```
GET /api/customer-service/qa/count
```

**响应**
```json
{
    "count": 150
}
```

---

### 创建会话

**请求**
```
POST /api/customer-service/session
```

**响应**
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 获取会话历史

**请求**
```
GET /api/customer-service/session/{session_id}/history
```

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话 ID（UUID） |

**响应**
```json
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "messages": [
        {
            "user_query": "孩子挑食怎么办？",
            "bot_response": "回复内容...",
            "match_type": "high_confidence",
            "confidence": 0.92,
            "timestamp": "2024-01-01T10:30:00"
        }
    ]
}
```

---

### 设置会话评分

**请求**
```
POST /api/customer-service/session/{session_id}/rating?rating=5
```

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话 ID |

**查询参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| rating | int | 是 | 评分（1-5） |

**响应**
```json
{
    "message": "评分成功"
}
```

**错误响应**
```json
{
    "detail": "评分必须在1-5之间"
}
```

---

## WebSocket 接口

### 连接地址

```
ws://{host}:{port}/api/customer-service/ws
```

### 连接流程

1. 客户端连接 WebSocket
2. 服务端自动创建会话并返回 `session_created` 消息
3. 客户端发送问题
4. 服务端返回回答

### 消息格式

#### 会话创建（服务端 → 客户端）

连接成功后自动发送：
```json
{
    "type": "session_created",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 发送问题（客户端 → 服务端）

**非流式模式**
```json
{
    "message": "孩子挑食怎么办？",
    "stream": false
}
```

**流式模式**
```json
{
    "message": "孩子挑食怎么办？",
    "stream": true
}
```

#### 接收回答（服务端 → 客户端）

**非流式响应**
```json
{
    "type": "response",
    "response": "回复内容...",
    "confidence": 0.85,
    "match_type": "mid_confidence",
    "transfer_to_human": false,
    "matched_topic": "挑食问题"
}
```

**流式响应 - 元数据**
```json
{
    "type": "metadata",
    "confidence": 0.85,
    "match_type": "mid_confidence",
    "transfer_to_human": false,
    "matched_topic": "挑食问题"
}
```

**流式响应 - 内容块**
```json
{
    "type": "chunk",
    "content": "增量文本内容"
}
```

**流式响应 - 结束**
```json
{
    "type": "end"
}
```

**错误响应**
```json
{
    "type": "error",
    "content": "消息不能为空"
}
```

---

## 匹配类型说明

| match_type | 置信度范围 | 响应策略 |
|------------|-----------|----------|
| high_confidence | ≥0.9 | 直接返回标准话术 |
| mid_confidence | 0.6-0.9 | LLM 改写话术 |
| low_confidence | <0.6 | 引导用户重新描述 |
| no_match | 0 | 无匹配，建议转人工 |

---

## 转人工条件

以下情况会触发 `transfer_to_human: true`：

1. **用户明确要求**：消息包含「人工」「转人工」「客服」「真人」等关键词
2. **用户表达不满**：消息包含「不满意」「投诉」「差评」「退款」等关键词

---

## 使用示例

### WebSocket 完整示例

```javascript
const ws = new WebSocket('ws://localhost:8000/api/customer-service/ws');

let sessionId = null;

ws.onopen = () => {
    console.log('连接成功，等待会话创建...');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
        case 'session_created':
            sessionId = data.session_id;
            console.log('会话已创建:', sessionId);

            // 发送第一条消息（流式模式）
            ws.send(JSON.stringify({
                message: '孩子挑食怎么办？',
                stream: true
            }));
            break;

        case 'metadata':
            console.log(`匹配类型: ${data.match_type}, 置信度: ${data.confidence}`);
            if (data.transfer_to_human) {
                console.log('建议转人工客服');
            }
            break;

        case 'chunk':
            process.stdout.write(data.content);
            break;

        case 'end':
            console.log('\n回复结束');
            break;

        case 'response':
            // 非流式响应
            console.log('回复:', data.response);
            console.log('置信度:', data.confidence);
            break;

        case 'error':
            console.error('错误:', data.content);
            break;
    }
};

ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);
};

ws.onclose = () => {
    console.log('连接关闭');
};
```

---

## CSV 数据导入

### CSV 文件格式

```csv
提问次数,主题名称,典型提问,标准话术,风险注意事项
100,挑食问题,孩子挑食怎么办？,家长您好，孩子挑食是常见问题...,如症状严重请就医
```

### 自动导入

将 CSV 文件放入 `backend/uploads/csv/` 目录，系统启动时会自动导入。

**导入特性**：
- 基于文件 MD5 哈希去重，相同文件不会重复导入
- 文件变更后会自动重新导入
- 自动生成 jieba 分词关键词（用于 BM25）
- 自动生成 Embedding 向量（用于语义匹配）

---

## 注意事项

1. 系统启动时会自动初始化 QA 匹配引擎，首次启动可能需要几秒钟
2. 需要配置 `DASHSCOPE_API_KEY` 环境变量用于 Embedding 和 LLM 调用
3. WebSocket 断开连接时会自动结束会话
4. 会话历史和日志会持久化到数据库
