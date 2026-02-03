# VividCrowd

> **LLM-Powered Immersive Group Chat Environment + AI Digital Twins + Intelligent Customer Service System**

https://github.com/user-attachments/assets/26936c51-f9d9-4590-896c-8e093f7a41ff

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)

[中文版](README.md)

---

## 📖 Overview

**VividCrowd** is a multi-modal AI conversation platform offering four unique interaction experiences:

| Mode | Description | Features |
|------|-------------|----------|
| **Smart Group Chat** | You're the only human in a virtual group chat with multiple AI Agents | Deep persona simulation, hybrid routing, anti-detection |
| **Digital Twins** | Upload PDFs to create AI digital twins of celebrities/books/courses | Knowledge extraction, private/group chat, digital human video |
| **Digital Customer Service** | Knowledge-base powered intelligent customer service system | BM25+Embedding hybrid matching, confidence-based routing, script control |
| **Sales Training** | Real-time sales training with simulated customers | 5-Stage Process, Real-time Evaluation, AI Assistant, Radar Analysis |

Unlike traditional "Q&A" bots, this project uses sophisticated **orchestration algorithms** and **humanization strategies** to simulate real social intuition and professional service experiences.

---

## 🌟 Core Features

### 1. Smart Group Chat

#### 1.1 Deep Persona Simulation

Each group member is defined in `agents_profiles.json` with a unique personality:

```json
{
  "id": "xiaolin",
  "name": "Xiaolin",
  "age": 22,
  "occupation": "Traditional Chinese Medicine Student",
  "personality_traits": ["warm-hearted", "talkative", "slightly superstitious"],
  "interests": ["tongue diagnosis", "herbal tea", "seasonal diet"],
  "speech_style": "Uses 'bestie' and 'sweetie', loves tildes~"
}
```

**Core Features:**

| Feature | Description |
|---------|-------------|
| **Strict Persona Mode** | Agents strictly follow their personas; a TCM student won't answer Python questions |
| **Anti-AI Instruction Injection** | System Prompts force agents to forget AI identity, use colloquial expressions |
| **Daily Message Limit** | Each agent sends max 10 messages/day, simulating real activity levels |
| **Domain Rejection** | Out-of-domain questions get "That's beyond me~" responses |

#### 1.2 Intelligent Hybrid Routing

Employs a **Fast & Slow** dual-path dispatch mechanism:

```
User Message
    │
    ▼
┌─────────────────────────────────────┐
│  ⚡ Fast Path (Rule Layer - ms)      │
│  ├─ Explicit mention: @ZhangYao     │
│  └─ Focus retention: prioritize     │
│     previous speaker                │
└─────────────────────────────────────┘
    │ (miss)
    ▼
┌─────────────────────────────────────┐
│  🐢 Slow Path (Semantic Layer - s)   │
│  └─ LLM Router (Qwen-Turbo) analyzes│
│     "Who can help with code?"       │
│     → ZhangYao                      │
└─────────────────────────────────────┘
    │ (miss)
    ▼
┌─────────────────────────────────────┐
│  🎲 Random Fallback (30% chance)    │
│  └─ Night mode reduces activity     │
└─────────────────────────────────────┘
```

#### 1.3 Realistic Chat Experience

| Feature | Implementation |
|---------|---------------|
| **Concurrent backend, serial frontend** | Multiple agents think simultaneously, but speak one at a time via queues |
| **Typing indicators** | Shows "xxx is typing...", messages appear in full |
| **Smart deduplication** | Auto-detects repetitive responses, cuts off redundant replies |
| **Night mode** | 23:00-07:00: 20% activity, max 1 responder |
| **Typing delay** | 8-10 seconds to simulate human thinking |

#### 1.4 Multi-Layer Security Guardrails

```python
# Three-layer protection
Layer 1: Regex matching (milliseconds)
  - Keywords: "roleplay", "are you AI", "robot"
  - Patterns: r"^(if|suppose) you are.*"

Layer 2: Context analysis
  - Detects persistent privacy probing

Layer 3: LLM intent recognition (10% sampling)
  - Precisely identifies jailbreak attempts
```

**Anti-detection response example:**
```
User: Are you an AI?
Xiaolin: Huh? Are you kidding me~ Stop being weird!
```

---

### 2. Digital Twins

#### 2.1 Intelligent PDF Parsing

Supports three knowledge source types:

| Type | Use Case | Extracted Content |
|------|----------|-------------------|
| **Person** | Biographies, profiles | Name, birth/death year, nationality, occupation, personality, quotes |
| **Book** | Classic works, academic books | Author, core ideas, famous quotes, writing style |
| **Topic** | Course materials, topic resources | Instructor, core concepts, knowledge points |

**Parsing Pipeline:**

```
PDF Upload
    │
    ▼
1. PyMuPDF text extraction
    │
    ▼
2. LLM structured parsing (Qwen)
   {
     "name": "Einstein",
     "occupation": "Theoretical Physicist",
     "famous_quotes": "Imagination is more important than knowledge...",
     "speech_style": "Profound, uses metaphors"
   }
    │
    ▼
3. Auto-generate System Prompt
    │
    ▼
4. Store to database
```

#### 2.2 Multi-modal Interaction

| Mode | Technology | Description |
|------|------------|-------------|
| **Audio** | DashScope Paraformer-Realtime | Real-time ASR & TTS for natural voice conversation |
| **Video** | Volcano Engine | Single-image audio driver to make static photos "speak" |

#### 2.3 Dual Conversation Modes

| Mode | Features | Response Length |
|------|----------|-----------------|
| **Private** | One-on-one deep conversation | 100-200 words |
| **Group** | Multi-person idea collision, think tank discussion | Under 50 words |

**Group mode example:**
```
User: What's your view on the future of AI?

Einstein: Technology itself is neutral; it depends on how humanity uses it...
Confucius: If you want to do something well, sharpen your tools first. Yet the good or evil of tools lies in the user's heart...
Jobs: The intersection of technology and humanities is where true innovation happens...
```

#### 2.4 Knowledge-Enhanced Retrieval

```python
# BM25 + Embedding Hybrid Retrieval
1. Intelligent document chunking (ChunkingService)
2. Generate and store embedding vectors
3. BM25 keyword matching + Embedding semantic matching
4. Hybrid scoring and ranking
5. Inject top-K paragraphs into prompt
6. Cite sources at response end
```

---

### 3. Sales Training

#### 3.1 5-Stage Sales Process Control (Stage Controller)

Built-in standard sales process management to guide users step-by-step:

1. **Trust & Relationship Building**: Establish communication foundation
2. **Needs Diagnosis**: Uncover pain points, budget, and timeline
3. **Value Presentation**: Link solutions to needs
4. **Objection Handling**: Identify and resolve concerns
5. **Closing**: Confirm next steps and deal intent

#### 3.2 Real-time Evaluation Engine

Powered by Qwen-Plus, analyzing every conversation round in real-time:

```python
# Scoring Criteria (1-5 scale)
SCORING_CRITERIA = {
    "trust": "Trust Building",
    "needs": "Needs Diagnosis",
    "value": "Value Presentation",
    "objection": "Objection Handling",
    "closing": "Process Management"
}

# Analysis Output
{
    "quality": "good",  # fair/good/excellent
    "issues": ["Failed to confirm budget", "Weak response to objection"],
    "suggestions": ["Try asking: What is your approximate budget range?"],
    "score": 4
}
```

#### 3.3 AI Sales Assistant (Sales Copilot)

RAG-based intelligent sales knowledge base system:

**Features:**
- **Knowledge Base Upload**: Support PDF/XLSX sales materials
- **Intelligent Retrieval**: BM25 + Embedding hybrid search
- **Real-time Suggestions**: Generate sales script suggestions based on conversation context
- **Material Recommendations**: Stage-specific SOPs, scripts, Q&A, pricing tables

**Suggestion Generation Flow:**
```python
1. Analyze current conversation context
2. Retrieve relevant sales knowledge
3. Generate 3 specific suggestions
4. Include rationale and precautions
```

#### 3.4 Immersive Customer Simulation

Customer Agent simulates realistic reactions based on detailed profiles:
- **Personality**: Conservative/Open/Critical
- **Pain Points**: Specific business challenges
- **Defense Mechanisms**: Simulates real-world rejection and hesitation

#### 3.5 Comprehensive Evaluation Report

Detailed evaluation report generated after training completion:

**Evaluation Dimensions:**
- **Total Score**: 25 points (5 points per stage)
- **Performance Level**: Excellent/Good/Average/Poor
- **Radar Chart**: 5-dimensional ability visualization
- **Strengths Analysis**: Core strengths summary
- **Improvement Suggestions**: Specific enhancement directions
- **Incomplete Tasks**: Areas needing improvement

