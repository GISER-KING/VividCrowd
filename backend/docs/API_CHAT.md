# 群聊模块 API 文档

## 概述

群聊模块提供多 Agent 智能对话功能，支持多个 AI 角色同时参与讨论。

**基础路径**: `/api/chat`

---

## WebSocket 接口

### 连接地址

```
ws://{host}:{port}/api/chat/ws
```

### 消息格式

#### 发送消息（客户端 → 服务端）

```json
{
    "message": "用户消息内容",
    "agent_ids": [1, 2, 3]  // 可选，指定参与的 Agent ID 列表
}
```

#### 接收消息（服务端 → 客户端）

**流式开始**
```json
{
    "type": "stream_start",
    "sender": "Agent 名称",
    "content": ""
}
```

**流式内容**
```json
{
    "type": "stream_chunk",
    "sender": "Agent 名称",
    "content": "增量文本内容"
}
```

**流式结束**
```json
{
    "type": "stream_end",
    "sender": "Agent 名称",
    "content": ""
}
```

**错误消息**
```json
{
    "type": "error",
    "sender": "System",
    "content": "错误描述"
}
```

---

## HTTP 接口

### 获取所有 Agent 列表

**请求**
```
GET /api/chat/agents
```

**响应**
```json
[
    {
        "id": 1,
        "name": "Agent 名称",
        "avatar": "头像 URL",
        "system_prompt": "系统提示词"
    }
]
```

---

## 使用示例

### JavaScript WebSocket 示例

```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws');

ws.onopen = () => {
    console.log('连接成功');
    ws.send(JSON.stringify({
        message: '你好，大家对 AI 的未来有什么看法？',
        agent_ids: [1, 2, 3]
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch (data.type) {
        case 'stream_start':
            console.log(`${data.sender} 开始回复...`);
            break;
        case 'stream_chunk':
            process.stdout.write(data.content);
            break;
        case 'stream_end':
            console.log(`\n${data.sender} 回复完成`);
            break;
        case 'error':
            console.error(`错误: ${data.content}`);
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

## 注意事项

1. WebSocket 连接建立后会自动进入群聊模式
2. 每个 Agent 会依次回复，回复之间有短暂延迟
3. 如果不指定 `agent_ids`，将使用所有可用的 Agent
4. 消息历史会在服务端维护，支持上下文连续对话
