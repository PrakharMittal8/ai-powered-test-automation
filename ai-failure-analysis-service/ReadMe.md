# AI Failure Analysis Service

> Python-based AI agent that automatically analyzes Selenium test failures. Uses RAG (Retrieval Augmented Generation), LangGraph agent, and MCP protocol to find root cause, detect patterns, generate bug reports, and expose results to AI assistants — all without any manual effort.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| FastAPI | REST API server |
| FAISS | Vector similarity search |
| sentence-transformers (MiniLM) | Local offline text embedding model |
| LangGraph | AI agent pipeline |
| LangChain Core | Agent state management |
| Claude / OpenAI compatible LLM | Failure analysis and agent decisions |
| httpx | Async HTTP client |
| Pydantic | Request validation |
| MCP | AI client protocol (VS Code Copilot, Claude Desktop) |

---

## Folder Structure

```
ai-failure-analysis-service/
│
├── mcp_server.py                    ← MCP server — exposes tools to VS Code Copilot
├── requirements.txt                 ← All Python dependencies
├── setup.ps1                        ← PowerShell setup script
├── .env                             ← Environment variables (NOT committed — create manually)
│
├── embeddingmodel/
│   └── minilm/                      ← MiniLM model files (NOT committed — download manually)
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       ├── vocab.txt
│       ├── modules.json
│       ├── sentence_bert_config.json
│       └── 1_Pooling/
│           └── config.json
│
├── data/
│   ├── failure_memory.json          ← FAISS vector store persistence (runtime generated)
│   └── dashboard_log.json           ← Dashboard entries (runtime generated)
│
├── dashboard/
│   └── index.html                   ← Live HTML dashboard (auto-refreshes every 30s)
│
└── app/
    │
    ├── main.py                      ← FastAPI app entry, registers routes, serves dashboard
    │
    ├── models/
    │   └── failure_models.py        ← Pydantic model for incoming failure JSON
    │
    ├── prompts/
    │   ├── analysis_prompt.py       ← Main LLM prompt with failure details + RAG context
    │   └── reanalysis_prompt.py     ← Sharper prompt for LOW confidence re-analysis
    │
    ├── rag/
    │   ├── embedding_service.py     ← Loads MiniLM, converts text to 384-dim vector
    │   ├── preprocessing_service.py ← Cleans raw text, removes noise and dynamic IDs
    │   ├── vector_store.py          ← FAISS store — save, search, persist vectors
    │   └── retriever.py             ← Connects embedding + vector store, returns similar failures
    │
    ├── routes/
    │   └── analysis_routes.py       ← /analyze endpoint — orchestrates all layers
    │
    ├── services/
    │   ├── openai_service.py        ← LLM calls: analyze_failure() + decide_tools() (agent brain)
    │   ├── report_service.py        ← Generates markdown bug report with agent findings
    │   └── dashboard_service.py     ← Read/write dashboard_log.json, repeat count logic
    │
    └── agent/
        ├── __init__.py
        ├── failure_agent.py         ← LangGraph agent: 6 nodes, graph compile, run_agent()
        └── tools.py                 ← 3 investigation tools the agent can call
```

---

## How It Works — Full Flow

```
Selenium test fails
        ↓
TestListener.java calls AIAnalysisService.java
        ↓
POST /analyze with failure JSON
        ↓
┌─────────────────────────────────────────────┐
│              FastAPI /analyze               │
│                                             │
│  1. PreprocessingService                    │
│     Clean text — remove session IDs,        │
│     timestamps, memory addresses,           │
│     Angular dynamic IDs, noise              │
│                                             │
│  2. EmbeddingService                        │
│     Convert cleaned text to 384-dim         │
│     vector using local MiniLM model         │
│     Normalize for cosine similarity         │
│                                             │
│  3. VectorStore (FAISS)                     │
│     Search for similar past failures        │
│     Threshold: cosine similarity > 0.75     │
│     Match = similar failure found           │
│     No match = new unique failure           │
│                                             │
│  4. Store or Skip                           │
│     New failure → store vector + metadata  │
│     Duplicate → skip storage               │
│                                             │
│  5. LLM Analysis                            │
│     Build prompt with failure details       │
│     + similar past failures (RAG context)   │
│     Call Claude → get structured JSON       │
│                                             │
│  6. LangGraph Agent (6 nodes)               │
│     Node 1: Classify failure type           │
│     Node 2: Count repeat occurrences        │
│     Node 3: LLM decides which tools to call │
│     Node 4: Execute chosen tools            │
│     Node 5: Generate bug report             │
│     Node 6: Log to dashboard                │
└─────────────────────────────────────────────┘
        ↓
Response returned to Selenium framework
        ↓
Dashboard updated at http://localhost:8000/dashboard
```

---

## Agent Tools

The LLM agent reads each failure's context and decides which tools to call.
This is what makes it a true agent — not hardcoded if-else rules.