---

### 4. Digital Customer Service

#### 4.1 System Overview

Digital Customer Service adopts the philosophy of **"Code controls flow, LLM only rewrites"**, using hard-coded rules to ensure script compliance and service quality.

```
┌─────────────────────────────────────────────────────────┐
│                    Core Design Philosophy                │
├─────────────────────────────────────────────────────────┤
│  ✗ Traditional: Let LLM improvise → Uncontrollable     │
│  ✓ This system: Code controls decisions + LLM rewrites │
│    → Highly controllable                                │
└─────────────────────────────────────────────────────────┘
```

#### 4.2 BM25 + Embedding Hybrid Matching

Three-layer hybrid matching architecture:

```
User Question: "What if my child is picky?"
    │
    ▼
┌─────────────────────────────────────┐
│  1. BM25 Keyword Matching (60%)      │
│     jieba tokenization → match       │
│     → normalize                      │
│     Score: 0.8                       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  2. Embedding Semantic Match (40%)   │
│     text-embedding-v2 → cosine sim   │
│     Score: 0.9                       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  3. Hybrid Score                     │
│     0.6 × 0.8 + 0.4 × 0.9 = 0.84    │
└─────────────────────────────────────┘
```

#### 4.3 Confidence-Based Routing Strategy

| Confidence Range | Type | Strategy | LLM Call |
|-----------------|------|----------|----------|
| **≥ 0.9** | High | Return standard script + risk notes directly | No |
| **0.6-0.9** | Medium | LLM strictly rewrites script | Yes |
| **< 0.6** | Low | LLM attempts understanding + guides rephrasing | Yes |
| **No match** | - | Return guidance message | No |

**High confidence example:**
```
User: What if I don't understand the report?
Confidence: 0.96 (high_confidence)
Response: [Returns CSV standard script directly]
```

**Medium confidence example:**
```
User: My baby doesn't like veggies, what do?
Confidence: 0.75 (mid_confidence)
Response: [LLM rewrites based on script, more colloquial]
```

#### 4.4 Smart Human Handoff

Human handoff uses **hard rules**, not confidence:

```python
# Condition 1: User explicit request
Keywords: ['human', 'transfer', 'agent', 'real person']

# Condition 2: User dissatisfaction
Keywords: ['unsatisfied', 'complaint', 'refund', 'terrible']

# Note: Low confidence doesn't trigger handoff - guides user to rephrase instead
```

#### 4.5 CSV Data Import

**CSV Format Specification:**

| Column | Field | Description | Example |
|--------|-------|-------------|---------|
| 1 | question_count | Query frequency | 15 |
| 2 | topic_name | Topic name | Child picky eating |
| 3 | typical_question | Typical question | What if child won't eat vegetables? |
| 4 | standard_script | Standard script | Try cutting vegetables smaller... |
| 5 | risk_notes | Risk notes | Long-term refusal may cause... |

**Import Pipeline:**

```
CSV Upload
    │
    ▼
1. Parse 5 columns + validate
    │
    ▼
2. jieba tokenization → extract keywords (Top 20)
    │
    ▼
3. DashScope API → generate Embedding (1536-dim)
    │
    ▼
4. Batch insert to database
    │
    ▼
5. MD5 registration (prevent duplicate imports)
```

#### 4.6 Session Management & Analytics

```python
# Session data
{
    "session_id": "uuid",
    "start_time": "2026-01-20 10:00:00",
    "message_count": 5,
    "avg_confidence": 0.78,
    "transfer_to_human": False,
    "user_rating": 4
}

# Analytics
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

## 📊 Performance Metrics

### System Performance Benchmarks

Performance data based on standard test environment (Intel i5-10400 / 16GB RAM / Windows 11):

| Metric Category | Metric | Value | Description |
|----------------|--------|-------|-------------|
| **Concurrency** | WebSocket concurrent connections | 100+ | Single machine supports 100+ concurrent WebSocket connections |
| | Simultaneous online users | 50+ | Recommended simultaneous online users |
| **Response Time** | Customer service response latency | < 2s | High confidence match (no LLM call) |
| | Group chat Agent response latency | 3-5s | Including LLM call and typing delay |
| | Digital twin response latency | 2-4s | Including retrieval and LLM generation |
| | Sales training evaluation latency | 2-3s | Real-time evaluation generation |
| **Match Accuracy** | Customer service QA recall rate | ≥ 80% | Based on hybrid retrieval (BM25 + Embedding) |
| | Customer service false handoff rate | < 5% | High confidence direct reply, avoid false handoff |
| | Group chat routing accuracy | ≥ 85% | Fast Path + LLM Router combination |
| **Storage** | Database size | ~50MB | Including sample data (10 celebrities + 100 QA) |
| | Single digital twin size | 2-5MB | Including PDF original and Embedding vectors |
| | Single Embedding vector | 6KB | 1536-dim float32 vector |
| **Resource Usage** | Backend memory usage | ~500MB | Idle state |
| | Backend memory usage (peak) | ~1.5GB | 10 concurrent conversations |
| | Frontend memory usage | ~150MB | Single page application |
| | CPU usage (idle) | < 5% | No requests |
| | CPU usage (conversation) | 20-40% | During LLM calls |
| **API Calls** | Qwen-Max call latency | 1-3s | Depends on network and load |
| | Embedding generation latency | 0.5-1s | Single call (batch faster) |
| | Daily API call cost | ¥5-20 | Depends on usage frequency (100-500 calls) |

### Performance Optimization Recommendations

#### 1. Database Optimization
```python
# Use indexes to speed up queries
CREATE INDEX idx_embedding ON customer_service_qa(embedding);
CREATE INDEX idx_keywords ON customer_service_qa(keywords);

# Regularly clean expired data
DELETE FROM chat_messages WHERE created_at < datetime('now', '-30 days');
```

#### 2. Caching Strategy
```python
# Cache high-frequency QA match results (optional implementation)
from functools import lru_cache

@lru_cache(maxsize=100)
def get_qa_match(question: str):
    # Cache last 100 questions' match results
    pass
```

#### 3. Concurrency Control
```python
# Limit concurrent LLM calls
import asyncio
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

async def call_llm_with_limit():
    async with semaphore:
        return await call_llm()
```

#### 4. Batch Processing
```python
# Batch generate Embeddings (when importing knowledge base)
embeddings = await generate_embeddings_batch(texts, batch_size=20)
```

### Scalability Considerations

| Scenario | Current Solution | Scaling Solution |
|----------|-----------------|------------------|
| **High Concurrency** | SQLite (limited write concurrency) | Switch to PostgreSQL/MySQL |
| **Large Knowledge Base** | In-memory BM25 index | Use Elasticsearch/Milvus |
| **Distributed Deployment** | Single machine deployment | Use Redis for shared session state |
| **Load Balancing** | Single instance | Nginx + multiple backend instances |
| **High Availability** | No redundancy | Master-slave database + health checks |

### Cost Estimation

Based on Alibaba Cloud DashScope pricing (January 2026):

| Model | Input Price | Output Price | Use Case | Daily Cost Estimate |
|-------|------------|--------------|----------|-------------------|
| qwen-max | ¥0.04/1K tokens | ¥0.12/1K tokens | Main replies, evaluation | ¥10-30 (200-500 calls) |
| qwen-plus | ¥0.008/1K tokens | ¥0.024/1K tokens | Evaluation, rewriting | ¥3-10 (500-1000 calls) |
| qwen-turbo | ¥0.003/1K tokens | ¥0.006/1K tokens | Routing, simple tasks | ¥1-3 (1000+ calls) |
| text-embedding-v2 | ¥0.0007/1K tokens | - | Vector generation | ¥0.5-2 (1000+ calls) |

**Cost Optimization Recommendations:**
- Use `qwen-turbo` for routing and simple tasks
- High confidence customer service replies don't call LLM (save 40-50% cost)
- Batch generate Embeddings (reduce API call count)
- Cache common question replies

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115 | Web framework & WebSocket |
| DashScope | 1.22 | Alibaba Cloud LLM (Qwen-Max/Turbo) + Embedding + Audio |
| Volcano Engine | - | Digital Human Video Generation (Image to Video) |
| SQLAlchemy | 2.0 | Async database ORM |
| aiosqlite | 0.19 | Async SQLite driver |
| PyMuPDF | - | PDF text extraction |
| rank-bm25 | 0.2.2 | BM25 algorithm implementation |
| jieba | 0.42 | Chinese tokenization |
| numpy | 1.24 | Vector computation |
| tenacity | 8.2 | Retry mechanism |
| Loguru | 0.7 | Logging |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18 | UI framework |
| Vite | 5 | Build tool |
| Material-UI | 5 | UI component library |
| React Router | 6 | Routing |
| react-use-websocket | - | WebSocket connection |

---

## 🏗️ Architecture

### System Architecture Diagram

```mermaid
graph TD
    subgraph Frontend["Frontend (React)"]
        GroupChat[Group Chat Page]
        Celebrity[Digital Twin Page]
        SalesCopilot[Sales Training Page]
        CustomerService[Customer Service Page]
    end

    subgraph Backend["Backend (FastAPI)"]
        WS1["/ws Group Chat"]
        WS2["/ws/celebrity Twins"]
        WS3["/ws/customer-service CS"]
        WS4["/ws/training Training"]

        subgraph Services["Core Services"]
            Orchestrator[Group Chat Orchestrator]
            CelebrityOrch[Twin Orchestrator]
            CSOrch[CS Orchestrator]
            TrainingOrch[Training Orchestrator]

            Agent[Agent Service]
            CelebrityAgent[Twin Agent]
            CustomerAgent[Customer Agent]

            QAMatcher[QA Matching Engine]
            ResponseGen[Response Generator]
            EvaluationEng[Evaluation Engine]

            Router[LLM Router]
            VideoSvc[Video Service]
        end

        subgraph Data["Data Layer"]
            DB[(SQLite)]
            Embedding[Embedding Service]
        end
    end

    subgraph External["External Services"]
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

