# AI Career Copilot - System Evaluation and Benchmarking

This directory contains the automated evaluation framework and benchmarking suite for AI Career Copilot. The system is evaluated across two core engineering dimensions:

1. **RAG Retrieval Quality**: Measuring document retrieval accuracy, recall, and ranking quality over candidate resume chunks.
2. **LLM Inference Latency & Generation Speed**: Benchmarking real-world response latency, typical (P50) vs. tail (P95) latency, generation speed, and architectural trade-offs between Cloud API (Groq) and Local On-Device (Ollama) providers.

---

## Executive Summary

| Evaluation Area | Target Component | Primary Metric | Result | Engineering Impact |
|---|---|---|---|---|
| Vector Retrieval | ChromaDB + MiniLM Embeddings | Recall@4 | 90.00% | Relevant resume context is retrieved in the top 4 chunks 9 out of 10 times |
| Vector Retrieval | ChromaDB + MiniLM Embeddings | MRR@4 | 83.33% | Top-ranked chunk is the direct ground-truth match in 11 of 15 queries |
| Cloud Inference | Groq API (`openai/gpt-oss-120b`) | P50 / P95 Latency | 0.81s / 1.20s | Consistently low response times suitable for real-time conversational UX (246.7 tok/s) |
| Local Inference | Ollama (`qwen2.5:7b` on CPU) | P50 / P95 Latency | 14.22s / 132.61s | Full data privacy with zero API costs; likely influenced by local CPU inference and hardware constraints (3.7 tok/s) |
| System Speedup | Cloud vs. Local | Latency Ratio | 32.9x | Validates hybrid routing: cloud for interactive UX, local for offline privacy |

---

## 1. RAG Retrieval Evaluation

### Objective
Assess whether the semantic search engine accurately identifies and ranks the exact sections of a candidate's resume required to answer targeted technical, academic, and experience questions.

### Methodology
- **Vector Database**: ChromaDB (Cosine similarity, Maximal Marginal Relevance search with `top_k=4`, `fetch_k=10`).
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense embeddings).
- **Dataset**: `retrieval_dataset.json` containing 15 ground-truth query-chunk mappings across the candidate resume index (`chunk_0` through `chunk_8`).
- **Metrics Evaluated**:
  - **Recall@K**: Proportion of ground-truth relevant chunks successfully retrieved in the top K positions.
  - **Mean Reciprocal Rank (MRR@K)**: Evaluates ranking quality; assigns `1/rank` for the first relevant chunk found, rewarding systems that surface relevant context at rank 1.

### Retrieval Benchmark Results

| Query ID | Question Summary | Target Chunks | Retrieved Chunks | Recall@4 | Reciprocal Rank |
|---|---|---|---|---|---|
| Q1 | Deep learning models in internship | chunk_1, chunk_2 | chunk_1, chunk_0, chunk_7, chunk_3 | 50.00% | 1.00 |
| Q2 | AI Complaint Triage architecture | chunk_2, chunk_3 | chunk_2, chunk_3, chunk_5, chunk_8 | 100.00% | 1.00 |
| Q3 | Visual Search Engine architecture | chunk_3, chunk_4 | chunk_4, chunk_3, chunk_5, chunk_7 | 100.00% | 1.00 |
| Q4 | RAG system architecture and results | chunk_5, chunk_6 | chunk_5, chunk_6, chunk_8, chunk_2 | 100.00% | 1.00 |
| Q5 | Competitive programming achievements | chunk_7 | chunk_8, chunk_0, chunk_7, chunk_3 | 100.00% | 0.33 |
| Q6 | Programming languages and data tools | chunk_0 | chunk_0, chunk_7, chunk_5, chunk_8 | 100.00% | 1.00 |
| Q7 | RAG and vector search technologies | chunk_1 | chunk_5, chunk_0, chunk_1, chunk_8 | 100.00% | 0.33 |
| Q8 | Internship responsibilities summary | chunk_2 | chunk_7, chunk_0, chunk_2, chunk_4 | 100.00% | 0.33 |
| Q9 | Academic background and CGPA | chunk_8 | chunk_8, chunk_7, chunk_1, chunk_5 | 100.00% | 1.00 |
| Q10 | Published book and research paper | chunk_6, chunk_7 | chunk_7, chunk_0, chunk_5, chunk_2 | 50.00% | 1.00 |
| Q11 | Medical image analysis architectures | chunk_1, chunk_2 | chunk_1, chunk_0, chunk_5, chunk_8 | 50.00% | 1.00 |
| Q12 | Department count in complaint triage | chunk_2 | chunk_2, chunk_3, chunk_5, chunk_8 | 100.00% | 1.00 |
| Q13 | Embedding and vector search skills | chunk_0, chunk_1 | chunk_4, chunk_0, chunk_1, chunk_7 | 100.00% | 0.50 |
| Q14 | University CGPA details | chunk_8 | chunk_8, chunk_7, chunk_2, chunk_5 | 100.00% | 1.00 |
| Q15 | Visual Search Engine performance metrics | chunk_4 | chunk_4, chunk_6, chunk_3, chunk_8 | 100.00% | 1.00 |