| Tool | Triggers When | What It Investigates |
|---|---|---|
| `re_analyze` | Confidence is LOW | Re-calls LLM with sharper stack-trace focused prompt. New analysis replaces original. |
| `check_environment_pattern` | Same failure type seen before | Checks if repeated failures are in one environment (config issue) or many (code issue) |
| `check_same_page_failures` | Failure type contains ELEMENT, TIMEOUT, VISIBILITY, LOCATOR, STALE | Finds other tests on the same page that are also failing |

---

## LLM Response Structure

```json
{
  "failureType": "ASSERTION_FAILURE",
  "rootCause": "Product was not added to cart due to race condition",
  "confidence": "HIGH",
  "recommendedFix": [
    "Add explicit wait after add-to-cart click",
    "Verify cart count element before assertion"
  ],
  "frameworkSuggestion": "Add retry mechanism for cart operations",
  "isTransient": false,
  "shouldRetry": false
}
```

---

## MCP Integration

The `mcp_server.py` exposes 3 tools to any MCP-compatible AI client:

| Tool | What It Does |
|---|---|
| `analyze_failure` | Posts failure to `/analyze`, returns full AI analysis |
| `get_dashboard_summary` | Returns failure counts, type breakdown, trend patterns |
| `get_recent_failures` | Returns last N failures with root cause and agent reasoning |

Ask VS Code Copilot (Agent mode):
```
What are the latest test failures?
Give me a summary of all failures today
What patterns do you see in the failures?
```

---

## Prerequisites

- Python 3.10+
- Access to an OpenAI-compatible LLM endpoint
- MiniLM embedding model (downloaded separately — see setup)

---

## Setup and Run

**1. Clone the repository**
```bash
git clone https://github.com/PrakharMittal8/ai-powered-test-automation.git
cd ai-powered-test-automation/ai-failure-analysis-service
```

**2. Create virtual environment**
```bash
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Download MiniLM embedding model**

The MiniLM model is not committed to GitHub due to its size (~90MB).
Download it manually from Hugging Face:

- Go to: `https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2`
- Click **Files and versions**
- Download these files:
  - `config.json`
  - `model.safetensors`
  - `tokenizer.json`
  - `tokenizer_config.json`
  - `vocab.txt`
  - `modules.json`
  - `sentence_bert_config.json`
  - `1_Pooling/config.json`

Place them in this exact folder structure:
```
ai-failure-analysis-service/
└── embeddingmodel/
    └── minilm/
        ├── config.json
        ├── model.safetensors
        ├── tokenizer.json
        ├── tokenizer_config.json
        ├── vocab.txt
        ├── modules.json
        ├── sentence_bert_config.json
        └── 1_Pooling/
            └── config.json
```

**5. Create `.env` file**

Create a file named `.env` at the root of `ai-failure-analysis-service/`:
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=your_llm_gateway_url
CHAT_MODEL=your_model_name
EMBEDDING_MODEL=embeddingmodel/minilm
```

**6. Create data files**

```bash
mkdir data
echo [] > data/failure_memory.json
echo [] > data/dashboard_log.json
```

**7. Start the service**
```bash
uvicorn app.main:app --reload
```

Service runs at: `http://localhost:8000`

**8. View the dashboard**

Open in browser:
```
http://localhost:8000/dashboard
```

**9. Connect MCP to VS Code Copilot (optional)**

Create `.vscode/mcp.json` inside the project:
```json
{
  "servers": {
    "ai-failure-analysis": {
      "type": "stdio",
      "command": "C:\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\ai-failure-analysis-service\\mcp_server.py"]
    }
  }
}
```

Replace paths with your actual paths. Open VS Code Copilot in **Agent mode** and ask questions about your failures.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze` | Accepts failure JSON, runs full analysis + agent |
| GET | `/dashboard` | Serves the live HTML dashboard |
| GET | `/dashboard-data` | Returns all failures as JSON |
| GET | `/health` | Health check |

**Sample Request to `/analyze`:**
```json
{
  "testName": "addProductToCartTest",
  "exceptionMessage": "Expected [true] but found [false]",
  "stackTrace": "java.lang.AssertionError: Expected [true] but found [false]...",
  "screenshotPath": "",
  "pageSourcePath": "",
  "browserLogs": "WARNING: ngx-spinner type missed...",
  "timestamp": "2024-01-15T10:30:00",
  "environment": "QA"
}
```

---

## How to Adapt to Any Domain

This agent can be adapted to any failure analysis use case:

| What to change | Where |
|---|---|
| Failure input fields | `failure_models.py` |
| Analysis prompt | `analysis_prompt.py` |
| Re-analysis prompt | `reanalysis_prompt.py` |
| Investigation tool logic | `tools.py` |
| MCP tool descriptions | `mcp_server.py` |

**What you never need to change:**
`vector_store.py`, `embedding_service.py`, `preprocessing_service.py`, `failure_agent.py` graph structure, `dashboard_service.py` — core RAG and agent infrastructure works for any domain.

---

## Author

**Prakhar Mittal** — Senior QA Lead