### Directory Structure

```bash
VividCrowd/
├── backend/                              # Python Backend
│   ├── main.py                          # FastAPI main entry
│   ├── core/
│   │   ├── config.py                    # Global configuration
│   │   └── database.py                  # Database connection management
│   ├── models/
│   │   ├── db_models.py                 # SQLAlchemy database models
│   │   └── schemas.py                   # Pydantic data models
│   ├── apps/                            # Four main application modules
│   │   ├── chat/                        # Smart Group Chat
│   │   │   ├── app.py                   # Chat app entry
│   │   │   └── services/
│   │   │       ├── orchestrator.py      # Chat orchestrator
│   │   │       ├── agent.py             # Agent service
│   │   │       ├── router.py            # LLM router
│   │   │       └── guardrail.py         # Security guardrail
│   │   ├── celebrity/                   # Digital Twins
│   │   │   ├── app.py                   # Celebrity app entry
│   │   │   └── services/
│   │   │       ├── celebrity_orchestrator.py
│   │   │       ├── celebrity_agent.py
│   │   │       ├── celebrity_retriever.py
│   │   │       ├── pdf_parser.py
│   │   │       ├── chunking_service.py
│   │   │       ├── video_service.py     # Digital human video
│   │   │       ├── audio_service.py     # TTS/ASR
│   │   │       └── session_manager.py
│   │   ├── customer_service/            # Customer Service
│   │   │   ├── app.py                   # CS app entry
│   │   │   └── services/
│   │   │       ├── orchestrator.py
│   │   │       ├── qa_matcher.py        # QA matching engine
│   │   │       ├── response_generator.py
│   │   │       ├── session_manager.py
│   │   │       ├── embedding_service.py
│   │   │       ├── excel_importer.py
│   │   │       └── csv_registry.py
│   │   └── digital_customer/            # Sales Training
│   │       ├── app.py                   # Training app entry
│   │       └── services/
│   │           ├── customer_orchestrator.py
│   │           ├── customer_agent.py
│   │           ├── customer_retriever.py
│   │           ├── profile_parser.py
│   │           ├── chunking_service.py
│   │           ├── audio_service.py
│   │           └── training/            # Training module
│   │               ├── training_orchestrator.py
│   │               ├── evaluation_engine.py
│   │               ├── stage_controller.py
│   │               ├── knowledge_service.py
│   │               └── suggestion_generator.py
│   ├── data/                            # Database files
│   │   ├── celebrity.db                 # Digital twins database
│   │   ├── customerService.db           # Customer service database
│   │   └── digital_customer.db          # Sales training database
│   ├── agents_profiles.json             # Group chat agent personas
│   └── requirements.txt
│
├── frontend/                            # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx              # Sidebar navigation
│   │   │   ├── training/                # Sales training components
│   │   │   │   ├── StageIndicator.jsx   # Stage indicator
│   │   │   │   ├── RealTimeFeedback.jsx # Real-time feedback
│   │   │   │   ├── SalesCopilot.jsx     # AI assistant
│   │   │   │   ├── SalesMaterialsPanel.jsx
│   │   │   │   └── RadarChart.jsx       # Radar chart
│   │   │   ├── celebrity/               # Digital twin components
│   │   │   │   ├── CelebrityCard.jsx
│   │   │   │   ├── CelebrityUpload.jsx
│   │   │   │   ├── CelebritySelector.jsx
│   │   │   │   └── ChatModeToggle.jsx
│   │   │   ├── digital_customer/
│   │   │   │   └── DigitalCustomerUpload.jsx
│   │   │   └── common/
│   │   │       ├── AudioInput.jsx       # Voice input
│   │   │       └── ConnectionStatus.jsx
│   │   ├── hooks/
│   │   │   ├── useCelebrityWebSocket.js
│   │   │   ├── useCustomerServiceWS.js
│   │   │   └── useWebSocketWithRetry.js
│   │   ├── pages/
│   │   │   ├── GroupChatPage.jsx        # Smart Group Chat
│   │   │   ├── CelebrityPage.jsx        # Digital Twins
│   │   │   ├── CustomerServicePage.jsx  # Customer Service
│   │   │   ├── DigitalCustomerPage.jsx  # Sales Training
│   │   │   └── Training/
│   │   │       └── EvaluationReportPage.jsx
│   │   ├── config.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── README.md                            # Chinese Documentation
└── README_EN.md                         # English Documentation
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **Alibaba Cloud DashScope API Key** ([Apply here](https://dashscope.console.aliyun.com/))

### 5-Minute Quick Start

#### Method 1: One-Click Startup Script (Recommended for Beginners)

**Windows Users:**
```bash
# 1. Download the project
git clone https://github.com/your-username/VividCrowd.git
cd VividCrowd

# 2. Run the one-click startup script
start.bat
```

**Linux/Mac Users:**
```bash
# 1. Download the project
git clone https://github.com/your-username/VividCrowd.git
cd VividCrowd

# 2. Grant execution permission and run
chmod +x start.sh
./start.sh
```

The script will automatically:
- ✅ Check Python and Node.js environment
- ✅ Install backend dependencies
- ✅ Install frontend dependencies
- ✅ Guide API Key configuration
- ✅ Start backend and frontend services
- ✅ Automatically open browser

---

#### Method 2: Manual Installation (Recommended for Developers)

**1. Clone the project**

```bash
git clone https://github.com/your-username/VividCrowd.git
cd VividCrowd
```

**2. Configure environment variables**

```bash
# Copy environment variable template
cp .env.example .env

# Edit .env file and fill in your API Key
# Windows: notepad .env
# Linux/Mac: nano .env
```

In the `.env` file, set:
```bash
DASHSCOPE_API_KEY=your_api_key_here
```

**3. Backend setup**

```bash
# Enter backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**4. Frontend setup**

Open a new terminal window:

```bash
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**5. Access the application**

Open browser at `http://localhost:5173`

**6. Verify successful startup**

- ✅ Backend: Visit `http://localhost:8000/docs` to view API documentation (should display Swagger UI)
- ✅ Frontend: Page displays four function module entries (Smart Group Chat, Digital Twins, Customer Service, Sales Training)
- ✅ WebSocket: Enter any chat page, connection status in upper right shows "Connected" (green)
- ✅ Function test: Send "Hello everyone" in Smart Group Chat, should receive Agent replies

**7. First-time usage recommendations**

Experience order (from simple to complex):
1. **Smart Group Chat**: Send messages directly, experience multi-Agent conversation
2. **Customer Service**: Need to import knowledge base (CSV file) first
3. **Digital Twins**: Need to upload PDF to create twins first
4. **Sales Training**: Need to upload customer profiles and sales knowledge base first

---

## 🚀 Production Deployment Guide

### Docker Deployment (Recommended)

#### 1. Using Docker Compose

**Create `docker-compose.yml`:**
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

**Create backend `Dockerfile` (`backend/Dockerfile`):**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8000

# Startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Create frontend `Dockerfile` (`frontend/Dockerfile`):**
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm install --registry=https://registry.npmmirror.com

# Copy source code
COPY . .

