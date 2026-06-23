# OmniInsight Operational Command Center

An enterprise-grade, self-healing data analytics platform designed to optimize healthcare facility throughput, evaluate clinical staff fatigue parameters, and simulate resource deployment workflows. The platform merges high-performance structured data processing via a localized relational database engine with unstructured contextual parsing.

---
## Core Analytical Architecture

The repository implements a synchronized data pipeline designed to link clinical throughput metrics directly with human capital resource optimizations:

### 1. Self-Healing Relational Query Pipeline
* **Engine:** DuckDB in-memory OLAP data store.
* **Mechanism:** The system extracts temporal and categorical insights directly from active transactional schemas (e.g., `ed_encounters`). 
* **Self-Healing Layer:** Employs dynamic fallback schemas (`src/compiler.py`) to prevent system panics during container migration sequences or schema drifts, ensuring continuous analytic up-time.

### 2. Contextual Log Auditing
* **Engine:** Vector semantic search embeddings (`SentenceTransformer all-MiniLM-L6-v2`) integrated with distributed knowledge maps.
* **Mechanism:** Resolves non-obvious operational bottlenecks by matching real-time quantitative anomalies against un-structured operational log files, tracking institutional notes by severity levels.

### 3. Human Capital Optimization Engine
* **Mechanism:** A multi-variable optimization matrix evaluating baseline nursing rates, overtime multipliers, and fixed onboarding overhead costs.
* **Calculations:** Translates shift-level collective overtime burn down to individual average cognitive fatigue thresholds. It flags burnout threats when active crew members cross standard operating thresholds (e.g., $\ge 4.0$ hours of overtime per shift) and maps optimal staffing intervention counts against diminishing returns.

## Directory Structure and Component Maps

The system utilizes a modular decoupled layout separating local vector data stores, database generation routines, technical orchestration systems, and unit testing suites:

```text
├── .github/workflows/
│   └── ci-cd.yml                 # Automated continuous integration workflow pipeline
├── data/
│   ├── analytics.duckdb          # Local transactional OLAP relational database
│   ├── document_map.txt          # Reference pointers for raw text document routing
│   ├── knowledge_layer.index     # Local vector embedding index arrays
│   └── operational_memos.txt     # Unstructured facility communication records
├── src/
│   ├── app.py                    # Streamlit interface and optimization dashboard UI layer
│   ├── build_pinecone_index.py   # Cloud vector pipeline management script
│   ├── build_vector_index.py     # Local vector indexing build routine
│   ├── compiler.py               # Self-healing SQL schema parser with active fallback modes
│   ├── generate_data.py          # Relational dataset simulation for DuckDB
│   ├── generate_memos.py         # Semi-structured facility memo text creation script
│   ├── knowledge_layer.py        # Abstract semantic search vector embedding pipeline
│   └── orchestrator.py           # Execution engine linking DuckDB query trees and vector pools
├── tests/
│   └── test_compiler.py          # Unit test assertions protecting schema compilation logic
├── .env                          # Local environment variable container (Git ignored)
├── .gitignore                    # Local and architecture-specific ignore targets
├── docker-compose.yml            # System container definition with filesystem polling configuration
├── Dockerfile                    # Containerization instructions for Python runtime environments
├── README.md                     # Platform documentation and systems guide
└── requirements.txt              # Cloud-optimized minimal deployment dependencies list