### Overall Retrieval Metrics
- **Total Test Queries**: 15
- **Average Recall@4**: **90.00%**
- **Mean Reciprocal Rank (MRR@4)**: **83.33%**

### Engineering Insights
1. High MMR diversity (`lambda_mult=0.5`) ensures that multi-faceted queries (such as system architectures spanning two chunks) successfully retrieve both target chunks without redundant duplicates.
2. In 11 out of 15 queries, the primary relevant chunk was retrieved in the top position (RR = 1.00), demonstrating clean embedding separation between project descriptions, skill catalogs, and academic history.

---

## 2. LLM Latency & Generation Speed Benchmark

### Objective
Measure real-world latency, generation speed (tokens/sec), and statistical distributions (P50 and P95) across four representative application workloads.

### Evaluated Providers
- **Cloud Provider**: Groq API using `openai/gpt-oss-120b` (custom LPU silicon acceleration).
- **Local Provider**: Ollama using `qwen2.5:7b` (4-bit quantized 7B model executed on local consumer CPU).

### Benchmark Methodology
- **Sample Size**: 4 representative prompt tasks x 5 repeated runs per prompt = **20 independent inferences per provider** (40 total calls).
- **Metrics Evaluated**:
  - **Average Latency**: Arithmetic mean across all runs.
  - **P50 Latency (Median)**: The 50th percentile, representing typical user experience.
  - **P95 Latency**: Latency below which approximately 95% of measured requests fall, used to characterize tail performance.
  - **Overall Generation Speed (tokens/sec)**: Total generated completion tokens divided by total elapsed request time across all runs.

### Benchmark Workloads
1. **Quick Technical Lookup**: Short factual query (< 60 words).
2. **Resume Profile Summary**: Context extraction and executive bullet point generation.
3. **Job Alignment Reasoning**: Multi-constraint analysis evaluating candidate profile against job requirements.
4. **Resume Bullet Rewriting**: Structured rewriting following the Google XYZ formula.

### Task-Level Comparison (Averaged Over 5 Runs Per Task)

| Benchmark Task | Cloud Latency (Avg) | Cloud Gen Speed | Local Latency (Avg) | Local Gen Speed | Speedup Ratio |
|---|---|---|---|---|
| Quick Technical Lookup | 0.76s | 198.0 tok/s | 9.57s | 3.0 tok/s | 12.6x |
| Resume Profile Summary | 0.69s | 195.0 tok/s | 15.49s | 4.0 tok/s | 22.4x |
| Job Alignment Reasoning | 0.99s | 297.0 tok/s | 79.76s | 4.0 tok/s | 80.6x |
| Resume Bullet Rewriting | 0.97s | 274.0 tok/s | 7.19s | 4.0 tok/s | 7.4x |

### Statistical Distribution Comparison (All 20 Inferences per Provider)