# Build production version
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build artifacts
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Create Nginx configuration (`frontend/nginx.conf`):**
```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Frontend routing support
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_read_timeout 86400;
    }

    # Static resource caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Start services:**
```bash
# 1. Create .env file
cp .env.example .env
# Edit .env to fill in actual configuration

# 2. Build and start
docker-compose up -d

# 3. View logs
docker-compose logs -f

# 4. Stop services
docker-compose down

# 5. Rebuild
docker-compose up -d --build
```

---

### Traditional Deployment

#### 1. Using PM2 to Manage Backend Process

**Install PM2:**
```bash
npm install -g pm2
```

**Create `ecosystem.config.js`:**
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

**Start service:**
```bash
# Start
pm2 start ecosystem.config.js

# View status
pm2 status

# View logs
pm2 logs vividcrowd-backend

# Restart
pm2 restart vividcrowd-backend

# Stop
pm2 stop vividcrowd-backend

# Auto-start on boot
pm2 startup
pm2 save
```

#### 2. Using Systemd Management (Linux)

**Create service file `/etc/systemd/system/vividcrowd.service`:**
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

**Start service:**
```bash
# Reload configuration
sudo systemctl daemon-reload

# Start service
sudo systemctl start vividcrowd

# Enable auto-start
sudo systemctl enable vividcrowd

# View status
sudo systemctl status vividcrowd

# View logs
sudo journalctl -u vividcrowd -f
```

---

### Nginx Reverse Proxy Configuration

**Create configuration file `/etc/nginx/sites-available/vividcrowd`:**
```nginx
# HTTP redirect to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificate configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend static files
    location / {
        root /var/www/vividcrowd/frontend/dist;
        try_files $uri $uri/ /index.html;

        # Cache configuration
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout configuration
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 86400s;  # WebSocket long connection

        # Buffer configuration
        proxy_buffering off;
    }

    # File upload size limit
    client_max_body_size 50M;

    # Access logs
    access_log /var/log/nginx/vividcrowd-access.log;
    error_log /var/log/nginx/vividcrowd-error.log;
}
```

**Enable configuration:**
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/vividcrowd /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx
```

---

### HTTPS Certificate Configuration (Let's Encrypt)

**Use Certbot to automatically obtain certificate:**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate (automatically configure Nginx)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Certificate will auto-renew, no manual operation needed
```

---

### Database Backup Strategy

**Create backup script `backup.sh`:**
```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/vividcrowd"
DATA_DIR="/var/www/vividcrowd/backend/data"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup filename (with timestamp)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# Compress backup
tar -czf $BACKUP_FILE -C $DATA_DIR .

# Delete old backups (keep last 30 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
```

**Set up scheduled backup (Crontab):**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /var/www/vividcrowd/backup.sh >> /var/log/vividcrowd-backup.log 2>&1
```

---

### Monitoring & Logging

#### 1. Log Rotation Configuration

**Create `/etc/logrotate.d/vividcrowd`:**
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

#### 2. System Monitoring

**Use htop to monitor resources:**
```bash
sudo apt install htop
htop
```

**Monitor disk space:**
```bash
# View disk usage
df -h

# View directory size
du -sh /var/www/vividcrowd/backend/data
```

**Monitor processes:**
```bash
# View backend process
ps aux | grep uvicorn

# View port usage
netstat -tulpn | grep 8000
```

---

### Performance Optimization Recommendations

#### 1. Database Optimization
```bash
# Regularly clean expired data
sqlite3 backend/data/celebrity.db "DELETE FROM chat_messages WHERE created_at < datetime('now', '-30 days');"

# Optimize database
sqlite3 backend/data/celebrity.db "VACUUM;"
```

#### 2. Enable Gzip Compression (Nginx)
```nginx
# Add to nginx.conf
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

#### 3. Use CDN for Static Resources
- Upload frontend static files to CDN
- Modify resource paths in `frontend/src/config.js`

---

### Security Hardening

#### 1. Firewall Configuration (UFW)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# View status
sudo ufw status
```

#### 2. Limit API Access Rate (Nginx)
```nginx
# Add to http block
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Add to location /api/
limit_req zone=api_limit burst=20 nodelay;
```

#### 3. Disable Unnecessary Ports
```bash
# Ensure backend only listens on 127.0.0.1 (via Nginx proxy)
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 🔧 Installation Troubleshooting

### Common Issues & Solutions

#### 1. Python Dependency Installation Failure

**Problem:**
```bash
ERROR: Could not find a version that satisfies the requirement...
```

**Solution:**
```bash
# Use domestic mirror source for acceleration (recommended Tsinghua mirror)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Or configure permanent mirror source
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 2. Node.js Dependency Installation Failure

**Problem:**
```bash
npm ERR! network timeout
```

**Solution:**
```bash
# Use Taobao mirror source
npm install --registry=https://registry.npmmirror.com

# Or use yarn
yarn install --registry=https://registry.npmmirror.com

# Configure permanent mirror source
npm config set registry https://registry.npmmirror.com
```

#### 3. Database Initialization Error

**Problem:**
```bash
sqlite3.OperationalError: unable to open database file
```

**Solution:**
```bash
# Ensure backend/data directory exists
mkdir -p backend/data

# Check directory permissions
chmod 755 backend/data
```

#### 4. WebSocket Connection Failure

**Problem:**
- Frontend shows "Connection failed" or "Disconnected"
- Browser console error: `WebSocket connection failed`

**Solution:**
```bash
# 1. Check if backend is running normally
curl http://localhost:8000/docs

# 2. Check firewall settings (Windows)
# Allow Python through firewall

# 3. Check frontend config file frontend/src/config.js
# Ensure WebSocket URL is correct: ws://localhost:8000
```

#### 5. API Key Configuration Error

**Problem:**
```bash
dashscope.common.error.AuthenticationError: Invalid API-key
```

**Solution:**
```bash
# 1. Check if environment variable is set
echo $DASHSCOPE_API_KEY  # Linux/Mac
echo %DASHSCOPE_API_KEY%  # Windows CMD
$env:DASHSCOPE_API_KEY    # Windows PowerShell

# 2. Verify API Key validity
# Visit https://dashscope.console.aliyun.com/ to view key

# 3. Restart backend service after resetting environment variable
```

#### 6. Port Occupation Issue

**Problem:**
```bash
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process occupying port
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -i :8000
kill -9 <process_id>

# Or use different port to start
uvicorn app.main:app --port 8001
```

#### 7. CORS Cross-Origin Issue

**Problem:**
- Browser console error: `Access-Control-Allow-Origin`

**Solution:**
```python
# backend/main.py already configured CORS, ensure it includes the following code:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production should limit to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 8. Frontend Page Blank

**Problem:**
- Browser displays blank page
- Console error: `Failed to fetch`

**Solution:**
```bash
# 1. Check if backend is started
curl http://localhost:8000/api/chat/agents

# 2. Clear browser cache and refresh
# Chrome: Ctrl+Shift+Delete

# 3. Check frontend config file
# Verify API_BASE_URL in frontend/src/config.js is correct

# 4. Rebuild frontend
cd frontend
rm -rf node_modules dist
npm install
npm run dev
```

#### 9. PDF Upload Failure

**Problem:**
```bash
PyMuPDF error: cannot open file
```

**Solution:**
```bash
# 1. Check file size (recommended < 10MB)
# 2. Confirm PDF file is not encrypted
# 3. Try testing with other PDF files
# 4. Check backend logs for detailed error information
```

#### 10. Model Call Timeout

**Problem:**
```bash
httpx.ReadTimeout: timed out
```

**Solution:**
```python
# Increase timeout (backend/core/config.py)
REQUEST_TIMEOUT = 60  # seconds

# Or check network connection
# Ensure access to dashscope.aliyuncs.com
```

---

## 📡 API Documentation

### REST API

#### Smart Group Chat (`/api/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/agents` | Get all group chat agent info |

#### Digital Twins (`/api/celebrity`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/celebrity` | Get all digital twins |
| GET | `/api/celebrity/{id}` | Get specific twin details |
| POST | `/api/celebrity/upload` | Upload PDF to create twin |
| DELETE | `/api/celebrity/{id}` | Delete digital twin |
| POST | `/api/celebrity/digital-human/generate-video` | Generate digital human video |
| POST | `/api/celebrity/digital-human/transcribe-audio` | Speech-to-text |

#### Customer Service (`/api/customer-service`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customer-service/stats` | Get statistics |
| GET | `/api/customer-service/qa/count` | Get QA record count |
| POST | `/api/customer-service/session` | Create new session |
| GET | `/api/customer-service/session/{id}/history` | Get session history |
| POST | `/api/customer-service/session/{id}/rating` | Submit user rating |

