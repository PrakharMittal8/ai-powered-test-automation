# AI-Powered Test Automation

> Enterprise-grade Selenium automation framework integrated with an AI agent that automatically analyzes test failures, finds root cause, detects patterns, and generates bug reports — using RAG, LangGraph, and MCP.

**Author:** Prakhar Mittal — Senior QA Lead

---

## What is this?

This repository contains two independent projects that work together as one complete system:

| Project | Language | What it does |
|---|---|---|
| `selenium-framework` | Java | Runs automated tests. On failure, automatically sends failure details to the AI agent |
| `ai-failure-analysis-service` | Python | Receives failures, analyzes them using AI, generates reports, shows a live dashboard |

---

## The Big Picture

```
Selenium test fails
        ↓
TestListener.java captures failure details
(test name, exception, stack trace, browser logs, environment)
        ↓
AIAnalysisService.java POSTs to Python FastAPI
        ↓
┌──────────────────────────────────────────────┐
│         AI Failure Analysis Service          │
│                                              │
│  Step 1 — Preprocessing                     │
│  Clean raw text, remove noise                │
│                                              │
│  Step 2 — Embedding (Local MiniLM)           │
│  Convert text to 384-dimension vector        │
│                                              │
│  Step 3 — RAG (FAISS Vector Search)          │
│  Find similar past failures                  │
│  Similarity threshold: 0.75                  │
│                                              │
│  Step 4 — LLM Analysis (Claude)              │
│  Analyze failure + historical context        │
│  Returns: type, root cause, confidence,      │
│  recommended fix, is transient               │
│                                              │
│  Step 5 — LangGraph Agent                   │
│  Node 1: Classify failure type               │
│  Node 2: Check repeat trends                 │
│  Node 3: LLM decides which tools to call     │
│  Node 4: Execute investigation tools         │
│  Node 5: Generate full bug report            │
│  Node 6: Log to dashboard                    │
└──────────────────────────────────────────────┘
        ↓
Live dashboard updated
        ↓
VS Code Copilot can query via MCP
```

---

## Repository Structure

### Project 1 — selenium-framework

```
selenium-framework/
│
├── pom.xml                              ← Maven config and dependencies
├── testng.xml                           ← TestNG suite and listeners registration
│
├── .mvn/wrapper/                        ← Maven wrapper (no Maven install needed)
│
└── src/
    ├── main/java/com/automation/
    │   ├── ai/
    │   │   ├── AIAnalysisService.java   ← POSTs failure to AI agent on test failure
    │   │   └── models/
    │   │       └── FailureContext.java  ← Lombok model for failure payload
    │   ├── api/
    │   │   ├── LoginAPI.java            ← REST Assured login API
    │   │   ├── ProductAPI.java          ← REST Assured product API
    │   │   └── CartAPI.java             ← REST Assured cart API
    │   ├── pages/
    │   │   ├── BasePage.java            ← Reusable Selenium actions
    │   │   ├── LoginPage.java
    │   │   ├── ProductPage.java
    │   │   └── CartPage.java
    │   └── utils/
    │       ├── DriverFactory.java       ← WebDriver init and teardown
    │       ├── ConfigReader.java        ← Loads config by environment
    │       ├── WaitUtils.java           ← Explicit wait helpers
    │       ├── ExtentManager.java       ← Singleton Extent Reports
    │       ├── ScreenshotUtil.java      ← Auto screenshot on failure
    │       ├── BrowserLogUtil.java      ← Browser console log capture
    │       ├── PageSourceUtil.java      ← Page source capture
    │       ├── ExcelUtil.java           ← Apache POI Excel reader
    │       └── ApiUtils.java            ← Shared REST Assured spec
    │
    └── test/
        ├── java/com/automation/
        │   ├── base/
        │   │   ├── BaseTest.java        ← UI test base class
        │   │   └── ApiBase.java         ← API test base class
        │   ├── hooks/
        │   │   └── Hooks.java           ← Cucumber @Before @After (driver lifecycle)
        │   ├── listeners/
        │   │   └── TestListener.java    ← ITestListener — calls AI on onTestFailure()
        │   ├── retry/
        │   │   └── RetryAnalyzer.java   ← Auto retry for flaky tests
        │   ├── stepdefinitions/
        │   │   └── AddToCartSteps.java  ← Cucumber steps
        │   └── tests/
        │       ├── AddToCartTest.java        ← UI E2E test
        │       ├── ApiE2ETest.java           ← Full API E2E test
        │       ├── DataDrivenOrderTest.java  ← Excel data driven test
        │       └── TestRunner.java           ← Cucumber runner
        └── resources/
            ├── config-qa.properties     ← QA environment config
            ├── config-dev.properties    ← Dev environment config
            ├── config-prod.properties   ← Prod environment config
            ├── log4j2.xml               ← Logging config
            ├── features/
            │   └── addToCart.feature   ← BDD feature file
            └── testdata/
                └── LoginTestData.xlsx  ← Excel test data
```

