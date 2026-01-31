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

### Installation & Running

**1. Clone the project**

```bash
git clone https://github.com/your-username/VividCrowd.git
cd VividCrowd
```

**2. Backend setup**

```bash
cd backend
pip install -r requirements.txt

# Set API Key
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key_here"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key_here"

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. Frontend setup**

```bash
cd frontend
npm install
npm run dev
```

**4. Access the application**

Open browser at `http://localhost:5173`

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