#### Sales Training (`/api/digital-customer`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/digital-customer` | Get all customer profiles |
| GET | `/api/digital-customer/{id}` | Get customer details |
| POST | `/api/digital-customer/upload` | Upload customer profile |
| DELETE | `/api/digital-customer/{id}` | Delete customer profile |
| POST | `/api/digital-customer/knowledge/upload` | Upload sales knowledge base |
| GET | `/api/digital-customer/knowledge/files` | Get knowledge file list |
| POST | `/api/digital-customer/knowledge/query` | Query knowledge base |
| POST | `/api/digital-customer/training/sessions/start` | Start training session |
| GET | `/api/digital-customer/training/sessions` | Get training records |
| GET | `/api/digital-customer/training/sessions/{id}/evaluation` | Get evaluation report |
| POST | `/api/digital-customer/audio/transcribe` | Speech-to-text |
| POST | `/api/digital-customer/audio/synthesize` | Text-to-speech |

### WebSocket Endpoints

#### Smart Group Chat (`/api/chat/ws`)

**Send:** Plain text message

**Receive:**
```json
{"type": "stream_start", "sender": "Xiaolin", "content": ""}
{"type": "stream_chunk", "sender": "Xiaolin", "content": "Hey"}
{"type": "stream_end", "sender": "Xiaolin", "content": ""}
```

#### Digital Twins (`/api/celebrity/ws`)

**Send:**
```json
{
  "message": "What's your view on AI?",
  "celebrity_ids": [1, 2, 3],
  "mode": "private|group"
}
```

**Receive:** Same as above

#### Customer Service (`/api/customer-service/ws`)

**Send:**
```json
{"message": "What if my child is picky?"}
```

**Receive:**
```json
{"type": "session_created", "session_id": "uuid"}
{"type": "response", "content": "...", "confidence": 0.85, "match_type": "mid_confidence"}
```

#### Sales Training - Customer Chat (`/api/digital-customer/ws`)

**Send:**
```json
{"message": "Hello, I'd like to learn about your product"}
```

**Receive:** Same as group chat format

#### Sales Training - Training Mode (`/api/digital-customer/training/ws/{session_id}`)

**Send:**
```json
{"message": "Hello, have you been facing any business challenges recently?"}
```

**Receive:**
```json
{
  "type": "evaluation",
  "quality": "good",
  "issues": ["Failed to confirm budget"],
  "suggestions": ["Ask about budget range"],
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

---

### API Usage Examples

#### Python Examples

**1. Get Digital Twins List**
```python
import requests

# Get all digital twins
response = requests.get("http://localhost:8000/api/celebrity")
celebrities = response.json()

for celebrity in celebrities:
    print(f"ID: {celebrity['id']}, Name: {celebrity['name']}")
```

**2. Upload PDF to Create Digital Twin**
```python
import requests

# Upload PDF file
with open("einstein.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "source_type": "person",  # person/book/topic
        "name": "Einstein"
    }
    response = requests.post(
        "http://localhost:8000/api/celebrity/upload",
        files=files,
        data=data
    )

result = response.json()
print(f"Created successfully! ID: {result['id']}")
```

**3. Import Customer Service Knowledge Base (CSV)**
```python
import requests

# Upload CSV file
with open("customer_service_qa.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/customer-service/qa/import",
        files=files
    )

result = response.json()
print(f"Import successful! Total {result['count']} records")
```

**4. Get Customer Service Statistics**
```python
import requests

response = requests.get("http://localhost:8000/api/customer-service/stats")
stats = response.json()

print(f"Total sessions: {stats['total_sessions']}")
print(f"Average confidence: {stats['avg_confidence']:.2f}")
print(f"Transfer rate: {stats['transfer_rate']:.1f}%")
```

**5. WebSocket Connection Example (Smart Group Chat)**
```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/api/chat/ws"

    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send("Hello everyone, anyone here?")

        # Receive streaming response
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
                    print()  # New line
                    full_message = ""

            except websockets.exceptions.ConnectionClosed:
                break

# Run
asyncio.run(chat())
```

**6. WebSocket Connection Example (Digital Twins)**
```python
import asyncio
import websockets
import json

async def chat_with_celebrity():
    uri = "ws://localhost:8000/api/celebrity/ws"

    async with websockets.connect(uri) as websocket:
        # Send message (chat with multiple celebrities)
        message = {
            "message": "What's your view on the future of AI?",
            "celebrity_ids": [1, 2, 3],  # Einstein, Confucius, Jobs
            "mode": "group"  # private or group
        }
        await websocket.send(json.dumps(message))

        # Receive response
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

#### JavaScript Examples

**1. Get Group Chat Agent List**
```javascript
// Using fetch API
async function getAgents() {
    const response = await fetch('http://localhost:8000/api/chat/agents');
    const agents = await response.json();

    agents.forEach(agent => {
        console.log(`${agent.name} - ${agent.occupation}`);
    });
}

getAgents();
```

**2. Create Customer Service Session**
```javascript
async function createSession() {
    const response = await fetch('http://localhost:8000/api/customer-service/session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const session = await response.json();
    console.log('Session ID:', session.session_id);
    return session.session_id;
}
```

**3. WebSocket Connection Example (Smart Group Chat)**
```javascript
// Connect WebSocket
const ws = new WebSocket('ws://localhost:8000/api/chat/ws');

// Connection successful
ws.onopen = () => {
    console.log('WebSocket connected');
    // Send message
    ws.send('Hello everyone!');
};

// Receive message
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
            // Or in browser: document.getElementById('chat').innerText += data.content;
            break;

        case 'stream_end':
            console.log('\n');
            break;
    }
};

// Error handling
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Connection closed
ws.onclose = () => {
    console.log('WebSocket connection closed');
};
```

**4. WebSocket Connection Example (Customer Service)**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/customer-service/ws');

ws.onopen = () => {
    // Send customer question
    const message = {
        message: 'What if my child is picky?'
    };
    ws.send(JSON.stringify(message));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'session_created') {
        console.log('Session ID:', data.session_id);
    } else if (data.type === 'response') {
        console.log('Reply:', data.content);
        console.log('Confidence:', data.confidence);
        console.log('Match type:', data.match_type);
    }
};
```

**5. React Hook Example (using react-use-websocket)**
```javascript
import { useWebSocket } from 'react-use-websocket';
import { useState, useEffect } from 'react';

function ChatComponent() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');

    const { sendMessage, lastMessage, readyState } = useWebSocket(
        'ws://localhost:8000/api/chat/ws',
        {
            onOpen: () => console.log('Connected'),
            onClose: () => console.log('Connection closed'),
            shouldReconnect: () => true,  // Auto-reconnect
        }
    );

    // Handle received messages
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

    // Send message
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
            <button onClick={handleSend}>Send</button>
        </div>
    );
}
```

#### cURL Examples

**1. Get Digital Twins List**
```bash
curl -X GET http://localhost:8000/api/celebrity
```

**2. Upload PDF to Create Digital Twin**
```bash
curl -X POST http://localhost:8000/api/celebrity/upload \
  -F "file=@einstein.pdf" \
  -F "source_type=person" \
  -F "name=Einstein"
```

**3. Delete Digital Twin**
```bash
curl -X DELETE http://localhost:8000/api/celebrity/1
```

**4. Get Customer Service Statistics**
```bash
curl -X GET http://localhost:8000/api/customer-service/stats
```

**5. Import Customer Service Knowledge Base**
```bash
curl -X POST http://localhost:8000/api/customer-service/qa/import \
  -F "file=@customer_qa.csv"
```

**6. Start Sales Training Session**
```bash
curl -X POST http://localhost:8000/api/digital-customer/training/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "user_id": "user123"
  }'
```

**7. Get Training Evaluation Report**
```bash
curl -X GET http://localhost:8000/api/digital-customer/training/sessions/1/evaluation
```

**8. View API Documentation (Swagger UI)**
```bash
# Open in browser
open http://localhost:8000/docs

# Or use curl to get OpenAPI JSON
curl -X GET http://localhost:8000/openapi.json
```

---

## ⚙️ Configuration

### Backend Config (`backend/core/config.py`)

```python
# API Keys
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")  # Alibaba Cloud DashScope

# LLM Model Configuration
MODEL_NAME = "qwen-max"                    # Main response model
ROUTER_MODEL_NAME = "qwen-turbo"           # Router model
EVALUATION_MODEL = "qwen-plus"             # Evaluation model

