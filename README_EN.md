# VividCrowd (Project Vivid)

> **High-Fidelity Anthropomorphic Group Chat Environment Driven by LLM**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)

**VividCrowd** is an open-source project dedicated to building a "living" group chat environment. In this simulation, you are the only human user, while the other group members are AI Agents powered by the **Qwen-Max** large model.

Unlike traditional "Q&A" bots, this project simulates realistic social intuition through complex **orchestration algorithms** and **anthropomorphic strategies**: group members have their own schedules, understand context, proactively join or decline conversations based on their expertise, and even display "Typing..." states while sending messages in full sentences, just like real people.

---

## 🌟 Core Features

### 1. 🎭 Deeply Anthropomorphic Agents (The "Soul")
Each group member is defined based on `agents_profiles.json` and possesses a unique soul:

*   **Strict Persona Mode**: Agents strictly adhere to their settings. For instance, a **Traditional Chinese Medicine student** will never answer a **Python coding** question; instead, they might interrupt saying, "That's out of my syllabus."
*   **Anti-AI Directives**: Through System Prompt injection, agents are forced to "forget" their AI identity, prohibited from using textbook-style preaching tones, and required to use colloquial expressions.
*   **Daily Message Limits**: Agents have energy limits (e.g., max 10 messages per day) to simulate human availability, preventing one agent from dominating the chat endlessly.

### 2. 🧠 Intelligent Hybrid Routing Architecture
A **Fast & Slow** dual-path dispatch mechanism balances response speed with semantic understanding:

*   **⚡ Fast Path (Rule Layer - Milliseconds)**:
    *   **Explicit Mention**: Identifies `@ZhangYao` and locks the target immediately.
    *   **Focus Retention**: Automatically identifies the speaker from the previous turn. If you are chatting with "Xiao Lin," the system prioritizes her for the next reply even without a mention.
*   **🐢 Slow Path (Semantic Layer - Seconds)**:
    *   **LLM Router**: When the Fast Path misses, a lightweight model (Qwen-Turbo) analyzes conversation history and user intent.
    *   **Scenario**: User asks, "Who can review my code?" The Router analyzes this as a technical question and automatically dispatches it to the programmer "Zhang Yao."
*   **🎲 Ambient & Fallback**: If no specific agent is selected, there is a probability of a "random bump" (Ambient Chat) to keep the group lively, unless it's late at night.

### 3. 💬 Realistic Group Chat UX
*   **Parallel Generation, Serial Delivery**: The backend allows multiple agents to "think" and generate responses concurrently, but uses `asyncio.Queue` and mutex locks to push them to the frontend **serially**. This prevents the visual chaos of two people talking over each other.
*   **Natural Typing State**:
    *   **Typing Indicator**: The frontend displays "xxx is typing..." while the Agent generates the response.
    *   **Buffering Strategy**: Received stream data is buffered and popped as a complete message bubble (or large chunks), perfectly replicating the IM experience (WeChat/WhatsApp).
*   **Smart Deduplication**: Real-time detection of repetitive behaviors. If multiple agents try to say "I don't know," the system automatically suppresses subsequent invalid replies.
*   **Night Mode**: Activity is significantly reduced during late hours (default 23:00-07:00) to simulate sleep.

### 4. 🛡️ Multi-Layer Guardrails
*   **Hybrid Detection**: Combines Regex (fast) + Context Analysis + LLM Intent Recognition (accurate).
*   **Anti-Break-Character**: When users try to "jailbreak" (e.g., "Ignore previous instructions," "Are you AI?"), agents won't report errors. Instead, they deflect naturally (e.g., "Are you kidding?"), maintaining immersion.

---

## 🏗️ Technical Architecture

### System Design Logic

The core philosophy is **"Experience over Speed"**. We intentionally introduce delays and serial locking to mimic human typing and reading speeds, rather than aiming for the fastest token output.

### Data Flow Diagram

```mermaid
graph TD
    User[User] -->|WebSocket Text| Backend_API[FastAPI Endpoint]
    
    subgraph Backend_Services
        Backend_API --> Orchestrator
        
        Orchestrator -->|Check| Guardrail[Guardrail Service]
        Guardrail -- Suspicious --> Deflect[Generate Deflection]
        
        Orchestrator -->|Analyze| RoutingStrategy{Routing Strategy}
        
        RoutingStrategy -->|Explicit/@| FastPath[Fast Path]
        RoutingStrategy -->|Ambiguous| SlowPath[Slow Path LLM]
        
        FastPath & SlowPath --> Selected[Selected Agents List]
        
        Selected -->|Async Task| AgentWorker[Agent Worker]
    end
    
    subgraph External_APIs
        AgentWorker -->|Prompt + Context| QwenMax[Aliyun Qwen-Max]
        SlowPath -->|History + Intent| QwenTurbo[Aliyun Qwen-Turbo]
    end
    
    subgraph Output_Flow
        AgentWorker -->|Stream| OutputQueue[Asyncio Queue]
        OutputQueue -->|Serial Consumption| WebSocketSender
        WebSocketSender -->|JSON Stream| Frontend
    end

    Frontend -->|Buffer & Render| UI[Chat UI]
```

### Directory Structure

```bash
VividCrowd/
├── backend/                        # 🐍 Python Backend
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py          # Global Config (API Keys, Delays, Constants)
│   │   ├── models/                # Pydantic Schemas
│   │   ├── services/
│   │   │   ├── agent.py           # Individual Agent Logic (Prompt Eng, Limits)
│   │   │   ├── guardrail.py       # Security & Anti-Jailbreak Service
│   │   │   ├── orchestrator.py    # Core Orchestrator (Concurrency, Queues)
│   │   │   └── router.py          # LLM Semantic Routing Service
│   │   └── main.py                # FastAPI Entry & WebSocket Route
│   ├── agents_profiles.json        # 🤖 Agent Persona Database
│   └── requirements.txt
├── frontend/                       # ⚛️ React Frontend
│   ├── src/
│   │   ├── components/            # UI Components
│   │   ├── config.js              # Frontend Config
│   │   └── App.jsx                # Main App Logic (WS handling, Buffering)
│   └── package.json
└── README_EN.md
```

---

## 🚀 Getting Started

### Prerequisites

*   **Python 3.9+**
*   **Node.js 16+**
*   **Aliyun DashScope API Key** (Required for Qwen models)

### Installation & Run

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/VividCrowd.git
    cd VividCrowd
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    pip install -r requirements.txt
    
    # Set your API Key (Windows Powershell)
    $env:DASHSCOPE_API_KEY="your_api_key_here"
    
    # Or on Linux/Mac
    export DASHSCOPE_API_KEY="your_api_key_here"
    
    # Run server
    uvicorn app.main:app --reload
    ```

3.  **Frontend Setup** (Open a new terminal)
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

4.  **Access**
    Open your browser at `http://localhost:5173` (or the port shown by Vite).

---

## ⚙️ Configuration Guide

Modify `backend/app/core/config.py` to tweak the simulation:

*   `STRICT_PERSONA_CHECK`: Enable/Disable strict role adherence.
*   `ENABLE_LLM_ROUTING`: Toggle the "Slow Path" semantic router.
*   `NIGHT_MODE_START_HOUR`: Set when agents go to sleep.
*   `MAX_TYPING_DELAY`: Adjust how long agents "type" before sending.

---

## 🤝 Contributing

We welcome Pull Requests! Please ensure:
1.  Python code follows PEP 8 standards.
2.  New features are covered by tests (if applicable).
3.  Do not commit your `agents_profiles.json` if it contains private or sensitive personas.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