---

### Project 2 — ai-failure-analysis-service

```
ai-failure-analysis-service/
│
├── mcp_server.py                    ← MCP server for VS Code Copilot integration
├── requirements.txt                 ← Python dependencies
├── setup.ps1                        ← PowerShell setup script
├── .env                             ← Config (NOT in repo — create manually)
│
├── embeddingmodel/
│   └── minilm/                      ← MiniLM model (NOT in repo — download manually)
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       ├── vocab.txt
│       ├── modules.json
│       ├── sentence_bert_config.json
│       └── 1_Pooling/config.json
│
├── data/
│   ├── failure_memory.json          ← FAISS persistence (runtime generated)
│   └── dashboard_log.json           ← Dashboard data (runtime generated)
│
├── dashboard/
│   └── index.html                   ← Live dashboard UI
│
└── app/
    ├── main.py                      ← FastAPI entry point
    ├── models/
    │   └── failure_models.py        ← Pydantic request model
    ├── prompts/
    │   ├── analysis_prompt.py       ← Main LLM prompt
    │   └── reanalysis_prompt.py     ← Re-analysis prompt for LOW confidence
    ├── rag/
    │   ├── embedding_service.py     ← Text to vector conversion
    │   ├── preprocessing_service.py ← Text cleaning
    │   ├── vector_store.py          ← FAISS store and search
    │   └── retriever.py             ← RAG orchestration
    ├── routes/
    │   └── analysis_routes.py       ← /analyze endpoint
    ├── services/
    │   ├── openai_service.py        ← LLM calls + agent brain (decide_tools)
    │   ├── report_service.py        ← Bug report generation
    │   └── dashboard_service.py     ← Dashboard read/write
    └── agent/
        ├── __init__.py
        ├── failure_agent.py         ← LangGraph 6-node agent
        └── tools.py                 ← 3 investigation tools
```

---

## Prerequisites

### For Selenium Framework
- Java 17
- Maven 3.8+
- Chrome / Firefox / Edge browser

### For AI Agent
- Python 3.10+
- Access to an OpenAI-compatible LLM endpoint
- MiniLM model (downloaded separately — see Step 5 below)

---

## Complete Setup Guide

### Part 1 — Set up AI Agent first (must be running before Selenium tests)

**Step 1: Clone the repository**
```bash
git clone https://github.com/PrakharMittal8/ai-powered-test-automation.git
cd ai-powered-test-automation/ai-failure-analysis-service
```

**Step 2: Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Step 3: Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Create `.env` file**

Create a file named `.env` in `ai-failure-analysis-service/`:
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=your_llm_gateway_url
CHAT_MODEL=your_model_name
EMBEDDING_MODEL=embeddingmodel/minilm
REPEAT_THRESHOLD=3
```

**Step 5: Download MiniLM embedding model**

The MiniLM model is not committed to GitHub due to its large size.
Download it from Hugging Face:

1. Go to: `https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2`
2. Click **Files and versions** tab
3. Download these files one by one:
   - `config.json`
   - `model.safetensors`
   - `tokenizer.json`
   - `tokenizer_config.json`
   - `vocab.txt`
   - `modules.json`
   - `sentence_bert_config.json`
4. Also open the `1_Pooling/` folder and download `config.json` from inside it

Place all downloaded files in this exact structure:
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

**Step 6: Create data files**
```bash
mkdir data
echo [] > data/failure_memory.json
echo [] > data/dashboard_log.json
```

**Step 7: Start the AI service**
```bash
uvicorn app.main:app --reload
```

Verify it is running:
```
http://localhost:8000/health   → should return {"status": "ok"}
http://localhost:8000/dashboard → live dashboard
```

---

### Part 2 — Set up Selenium Framework

**Step 8: Navigate to selenium-framework**
```bash
cd ../selenium-framework
```

**Step 9: Update application credentials**

Edit all 3 config files:
```
src/test/resources/config-qa.properties
src/test/resources/config-dev.properties
src/test/resources/config-prod.properties
```

```properties
base.url=https://your-application-url.com
username=your_email@example.com
password=your_password
```

Also update `src/test/resources/testdata/LoginTestData.xlsx` with your credentials.

**Step 10: Run the tests**
```bash
# Default (QA environment)
mvn clean test

