# 🔋 Patent Innovation Predictor

A cutting-edge AI-driven system that intelligently analyzes, explores, and forecasts innovation patterns in **Patents data and predict future innovations in specific technology areas**. This project fuses the power of **LLMs**, **vector databases**, and **multi-agent workflows** to deliver actionable insights for researchers, strategists, and R\&D leaders. Equipped with both CLI and GUI, it supports exploratory search, semantic retrieval, trend forecasting, and more.

---

## 🚀 Key Capabilities

* 🔍 **Keyword, Semantic & Hybrid Patent Search** using OpenSearch
* 🤖 **Multi-Agent Workflow** powered by CrewAI for deep patent analysis
* 🔄 **Iterative Search Refinement** for precision-driven discovery
* 📈 **Trend Forecasting** for identifying emerging innovations and R\&D opportunities
* 🌐 **Interactive Streamlit Dashboard** with real-time inputs and visual feedback
* 🗂 **Structured Logs & Reports** stored in dedicated subdirectories
* 💻 **Dual Interface**: Command Line & GUI for maximum flexibility
* ⚙️ **Extensible Design** for future tech domains beyond batteries

---

## 🧰 Technology Stack

| Component             | Description                                                                         |
| --------------------- | ----------------------------------------------------------------------------------- |
| **Python**            | Core programming language                                                           |
| **Ollama**            | Local LLM runtime for private, fast generation with models like `llama2`, `mistral` |
| **LangChain**         | Manages LLM chains and prompt templates                                             |
| **CrewAI**            | Orchestrates agent roles and task dependencies                                      |
| **OpenSearch**        | Enables vector & keyword-based patent search                                        |
| **Docker**            | Ensures consistent, portable OpenSearch deployment                                  |
| **Streamlit**         | Builds interactive user interfaces                                                  |
| **Logging & Reports** | Records agent interactions and stores analytical output                             |

---

## 📁 Project Structure

```
Patent_Predictor/
├── embeddings/                     # Embedding generation logic
├── opensearch_client/              # OpenSearch client setup
├── outputs/
│   ├── logs/                       # System logs and agent run diagnostics
│   └── patent_analysis/            # Saved analytical reports
├── patent_search_tools.py          # Implements search types
├── patent_crew.py                  # Defines CrewAI agents & task pipelines
├── agentic_rag.py                  # Terminal-based CLI interface
├── app.py                          # Streamlit GUI
├── requirements.txt                # Dependencies
└── README.md                       # This file
```

---

## ⚙️ Setup Instructions

### ✅ Prerequisites

* Python 3.9+
* Docker (to run OpenSearch locally)
* [Ollama](https://ollama.com/) (to run LLMs on your machine)

### 📦 Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/Patent_Predictor.git
cd Patent_Predictor

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🐳 OpenSearch Setup (via Docker)

```bash
docker run -d --name opensearch -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "plugins.security.disabled=true" \
  opensearchproject/opensearch:2.11.0
```

* Access: [http://localhost:9200](http://localhost:9200)

---

## 🧠 Ollama Setup

```bash
# Install Ollama from https://ollama.com

# Start the LLM server
ollama serve

# Pull your preferred model (e.g., llama2)
ollama pull llama2
```

---

## 🧪 Command-Line Interface (CLI)

Launch the agentic CLI workflow:

```bash
python agentic_rag.py
```

### Menu Options:

1. Full trend analysis and forecasting
2. Keyword / Semantic / Hybrid patent search
3. Iterative multi-step exploration
4. View system and LLM status
5. List available Ollama models
6. Exit

---

## 🌐 Streamlit Dashboard

Run the graphical UI:

```bash
streamlit run streamlit_app.py
```

### Features:

* Dropdowns for **search type** and **model selection**
* Query input and **result visualization**
* Real-time model validation and feedback
* Exportable summaries and logs

---

## 👨‍💻 Agentic Workflow (CrewAI)

| Agent Role              | Description                                       |
| ----------------------- | ------------------------------------------------- |
| `Research Director`     | Defines scope, key tech areas, and analysis goals |
| `Patent Retriever`      | Performs hybrid retrieval from OpenSearch         |
| `Patent Analyst`        | Extracts patterns, company strengths, and trends  |
| `Innovation Forecaster` | Projects future breakthroughs and R\&D focus      |

⛓ These agents collaborate sequentially using **CrewAI**, allowing complex, dependent reasoning across the pipeline.

---

## 🔬 Functional Highlights

* ✅ LLM-backed **automated literature mining** across 1000s of patents
* 🔄 Real-time **query optimization** using iterative context-building
* 🧩 Built-in fallback logic to ensure smooth execution even with LLM or OpenSearch issues
* 📂 Export-ready reports for downstream workflows or business use
* 🛡️ Fully **local execution** for secure research environments

---

## 🏆 Why This Project Stands Out

✔ Demonstrates **LLMs beyond chatbots**—real-world research augmentation
✔ Incorporates **RAG, agents, and search** into a unified workflow
✔ Enables analysts to move from search → insight → strategy in one tool
✔ Runs entirely **offline with open-source components**
✔ Excellent base for **enterprise AI adoption** or **IP consulting firms**

---

## 📬 Author & Contact

**Anish Tripathi**
🔹 AI/ML Developer | NLP | Vector Databases | RAG Architectures
🔗 [GitHub](https://github.com/anish3565) | 📧 [tripathianish12@gmail.com](mailto:tripathianish12@gmail.com)

---