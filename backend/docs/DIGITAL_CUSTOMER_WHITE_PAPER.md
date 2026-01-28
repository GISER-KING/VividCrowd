# VividCrowd 数字客户仿真系统技术白皮书 (v1.0)

## 1. 核心概述 (Executive Summary)

### 1.1 项目背景
在企业销售培训、用户调研及市场洞察等场景中，获取真实的高质量客户样本往往面临成本高、周期长、样本难触达等痛点。传统的角色扮演（Role-Play）培训依赖人工陪练，难以规模化且质量参差不齐。VividCrowd 旨在通过 AIGC 技术构建高保真的“数字客户”（Digital Customer），解决上述问题。

### 1.2 技术愿景
VividCrowd 致力于打造具备“行业认知”、“性格特质”和“决策逻辑”的数字客户孪生体（Digital Twin of Customer）。不仅仅是简单的问答机器人，而是拥有独立价值观、情绪波动和购买决策逻辑的智能体。

### 1.3 核心能力
*   **Persona-Driven Generation (人设驱动生成)**：能够基于非结构化文档（如用户画像描述、访谈记录、PDF 简历）自动化构建立体的人设。
*   **Domain-Specific QA (领域专业问答)**：基于垂直行业知识库（医疗、教育、金融、制造），确保数字客户在专业领域的对话逻辑严谨、术语准确。
*   **Multi-Turn Logic (多轮博弈逻辑)**：具备长期记忆，能够模拟销售过程中的异议处理、价格拉锯和信任建立过程。

---

## 2. 系统架构设计 (System Architecture)

### 2.1 总体架构
系统采用基于 Agent 的微服务架构，前端通过 WebSocket 与后端进行低延迟双向通信。

*   **接入层 (Access Layer)**: React 前端 + WebSocket Gateway，负责音视频流处理与信令交互。
*   **编排层 (Orchestration Layer)**: `CustomerOrchestrator` 负责会话管理、状态分发及多 Agent 协调。
*   **认知层 (Cognitive Layer)**: 包含 `CustomerAgent`（核心推理）、`CustomerRetriever`（知识检索）及 `ProfileParser`（人设解析）。
*   **数据层 (Data Layer)**: PostgreSQL (关系型数据) + Vector Store (向量知识库) + Object Storage (非结构化文档)。

### 2.2 核心模块交互流程
1.  **人设冷启动**: `ProfileParser` 解析上传的 MD/PDF 文件，提取结构化特征（姓名、职位、痛点、预算）存入数据库。
2.  **会话初始化**: `CustomerOrchestrator` 加载人设配置，初始化 `CustomerAgent` 及对话上下文。
3.  **对话循环**:
    *   用户输入 -> `CustomerAgent` 接收消息。
    *   `CustomerRetriever` 并行检索行业知识与历史记忆。
    *   `LLM` 结合 System Prompt、检索结果与当前对话历史生成回复。
    *   `AudioService` (规划中) 将回复转换为带有情绪特征的语音流。

### 2.3 数据流向 (Data Pipeline)
*   **离线处理**: `Raw Data` (MD/PDF) -> `Chunking Service` (切片) -> `Embedding Model` -> `Vector Store`。
*   **在线推理**: `User Query` -> `Embedding` -> `Hybrid Search` (Keyword + Vector) -> `Rerank` -> `LLM Context`.

---

## 3. 核心算法引擎 (Core Algorithm Engine)

### 3.1 动态人设构建 (Dynamic Persona Construction)
*   **静态属性提取**: 利用 LLM 的信息抽取能力，从非结构化文本中精准提取关键字段（如：`pain_points`, `needs`, `objections`, `personality_traits`）。
*   **性格参数化**: 将抽象的性格描述转化为模型参数。
    *   *示例*: “保守严谨” -> `temperature=0.3`, `top_p=0.8`；“开放创新” -> `temperature=0.8`。
    *   **System Prompt 动态注入**: 将性格特征编译为具体的指令集（Instructions），例如“你非常在意价格，除非对方给出明确的 ROI 数据，否则保持怀疑态度”。

### 3.2 领域知识增强生成 (Domain-RAG)
*   **混合检索策略 (Hybrid Search)**: 结合 BM25 关键词检索与 Dense Vector 语义检索。
    *   *解决痛点*: 纯语义检索有时难以精确匹配行业特定的“黑话”或专有名词（如“医保支付改革DRG”）。
*   **上下文重排序 (Rerank)**: 引入 Rerank 模型对初步检索回来的文档块进行相关性打分，确保 Top-K 上下文不仅语义相关，而且逻辑契合。

### 3.3 认知与决策模型 (Cognitive & Decision Model) - *演进方向*
为了突破当前“检索+生成”模式的局限，提升仿真度，我们将引入以下机制：

*   **情绪状态机 (Emotion FSM)**:
    *   维护一个隐式的状态机：`Neutral` -> `Skeptical` -> `Interested` -> `Convinced` -> `Deal`。
    *   用户的每一句话都会触发状态转移概率计算。例如，销售人员未能回答核心异议，状态可能从 `Interested` 回退到 `Skeptical`。
*   **内心独白 (Internal Monologue / Chain of Thought)**:
    *   在生成对外的回复之前，Agent 先进行一轮隐式推理（Hidden Thought）。
    *   *示例*: “（内心独白：这个人虽然态度很好，但他回避了我关于售后的问题，我需要再追问一下。） -> 对外回复：‘不管是多少钱，如果售后跟不上，我们是不会考虑的。’”
*   **反向图灵测试逻辑**:
    *   模拟人类的非理性行为，如基于偏见的决策、故意遗忘之前的承诺、对某些话题表现出不耐烦等。

---

## 4. 语音与多模态交互 (Multimodal Interaction)

### 4.1 语音合成 (TTS) 个性化
*   **声线匹配**: 根据画像中的年龄、性别、职业自动匹配 TTS 音色（如：50岁制造业总监 -> 低沉男声）。
*   **情感驱动**: 未来的 TTS 引擎将接收 LLM 输出的情感标签（如 `<anger>`, `<hesitation>`），生成带有叹气、停顿、语气加重的语音。

### 4.2 实时流式响应 (Streaming Response)
*   优化 WebSocket 协议，实现 ASR (语音转文字) -> LLM Stream -> TTS Stream 的全链路流式处理，将端到端延迟控制在秒级以内，提供接近真人的对话体验。

---

## 5. 工程实现与部署 (Engineering & Deployment)

### 5.1 技术栈
*   **Backend**: Python, FastAPI, SQLAlchemy
*   **LLM**: DashScope (Qwen-Max/Plus)
*   **Database**: PostgreSQL (业务数据), Vector DB (向量数据)
*   **Protocol**: WebSocket, RESTful API

### 5.2 服务治理
*   **Session Management**: `CustomerSessionManager` 负责管理高并发下的会话状态，确保多用户同时训练时的数据隔离。
*   **容错机制**: 针对 LLM 可能产生的幻觉或不符合人设的回复，设计基于规则的后处理（Post-processing）校验层。