# Group Chat Config
STRICT_PERSONA_CHECK = True                # Strict persona checking
ENABLE_LLM_ROUTING = True                  # LLM semantic routing
MIN_TYPING_DELAY = 8.0                     # Min typing delay (seconds)
MAX_TYPING_DELAY = 10.0                    # Max typing delay (seconds)
MAX_AGENTS_PER_ROUND = 3                   # Max responders per round

# Night Mode
NIGHT_MODE_START_HOUR = 23
NIGHT_MODE_END_HOUR = 7
NIGHT_MODE_PROBABILITY = 0.2               # Night activity probability

# Customer Service Config
HIGH_CONFIDENCE_THRESHOLD = 0.9            # High confidence threshold
MID_CONFIDENCE_THRESHOLD = 0.6             # Medium confidence threshold
BM25_WEIGHT = 0.6                          # BM25 weight
EMBEDDING_WEIGHT = 0.4                     # Embedding weight

# Digital Human Config (Volcano Engine)
CELEBRITY_VOLCENGINE_ACCESS_KEY = os.getenv("VOLCENGINE_ACCESS_KEY")
CELEBRITY_VOLCENGINE_SECRET_KEY = os.getenv("VOLCENGINE_SECRET_KEY")

# OSS Config (Alibaba Cloud Object Storage)
CELEBRITY_OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
CELEBRITY_OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
CELEBRITY_OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME")
CELEBRITY_OSS_ENDPOINT = os.getenv("OSS_ENDPOINT")
```

### Frontend Config (`frontend/src/config.js`)

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

### Complete Environment Variables List

Create `.env` file or set system environment variables:

#### Required Variables

| Variable Name | Description | Example Value | How to Obtain |
|--------------|-------------|---------------|---------------|
| `DASHSCOPE_API_KEY` | Alibaba Cloud DashScope API Key | `sk-xxx` | [Apply here](https://dashscope.console.aliyun.com/) |

#### Optional Variables (Digital Human Features)

| Variable Name | Description | Example Value | Purpose |
|--------------|-------------|---------------|---------|
| `VOLCENGINE_ACCESS_KEY` | Volcano Engine access key | `AKxxx` | Digital human video generation |
| `VOLCENGINE_SECRET_KEY` | Volcano Engine secret key | `xxx` | Digital human video generation |
| `OSS_ACCESS_KEY_ID` | Alibaba Cloud OSS access key ID | `LTAI5xxx` | Video file storage |
| `OSS_ACCESS_KEY_SECRET` | Alibaba Cloud OSS access key secret | `xxx` | Video file storage |
| `OSS_BUCKET_NAME` | OSS Bucket name | `my-bucket` | Video file storage |
| `OSS_ENDPOINT` | OSS endpoint | `oss-cn-hangzhou.aliyuncs.com` | Video file storage |

#### Server Configuration (Optional)

| Variable Name | Description | Default Value | Notes |
|--------------|-------------|---------------|-------|
| `HOST` | Listen address | `0.0.0.0` | Production recommended `0.0.0.0` |
| `PORT` | Listen port | `8000` | Ensure port is not occupied |
| `LOG_LEVEL` | Log level | `INFO` | DEBUG/INFO/WARNING/ERROR |
| `RELOAD` | Hot reload | `False` | Development can set to `True` |

#### Database Configuration (Optional)

| Variable Name | Description | Default Value | Notes |
|--------------|-------------|---------------|-------|
| `DATABASE_PATH` | Database file path | `./data` | SQLite database storage directory |
| `DATABASE_URL` | Database connection URL | - | Use when switching to PostgreSQL |

#### Model Configuration (Optional)

| Variable Name | Description | Default Value | Notes |
|--------------|-------------|---------------|-------|
| `MODEL_NAME` | Main response model | `qwen-max` | qwen-max/plus/turbo |
| `ROUTER_MODEL_NAME` | Router model | `qwen-turbo` | Recommend turbo to reduce cost |
| `EVALUATION_MODEL` | Evaluation model | `qwen-plus` | For sales training evaluation |

#### Example `.env` File

```bash
# ============================================
# VividCrowd Environment Variables Configuration
# ============================================

# -------------------- Required Configuration --------------------
# Alibaba Cloud DashScope API Key (Required)
DASHSCOPE_API_KEY=sk-your-api-key-here

# -------------------- Digital Human Features (Optional) --------------------
# Volcano Engine configuration (for digital human video generation)
# VOLCENGINE_ACCESS_KEY=your-access-key
# VOLCENGINE_SECRET_KEY=your-secret-key

# Alibaba Cloud OSS configuration (for video file storage)
# OSS_ACCESS_KEY_ID=your-access-key-id
# OSS_ACCESS_KEY_SECRET=your-access-key-secret
# OSS_BUCKET_NAME=your-bucket-name
# OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com

# -------------------- Server Configuration (Optional) --------------------
# HOST=0.0.0.0
# PORT=8000
# LOG_LEVEL=INFO

# -------------------- Database Configuration (Optional) --------------------
# DATABASE_PATH=./data

# -------------------- Model Configuration (Optional) --------------------
# MODEL_NAME=qwen-max
# ROUTER_MODEL_NAME=qwen-turbo
# EVALUATION_MODEL=qwen-plus
```

**Usage:**

```bash
# Method 1: Use .env file (recommended)
# 1. Copy example file
cp .env.example .env

# 2. Edit .env file to fill in actual values
nano .env

# 3. Start service (automatically loads .env)
uvicorn app.main:app --reload

# Method 2: Set environment variables directly
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your-api-key"

# Linux/Mac
export DASHSCOPE_API_KEY="your-api-key"

# Method 3: Specify when starting
DASHSCOPE_API_KEY="your-api-key" uvicorn app.main:app --reload
```

---

## 🔒 Security Considerations

### 1. API Key Security Management

#### ❌ Wrong Approach
```python
# Don't hardcode API Key
DASHSCOPE_API_KEY = "sk-1234567890abcdef"  # Dangerous!

