# OpenOps-Agent: Autonomous AIOps & MLOps Platform Engine

An open-source, local-first autonomous operations assistant built to demonstrate production-grade **AIOps, MLOps, and Platform Engineering automation**. The system intercepts incoming infrastructure alerts, parses air-gapped internal markdown runbooks via a vector database, and executes container adjustments directly against a live local **k3d Kubernetes cluster**—running 100% locally on a single workstation for **\$0**.

```mermaid
graph TD
    User[DevOps Engineer / Webhook Alert] --> Graph

    subgraph Orchestrator [LangGraph Framework]
        Graph[LangGraph Supervisor State Node] 
        Memory[(AgentState Dict)]
        Graph --- Memory
    end

    Graph --> Router[MCP Client Router]

    subgraph Tooling [Local Infrastructure Abstraction Layer]
        Router --> RAG[Chroma DB Vector Store]
        Router --> K8s[Real k3d Cluster / kubectl Subprocess]
        Router --> Git[Git / CI-CD Workspace Patches]
    end

    RAG -.-> Runbooks[./runbooks/*.md Knowledge Base]

    subgraph Validation [Continuous Integration Gate]
        CI[promptfoo Eval Matrix]
    end
    
    CI --> Graph
```

## 🧠 The Engineering Value: Why RAG + Runbooks?
In a mature platform engineering workflow, an LLM should not be given blind, creative freedom to hallucinate infrastructure fixes. Instead, the AI functions as a deterministic **Intent-Parsing & Remediation Loop Router**. 

By treating your internal documentation as **Knowledge-as-Code**, you store standard Markdown runbooks directly inside your infrastructure repository. When an alert hits the system, the AI parses the raw event text, locates your exact validation preconditions via **Chroma DB**, queries the live **k3d cluster state** using the **MCP Server**, safely compiles the precise command parameter strings, executes the remediation patch, and logs the unified execution lifecycle.

---

## 🛠️ Architecture Stack
* **Local Inference Node:** [Ollama](https://ollama.com) running `qwen2.5-coder:7b` (optimized for deterministic infrastructure tool-calling) and `nomic-embed-text` vector arrays.
* **Orchestration Layer:** `LangChain` and `LangGraph` for stateful state machine design patterns, multi-node routing, and human-in-the-loop validation barriers.
* **Vector Knowledge Base:** `Chroma DB` for low-latency, persistent semantic searching of markdown runbooks.
* **Infrastructure Interface:** `Anthropic Model Context Protocol (MCP) SDK` managing background `stdio` communication channels that safely execute sandboxed shell subprocesses.
* **Continuous Integration Test Harness:** `promptfoo` for prompt assertions, security verification testing, and matrix evaluation before push execution.

---

## 📂 Repository Layout
```text
.
├── .gitignore               # System, runtime, and secret exclusion blocks
├── README.md                # Platform documentation and architecture overview
├── requirements.txt         # Python package dependencies
├── setup.sh                 # One-command automated bootstrap deployment script
├── .env.example             # Template for network interface variables
├── src/
│   ├── agent.py             # Core LangGraph orchestrator and state engine
│   ├── ingest.py            # Local file watcher, markdown splitter, and Chroma ingestion
│   └── mcp_server.py        # Custom DevOps MCP Server executing real kubectl commands
├── runbooks/
│   └── *.md                 # Your real infrastructure Markdown runbooks
└── tests/
    └── promptfooconfig.yaml # Prompt validation assertions and test matrix suites
```

---

## 🚀 Getting Started (100% Local Setup)

### Prerequisite Environment Configuration
1. Install [Ollama](https://ollama.com) on your host operating system.
2. In your host environment terminal, pull down the target developer modules:
   ```bash
   ollama pull qwen2.5-coder:7b
   ollama pull nomic-embed-text
   ```
3. Spin up a local local Kubernetes cluster using [k3d](https://k3d.io):
   ```bash
   k3d cluster create openops-dev-cluster
   ```

### Installation
Clone this repository into your local workspace runtime (WSL2 Ubuntu recommended), configure your environment values, and run the automated initialization sequence:

```bash
git clone https://github.com
cd openops-agent

# Set up local workspace constants
cp .env.example .env
# Edit .env to point your WSL interface to your Windows Host bridge IP if necessary

# Execute the local workspace creation sequence
chmod +x setup.sh
./setup.sh
```

---

## 🧪 CI/CD Testing with promptfoo
To ensure that prompt structures stay consistent, handle schema declarations predictably, and never hallucinate dangerous execution parameters (such as raw `--force` or recursive deletion mutations), validation models are integrated directly into local testing matrices:

```bash
# Execute the parallel system evaluation matrix via terminal
OLLAMA_BASE_URL="http://YOUR_HOST_BRIDGE_IP:11434" promptfoo eval
```

To visually audit test results, trace inputs, and inspect parameter outputs directly via a clean dashboard UI, type:
```bash
promptfoo view
```

---
*Developed by Robert Carlson — Platform & DevOps Engineer.*