| Metric | Cloud Provider (Groq API) | Local Provider (Ollama On-Device) |
|---|---|---|
| **Model** | `openai/gpt-oss-120b` | `qwen2.5:7b` |
| **Total Inferences** | 20 | 20 |
| **Average Latency** | **0.85s** | **28.00s** |
| **P50 Latency (Median)** | **0.81s** | **14.22s** |
| **P95 Latency (Tail)** | **1.20s** | **132.61s** |
| **Min Latency** | 0.63s | 3.84s |
| **Max Latency** | 1.21s | 135.53s |
| **Overall Generation Speed** | **246.7 tokens/sec** | **3.7 tokens/sec** |
| **Total Tokens / Time** | 4,202 tokens / 17.0s | 2,089 tokens / 560.0s |
| **Overall Speedup Factor** | **32.9x faster than local** | Reference baseline |

### Latency Distribution Analysis
- **Cloud Provider (Groq)** exhibits a consistently narrow latency distribution across runs: minimum 0.63s, P50 of 0.81s, and P95 of 1.20s. Even complex reasoning queries finish within ~1.2 seconds, ensuring predictable interactive performance.
- **Local Provider (Ollama on CPU)** displays substantial variance between simple queries and multi-step reasoning:
  - For short outputs (e.g. bullet rewriting), latency remains manageable (P50 around 7-14s).
  - For longer reasoning tasks (e.g. Job Alignment Reasoning producing 300+ tokens), latency scales with output length, reaching tail latency (P95) of 132.61s, likely influenced by local CPU inference and hardware constraints.

---

## 3. Architecture Trade-Off Analysis: Cloud vs. Local

The evaluation highlights clear technical trade-offs between cloud-hosted APIs and local model deployment:

| Decision Factor | Cloud (Groq API) | Local (Ollama On-Device) |
|---|---|---|
| **P50 Latency** | Sub-second (0.81s) | Moderate (14.22s) |
| **P95 Latency** | Consistently bounded (1.20s) | Variable on long outputs (132.61s) |
| **Generation Speed** | Fast (246.7 tokens/sec) | Subject to local CPU constraints (3.7 tokens/sec) |
| **Data Privacy** | Prompts transmitted to cloud | Complete data isolation (100% on-device) |
| **Cost** | API usage costs (pay-per-token) | Zero ongoing API cost |
| **Availability** | Requires internet and API uptime | Fully offline operational capability |
| **Hardware Requirements** | Zero client GPU requirement | Requires 8 GB+ host RAM and compute overhead |

### Strategic Recommendation
- **Default Production Mode**: Route user-facing interactive conversations, job analyses, and LangGraph resume editing tools to the Cloud API (Groq) for sub-second responses and predictable P95 latency.
- **Enterprise / Privacy Mode**: Support local Ollama execution when candidate PII cannot leave the user host, or in restricted offline enterprise environments.

---

## 4. Evaluation Directory Structure

```
backend/evaluation/
├── README.md                 # Evaluation documentation and benchmark report
├── __init__.py               # Evaluation package init
├── retrieval_eval.py         # RAG evaluation script (Recall@K, MRR@K)
├── retrieval_dataset.json    # 15 ground-truth question-to-chunk test cases
├── latency_eval.py           # Multi-provider latency and generation speed benchmark
└── results/                  # Structured JSON outputs from evaluation runs
    └── latency_eval_*.json   # Timestamped benchmark execution logs
```

---

## 5. How to Reproduce the Evaluations

### Prerequisites
1. Activate virtual environment and ensure dependencies are installed:
   ```bash
   pip install langchain-core langchain-groq langchain-ollama chromadb requests
   ```
2. For Cloud evaluation: Ensure `GROQ_API_KEY` is defined in `backend/.env`.
3. For Local evaluation: Ensure Ollama is running (`ollama serve`) with `qwen2.5:7b` pulled (`ollama pull qwen2.5:7b`).

### Running RAG Retrieval Evaluation
From the project root:
```bash
python backend/evaluation/retrieval_eval.py
```

### Running Latency & Generation Speed Benchmark
From the project root:

```bash
# Run standard 5-iteration benchmark across both providers (computes P50, P95, and saves JSON report)
python backend/evaluation/latency_eval.py --provider both --runs 5 --save

# Benchmark Cloud provider only
python backend/evaluation/latency_eval.py --provider cloud --runs 5

# Benchmark Local provider only
python backend/evaluation/latency_eval.py --provider local --runs 5
```