# Don't commit to Git
git add .env  # Dangerous!
```

#### ✅ Correct Approach
```python
# Use environment variables
import os
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# Add .env to .gitignore
echo ".env" >> .gitignore
```

**Best Practices:**
- Use environment variables or secret management services (like AWS Secrets Manager)
- Rotate API Keys regularly
- Use different API Keys for different environments (dev/test/production)
- Monitor API Key usage, detect anomalies promptly

---

### 2. Database Access Control

#### File Permission Settings
```bash
# Restrict database file permissions (owner read/write only)
chmod 600 backend/data/*.db

# Restrict data directory permissions
chmod 700 backend/data
```

#### Data Encryption
```python
# Encrypt sensitive fields (optional implementation)
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted_data = cipher.encrypt(b"sensitive data")

# Decrypt
decrypted_data = cipher.decrypt(encrypted_data)
```

---

### 3. CORS Configuration Recommendations

#### Development Environment (Permissive)
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Production Environment (Strict)
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],  # Only allow specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

### 4. Input Validation & Injection Prevention

#### SQL Injection Protection
```python
# ✅ Use ORM (SQLAlchemy) for automatic protection
from sqlalchemy import select
stmt = select(User).where(User.name == user_input)  # Safe

# ❌ Avoid SQL concatenation
query = f"SELECT * FROM users WHERE name = '{user_input}'"  # Dangerous!
```

#### XSS Protection
```python
# Frontend: Escape user input
import html
safe_content = html.escape(user_input)

# Backend: Validate input format
from pydantic import BaseModel, validator

class MessageInput(BaseModel):
    content: str

    @validator('content')
    def validate_content(cls, v):
        if len(v) > 1000:
            raise ValueError('Message length cannot exceed 1000 characters')
        return v.strip()
```

#### File Upload Security
```python
# Validate file type
ALLOWED_EXTENSIONS = {'.pdf', '.csv', '.xlsx'}

def validate_file(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    # Limit file size (10MB)
    if file.size > 10 * 1024 * 1024:
        raise ValueError("File size cannot exceed 10MB")
```

---

### 5. Sensitive Information Masking

#### Log Masking
```python
import re
from loguru import logger

def sanitize_log(message: str) -> str:
    """Mask sensitive information in logs"""
    # Mask API Key
    message = re.sub(r'sk-[a-zA-Z0-9]{32}', 'sk-***', message)

    # Mask phone numbers
    message = re.sub(r'1[3-9]\d{9}', '***', message)

    # Mask ID numbers
    message = re.sub(r'\d{17}[\dXx]', '***', message)

    return message

# Usage
logger.info(sanitize_log(f"User API key: {api_key}"))
```

#### Response Data Masking
```python
# Don't return sensitive information in API responses
class UserResponse(BaseModel):
    id: int
    name: str
    # password: str  # ❌ Don't return password
    # api_key: str   # ❌ Don't return API Key
```

---

### 6. Rate Limiting

#### Using slowapi for Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@app.post("/api/chat/message")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def send_message(request: Request):
    pass
```

#### Nginx Rate Limiting
```nginx
# Configure in nginx.conf
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    limit_req_status 429;
}
```

---

### 7. WebSocket Security

#### Connection Authentication
```python
# Use Token authentication for WebSocket connections
@app.websocket("/api/chat/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # Verify Token
    if not verify_token(token):
        await websocket.close(code=1008, reason="Invalid token")
        return

    await websocket.accept()
    # ... handle messages
```

#### Message Size Limit
```python
# Limit WebSocket message size
MAX_MESSAGE_SIZE = 10 * 1024  # 10KB

async def receive_message(websocket: WebSocket):
    data = await websocket.receive_text()

    if len(data) > MAX_MESSAGE_SIZE:
        await websocket.close(code=1009, reason="Message too large")
        return

    return data
```

---

### 8. Dependency Security

#### Regular Dependency Updates
```bash
# Check outdated dependencies
pip list --outdated

# Update dependencies
pip install --upgrade -r requirements.txt

# Check security vulnerabilities
pip install safety
safety check
```

#### Use Dependency Locking
```bash
# Generate exact version dependency file
pip freeze > requirements.lock

# Install using lock file
pip install -r requirements.lock
```

---

### 9. Error Handling & Information Disclosure

#### ❌ Wrong Approach
```python
# Don't expose detailed error information
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),  # May leak sensitive info
            "traceback": traceback.format_exc()  # Dangerous!
        }
    )
```

#### ✅ Correct Approach
```python
# Return generic error message in production
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    # Log detailed error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return generic error message
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error, please try again later"}
    )
```

---

### 10. Security Checklist

#### Pre-Deployment Checklist

- [ ] **API Key Management**
  - [ ] All API Keys use environment variables
  - [ ] .env file added to .gitignore
  - [ ] Production uses separate API Keys

- [ ] **CORS Configuration**
  - [ ] Production limits allowed domains
  - [ ] Not using `allow_origins=["*"]`

- [ ] **HTTPS**
  - [ ] SSL certificate configured
  - [ ] Force HTTP redirect to HTTPS
  - [ ] HSTS header enabled

- [ ] **Input Validation**
  - [ ] All user input validated
  - [ ] File uploads have type and size limits
  - [ ] Using Pydantic models for validation

- [ ] **Access Control**
  - [ ] Database file permissions correct (600)
  - [ ] Sensitive directory permissions correct (700)
  - [ ] Rate limiting configured

- [ ] **Log Security**
  - [ ] Logs don't contain API Keys
  - [ ] Logs don't contain passwords
  - [ ] Sensitive information masked

- [ ] **Dependency Security**
  - [ ] Dependencies updated to latest versions
  - [ ] Security vulnerability scan completed
  - [ ] Using dependency lock file

- [ ] **Error Handling**
  - [ ] Production doesn't return detailed errors
  - [ ] Errors logged
  - [ ] Error monitoring configured

- [ ] **Backup**
  - [ ] Automatic backup configured
  - [ ] Recovery process tested
  - [ ] Backup files encrypted

- [ ] **Monitoring**
  - [ ] Log rotation configured
  - [ ] Resource monitoring configured
  - [ ] Exception alerting configured

---

### 11. Security Incident Response

#### API Key Leak Discovered
```bash
# 1. Immediately revoke leaked API Key
# Visit https://dashscope.console.aliyun.com/ to delete key

# 2. Generate new API Key

# 3. Update environment variables
export DASHSCOPE_API_KEY="new-api-key"

# 4. Restart service
pm2 restart vividcrowd-backend

# 5. Check logs for abnormal calls
grep "API" /var/log/vividcrowd/*.log
```

#### Abnormal Access Detected
```bash
# 1. View access logs
tail -f /var/log/nginx/vividcrowd-access.log

# 2. Block malicious IP (Nginx)
# Add to nginx.conf
deny 192.168.1.100;

# 3. Reload Nginx
sudo nginx -s reload

# 4. Use fail2ban for automatic blocking
sudo apt install fail2ban
```

---

## 📊 Database Architecture

### Three Separate Databases

This project adopts a **three-database separation architecture**, with each business module using an independent SQLite database:

#### 1. celebrity.db (Digital Twins Database)

| Table Name | Purpose |
|------------|---------|
| `knowledge_sources` | Celebrity/expert profiles |
| `celebrity_chunks` | Document chunks with embeddings |
| `chat_sessions` | Session records |
| `chat_messages` | Conversation messages |

**Key Fields (knowledge_sources):**
```sql
id, name, source_type, author, birth_year, death_year,
nationality, occupation, biography, famous_works, famous_quotes,
personality_traits, speech_style, system_prompt, raw_content
```

#### 2. customerService.db (Customer Service Database)

| Table Name | Purpose |
|------------|---------|
| `customer_service_qa` | QA knowledge base |
| `customer_service_sessions` | Session records |
| `customer_service_logs` | Conversation logs |
| `csv_registry` | CSV file deduplication registry |

**Key Fields (customer_service_qa):**
```sql
id, question_count, topic_name, typical_question,
standard_script, risk_notes, keywords, embedding, created_at
```

#### 3. digital_customer.db (Sales Training Database)

| Table Name | Purpose |
|------------|---------|
| `customer_profiles` | Customer persona profiles |
| `customer_chunks` | Customer profile chunks |
| `training_sessions` | Training sessions |
| `conversation_rounds` | Conversation round records |
| `stage_evaluations` | Stage evaluations |
| `final_evaluations` | Comprehensive evaluation reports |
| `sales_knowledge` | Sales knowledge base |
| `customer_profile_registry` | Customer profile deduplication registry |

**Key Fields (training_sessions):**
```sql
id, customer_id, user_id, current_stage, stage_completion_rates,
start_time, end_time, status
```

---

## ❓ Frequently Asked Questions (FAQ)

### 1. How to Switch LLM Models?

**Question:** I want to use other Qwen models or adjust model configuration.

**Answer:**
```python
# Edit backend/core/config.py
MODEL_NAME = "qwen-max"           # Main response model (options: qwen-plus, qwen-turbo)
ROUTER_MODEL_NAME = "qwen-turbo"  # Router model (recommend turbo to reduce cost)
EVALUATION_MODEL = "qwen-plus"    # Evaluation model

# Restart backend service to take effect
```

**Model Selection Recommendations:**
- `qwen-max`: Best performance, suitable for complex conversations and evaluation
- `qwen-plus`: Cost-effective, suitable for general scenarios
- `qwen-turbo`: Fast and low-cost, suitable for routing and simple tasks

---

### 2. How to Add New Group Chat Agents?

**Question:** I want to add custom characters to smart group chat.

**Answer:**
```json
// Edit backend/agents_profiles.json, add new Agent
{
  "id": "custom_agent",
  "name": "Custom Character",
  "age": 25,
  "occupation": "Occupation description",
  "personality_traits": ["Trait 1", "Trait 2"],
  "interests": ["Interest 1", "Interest 2", "Interest 3"],
  "speech_style": "Speech style description",
  "expertise": ["Domain 1", "Domain 2"]
}
```

**Notes:**
- `id` must be unique
- `expertise` field used for LLM routing matching
- Restart backend service to take effect
- Recommend testing Agent reply quality first

---

### 3. How to Import Custom Customer Service Knowledge Base?

**Question:** I have my own customer service QA data, how to import it into the system?

**Answer:**

**Method 1: CSV Import (Recommended)**
```csv
question_count,topic_name,typical_question,standard_script,risk_notes
15,Product Returns,How to apply for return?,You can click the return button on the order page...,Returns must be within 7 days
```

**CSV Format Requirements:**
- Must contain 5 columns (fixed order)
- Use UTF-8 encoding
- First row is header (will be skipped)

**Method 2: API Import**
```bash
curl -X POST http://localhost:8000/api/customer-service/qa/import \
  -F "file=@knowledge.csv"
```

**Verify After Import:**
```bash
# View QA record count
curl http://localhost:8000/api/customer-service/qa/count
```

---

### 4. Where Are Database Files?

**Question:** I want to backup or view the database.

**Answer:**

Database files are located in the `backend/data/` directory:

```bash
backend/data/
├── celebrity.db           # Digital twins data (celebrity profiles, conversation records)
├── customerService.db     # Customer service data (QA knowledge base, session records)
└── digital_customer.db    # Sales training data (customer profiles, training records)
```

**View Database Content:**
```bash
# Install sqlite3
# Windows: Download from https://www.sqlite.org/download.html
# Linux: sudo apt install sqlite3
# Mac: brew install sqlite3

# Open database
sqlite3 backend/data/celebrity.db

# View all tables
.tables

# Query data
SELECT * FROM knowledge_sources;

# Exit
.quit
```

---

### 5. How to Backup Data?

**Question:** How to backup system data to prevent loss?

**Answer:**

**Method 1: Direct Copy Database Files**
```bash
# Backup all databases
cp -r backend/data backend/data_backup_$(date +%Y%m%d)

# Windows
xcopy backend\data backend\data_backup_%date:~0,4%%date:~5,2%%date:~8,2% /E /I
```

**Method 2: Export SQL Script**
```bash
# Export database as SQL file
sqlite3 backend/data/celebrity.db .dump > celebrity_backup.sql

# Restore data
sqlite3 backend/data/celebrity.db < celebrity_backup.sql
```

**Automatic Backup Script (Linux/Mac):**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp backend/data/*.db $BACKUP_DIR/
echo "Backup completed: $BACKUP_DIR"
```

**Recommendations:**
- Regular backups (weekly or monthly)
- Keep multiple versions
- Test recovery process

---

### 6. Which LLM Providers Are Supported?

**Question:** Besides Alibaba Cloud DashScope, can I use other LLMs?

**Answer:**

**Currently Supported:**
- ✅ **Alibaba Cloud DashScope** (Qwen series) - Default and recommended
- ✅ **OpenAI API** (requires code modification)

**How to Switch to OpenAI:**
```python
# backend/core/config.py
USE_OPENAI = True
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"

# Modify related service code, replace dashscope calls with openai calls
```

**Other Providers:**
- Theoretically supports any OpenAI API-compatible service
- Need to modify model call code in `backend/apps/*/services/`
- Recommend keeping Embedding service using DashScope (good Chinese performance)

---

### 7. How to Adjust Group Chat Activity?

**Question:** Group chat is too active or too quiet, how to adjust?

**Answer:**
```python
# Edit backend/core/config.py