# Specific environment
mvn clean test -Denv=qa
mvn clean test -Denv=dev
mvn clean test -Denv=prod
```

When a test fails, you will see in the console:
```
================ AI RCA RESPONSE ================
{
  "analysis": {
    "failureType": "ASSERTION_FAILURE",
    "rootCause": "...",
    "confidence": "HIGH",
    ...
  }
}
=================================================
```

**Step 11: View reports**
```
target/ExtentReport.html       ← Rich HTML report
target/cucumber-report.html    ← BDD report
```

**Step 12: View the AI dashboard**
```
http://localhost:8000/dashboard
```

---

### Part 3 — Connect MCP to VS Code Copilot (optional)

**Step 13: Create MCP config**

Create `.vscode/mcp.json` inside `ai-failure-analysis-service/`:
```json
{
  "servers": {
    "ai-failure-analysis": {
      "type": "stdio",
      "command": "C:\\full\\path\\to\\venv\\Scripts\\python.exe",
      "args": ["C:\\full\\path\\to\\ai-failure-analysis-service\\mcp_server.py"]
    }
  }
}
```

Replace with your actual full paths.

**Step 14: Open VS Code Copilot in Agent mode**

- Open VS Code
- Open Copilot Chat (`Ctrl+Shift+P` → `Chat: Open Chat`)
- Switch to **Agent** mode using the dropdown in the chat input

**Step 15: Ask questions in plain English**
```
What are the latest test failures?
Give me a summary of all failures
What failure patterns do you see?
Analyze this failure: loginTest, NoSuchElementException, QA environment
```

Copilot will call your MCP tools, fetch live data from your system, and respond with intelligent analysis.

---

## How AI Integration Works Between the Two Projects

```
testng.xml
  └── registers TestListener as global listener
          ↓
Test fails
          ↓
TestListener.onTestFailure() is called automatically
          ↓
Captures: exception, stack trace, screenshot, browser logs, page source
          ↓
AIAnalysisService.analyzeFailure() is called
          ↓
REST Assured POSTs JSON to http://localhost:8000/analyze
          ↓
AI agent processes, generates report, updates dashboard
          ↓
Response printed in Selenium console output
```

**Important:** AI service must be running at `http://localhost:8000` before starting Selenium tests. If the service is not running, tests still execute normally — the AI call fails gracefully without breaking test execution.

---

## Key Concepts

**RAG (Retrieval Augmented Generation)**
Before analyzing a failure, the system searches for similar past failures using vector similarity. The LLM receives current failure + similar history as context, giving much more accurate root cause analysis than analyzing in isolation.

**LangGraph Agent**
The analysis result passes through a 6-node agent pipeline. At node 3, the LLM reads the failure context and decides which investigation tools to call — not hardcoded rules. Different failures take different investigation paths.

**MCP (Model Context Protocol)**
An open standard by Anthropic. Allows any AI assistant (VS Code Copilot, Claude Desktop) to call your tools directly. You ask questions in plain English — the AI calls your system and explains the results.

---

## Reusing This Framework for Your Project

**Selenium Framework:**
Replace config files, page locators, API endpoints, feature files, and test data.
All core infrastructure works as-is for any web application.

**AI Agent:**
Replace the failure model fields, LLM prompts, and tool logic.
All RAG, agent, dashboard, and MCP infrastructure works as-is for any domain.

---

## License

MIT License — free to use, adapt, and build upon.
