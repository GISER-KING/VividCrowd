# 数字分身模块 API 文档

## 概述

数字分身模块支持上传 PDF 文档创建名人/书籍/专题的数字分身，并通过 WebSocket 进行对话交互。

**基础路径**: `/api/celebrity`

---

## HTTP 接口

### 获取所有名人列表

**请求**
```
GET /api/celebrity/
```

**响应**
```json
[
    {
        "id": 1,
        "name": "名人姓名",
        "source_type": "person",
        "author": null,
        "birth_year": 1879,
        "death_year": 1955,
        "nationality": "德裔美籍",
        "occupation": "物理学家",
        "biography": "简介...",
        "famous_works": "代表作品...",
        "famous_quotes": "名言...",
        "personality_traits": "性格特点",
        "speech_style": "说话风格",
        "created_at": "2024-01-01T00:00:00"
    }
]
```

---

### 获取名人详情

**请求**
```
GET /api/celebrity/{celebrity_id}
```

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| celebrity_id | int | 是 | 名人 ID |

**响应**
```json
{
    "id": 1,
    "name": "名人姓名",
    "source_type": "person",
    "biography": "简介...",
    ...
}
```

**错误响应**
```json
{
    "detail": "名人不存在"
}
```

---

### 上传 PDF 创建名人

**请求**
```
POST /api/celebrity/upload
Content-Type: multipart/form-data
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | PDF 文件 |
| source_type | string | 否 | 类型：person/book/topic，默认 person |

**响应**
```json
{
    "id": 1,
    "name": "解析出的名称",
    "source_type": "person",
    "biography": "AI 提取的简介...",
    ...
}
```

**错误响应**
```json
{
    "detail": "只支持 PDF 文件"
}
```

---

### 删除名人

**请求**
```
DELETE /api/celebrity/{celebrity_id}
```

**路径参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| celebrity_id | int | 是 | 名人 ID |

**响应**
```json
{
    "message": "删除成功"
}
```

---

## WebSocket 接口

### 连接地址

```
ws://{host}:{port}/api/celebrity/ws
```

### 消息格式

#### 发送消息（客户端 → 服务端）

```json
{
    "message": "用户消息内容",
    "celebrity_ids": [1, 2],  // 选中的名人 ID 列表
    "mode": "private"         // 对话模式：private(一对一) / group(群聊)
}
```

#### 接收消息（服务端 → 客户端）

**流式开始**
```json
{
    "type": "stream_start",
    "sender": "爱因斯坦",
    "content": ""
}
```

**流式内容**
```json
{
    "type": "stream_chunk",
    "sender": "爱因斯坦",
    "content": "增量文本内容"
}
```

**流式结束**
```json
{
    "type": "stream_end",
    "sender": "爱因斯坦",
    "content": ""
}
```

**错误消息**
```json
{
    "type": "error",
    "sender": "System",
    "content": "请先选择一位名人进行对话"
}
```

---

## 对话模式说明

### private（一对一模式）
- 只有第一个选中的名人会回复
- 适合深度对话和详细讨论
- 回复较为详细（100-200字）

### group（群聊模式）
- 所有选中的名人依次回复
- 每个名人给出独特视角
- 回复较为简短（50字以内）
- 名人之间会有 0.5 秒的回复间隔

---

## 使用示例

### 上传 PDF 文件

```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('source_type', 'person');

const response = await fetch('http://localhost:8000/api/celebrity/upload', {
    method: 'POST',
    body: formData
});

const celebrity = await response.json();
console.log('创建成功:', celebrity.name);
```

### WebSocket 对话

```javascript
const ws = new WebSocket('ws://localhost:8000/api/celebrity/ws');

ws.onopen = () => {
    // 一对一私聊
    ws.send(JSON.stringify({
        message: '请问您对相对论的核心思想是什么？',
        celebrity_ids: [1],
        mode: 'private'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'stream_chunk') {
        // 显示流式内容
        appendMessage(data.sender, data.content);
    }
};
```

---

## source_type 说明

| 类型 | 说明 | 生成的 System Prompt 特点 |
|------|------|--------------------------|
| person | 人物传记 | 以第一人称扮演该人物 |
| book | 书籍 | 作为书籍的化身，以作者视角回答 |
| topic | 课程/专题 | 作为课程 AI 助教回答问题 |

---

## 注意事项

1. 上传的 PDF 文件会保存在服务器的 `uploads/` 目录
2. PDF 解析使用 LLM 提取结构化信息，可能需要几秒钟
3. 删除名人时会同时删除关联的 PDF 文件
4. WebSocket 连接会维护对话历史，支持上下文连续对话