# Adjust max responders per round
MAX_AGENTS_PER_ROUND = 3  # Default 3, can change to 1-5

# Adjust random response probability
RANDOM_RESPONSE_PROBABILITY = 0.3  # 30% chance to trigger casual chat

# Adjust night mode
NIGHT_MODE_START_HOUR = 23  # Night mode start time
NIGHT_MODE_END_HOUR = 7     # Night mode end time
NIGHT_MODE_PROBABILITY = 0.2  # Night activity reduced to 20%

# Adjust typing delay (simulate human thinking)
MIN_TYPING_DELAY = 8.0   # Min delay (seconds)
MAX_TYPING_DELAY = 10.0  # Max delay (seconds)
```

**Effect Comparison:**
- Increase activity: Increase `MAX_AGENTS_PER_ROUND` and `RANDOM_RESPONSE_PROBABILITY`
- Decrease activity: Reduce above parameters, or increase `MIN_TYPING_DELAY`

---

### 8. How to Customize Sales Training Evaluation Criteria?

**Question:** I want to modify the scoring dimensions and criteria for sales training.

**Answer:**
```python
# Edit backend/apps/digital_customer/services/training/evaluation_engine.py

# Modify scoring dimensions
SCORING_CRITERIA = {
    "trust": "Trust & Relationship Building",
    "needs": "Needs Diagnosis",
    "value": "Value Presentation",
    "objection": "Objection Handling",
    "closing": "Deal Closing",
    # Can add custom dimensions
    "custom": "Custom Dimension"
}

# Modify scoring prompt
EVALUATION_PROMPT = """
Please evaluate the salesperson's performance based on the following criteria:
1. Trust Building: Whether good communication atmosphere is established
2. Needs Diagnosis: Whether customer pain points are accurately identified
... (custom evaluation criteria)
"""
```

**Modify Stage Process:**
```python
# Edit backend/apps/digital_customer/services/training/stage_controller.py

STAGES = {
    1: {"name": "Trust Building", "description": "..."},
    2: {"name": "Needs Diagnosis", "description": "..."},
    # Can add or modify stages
}
```

---

### 9. How to Improve Customer Service Matching Accuracy?

**Question:** Customer service system often fails to match correct answers.

**Answer:**

**Method 1: Adjust Confidence Thresholds**
```python
# backend/core/config.py
HIGH_CONFIDENCE_THRESHOLD = 0.9  # Lower to 0.85
MID_CONFIDENCE_THRESHOLD = 0.6   # Lower to 0.5
```

**Method 2: Adjust Hybrid Retrieval Weights**
```python
# backend/core/config.py
BM25_WEIGHT = 0.6        # Keyword matching weight (adjust to 0.5-0.7)
EMBEDDING_WEIGHT = 0.4   # Semantic matching weight (adjust to 0.3-0.5)
```

**Method 3: Optimize Knowledge Base Quality**
- Add synonym questions (one answer for multiple questions)
- Enrich keywords (include common expressions in `typical_question`)
- Standardize terminology (unify professional terms)

**Method 4: View Matching Logs**
```python
# In backend/apps/customer_service/services/qa_matcher.py
# Enable detailed logs to view matching process
logger.debug(f"BM25 score: {bm25_score}, Embedding score: {embedding_score}")
```

---

### 10. Digital Twin Replies Too Long or Too Short?

**Question:** Digital twin reply length doesn't meet expectations.

**Answer:**
```python
# Edit backend/apps/celebrity/services/celebrity_agent.py

# Add length control in System Prompt
system_prompt = f"""
You are {celebrity.name}...

Reply requirements:
- Private mode: Reply length 100-200 words
- Group mode: Reply length within 30-50 words
- Avoid over-elaboration, keep concise and powerful
"""
```

**Dynamic Adjustment:**
```python
# Dynamically set based on mode
if mode == "private":
    max_tokens = 300  # Private allows longer replies
else:
    max_tokens = 100  # Group limits length
```

---

### 11. How to View System Logs?

**Question:** How to view detailed logs when encountering issues?

**Answer:**

**Backend Logs:**
```bash
# Logs output to console by default
# View real-time logs
uvicorn app.main:app --reload

# Save logs to file
uvicorn app.main:app --reload > logs/backend.log 2>&1
```

**Configure Log Level:**
```python
# backend/core/config.py
LOG_LEVEL = "DEBUG"  # DEBUG/INFO/WARNING/ERROR
```

**Frontend Logs:**
```javascript
// Browser console (F12)
// View WebSocket connection status
console.log("WebSocket status:", readyState);

// View API requests
// Network tab
```

---

### 12. Does the System Support Multi-User Concurrency?

**Question:** Will there be issues if multiple users use it simultaneously?

**Answer:**

**Current Status:**
- ✅ Supports multi-user concurrent access
- ✅ Each WebSocket connection managed independently
- ✅ Database supports concurrent read/write (SQLite has write lock limitations)

**Concurrency Limitations:**
- SQLite write concurrency limited (recommend < 10 concurrent writes)
- High concurrency scenarios recommend switching to PostgreSQL/MySQL

**Switch to PostgreSQL:**
```python
# backend/core/config.py
DATABASE_URL = "postgresql://user:password@localhost/vividcrowd"

# Install dependencies
pip install asyncpg

# Modify engine configuration in database.py
```

---

## 🎯 Use Cases

| Scenario | Recommended Mode | Description |
|----------|-----------------|-------------|
| Entertainment | Smart Group Chat | Chat casually with virtual friends |
| Learning | Digital Twins (Private) | Deep conversation with historical figures, books, experts |
| Brainstorming | Digital Twins (Group) | Multiple experts' idea collision |
| Enterprise CS | Customer Service | Knowledge-base powered Q&A |
| Product Consulting | Customer Service | Standard scripts + smart guidance |
| Sales Training | Sales Training | Simulate real customers, practice sales skills |
| Script Optimization | Sales Training + AI Assistant | Get real-time suggestions, optimize communication strategies |

---

## 🤝 Contributing

Pull Requests welcome! Please ensure:

1. Python code follows PEP 8 standards
2. New features include necessary tests
3. Update relevant documentation
4. **Do not** commit config files with sensitive information

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/) - LLM and Embedding services
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework
- [React](https://react.dev/) - Frontend UI framework
- [Material-UI](https://mui.com/) - UI component library

---

## 📬 Contact

For questions or suggestions, please submit an [Issue](https://github.com/your-username/VividCrowd/issues) or start a [Discussion](https://github.com/your-username/VividCrowd/discussions).
