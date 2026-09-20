# Product Advisor - Architecture & Technical Design Document

## 1. System Overview

**Product Advisor** is an AI-powered multimodal product recommendation and intelligence platform supporting both **Consumer Electronics** (laptops, smartphones, GPUs, audio) and **Electronic Components** (microcontrollers, MOSFETs, sensors, ICs, passives).

The architecture is built for strict local-to-AWS portability: the same application logic, agent graphs, database schemas, retrieval algorithms, and API contracts run locally via Docker Compose and transition to AWS production infrastructure without code modifications.

---

## 2. Request & Execution Architecture

### 2.1 User Request Flow
```
User
  │
  ▼
Web App (Next.js / TypeScript / Tailwind CSS)
  │
  ▼
FastAPI Gateway (Port 8000, Request ID tracing, CORS, Auth)
  │
  ▼
Supervisor Agent (LangGraph Coordinator)
  │
  ├──► Query Understanding (Qwen 4B: category, budget, constraints, Hinglish/English)
  │
  ├──► Retrieval Agent (OpenSearch: BM25 + Vector k-NN + Metadata Filters)
  │
  ├──► Specialist Agents (Triggered dynamically based on query type):
  │     ├── Review Agent (Qwen 4B/8B: sentiment, recurring flaws, fraud/burst detection)
  │     ├── Parts & Compatibility Agent (Deterministic rules + Qwen 8B for electronics)
  │     └── Vision Agent (Multimodal inspection: ports, layout, condition)
  │
  ├──► Ranking Engine (Deterministic scoring with configurable weights & hard vetoes)
  │
  ├──► Evidence & Verification Critic (Traceability check, constraint & conflict audit)
  │
  ▼
Final Recommendation Response (Structured claims, evidence links, confidence scores)
```

### 2.2 Asynchronous Data Ingestion Pipeline (Independent from Request Flow)
The user request flow **never** synchronously waits for web crawling or scraping.

```
Open Web Sources (Retailers, Component Datasheets, Review Aggregators)
  │
  ▼
Source Discovery & Robots.txt / Rate-Limit Compliance
  │
  ▼
Crawler (SSRF protected, raw content extraction)
  │
  ▼
Object Storage (MinIO locally / Amazon S3 on AWS)
  │
  ▼
Extraction, Cleaning, Normalization, PII Redaction, Deduplication
  │
  ▼
PostgreSQL (Source of truth relational catalog)
  │
  ▼
Embedding Service (nomic-embed-text / modular vectorizer)
  │
  ▼
OpenSearch (Indexed for BM25 and vector k-NN hybrid retrieval)
```

---

## 3. Local / AWS Portability & Service Abstraction Layer

Business logic and agents communicate **only** with abstract interfaces. No AWS SDKs (`boto3`) or local runtime specifics (`ollama`) are imported into agent nodes.

| Service Layer | Abstract Interface | Local Implementation | AWS Implementation (Phase 16) |
| :--- | :--- | :--- | :--- |
| **Relational Database** | `DatabaseService` | PostgreSQL 16 (AsyncPG) | Amazon Aurora PostgreSQL |
| **Search & Retrieval** | `SearchService` | OpenSearch 2.12 | Amazon OpenSearch Serverless |
| **Object Storage** | `StorageService` | MinIO S3 API | Amazon S3 |
| **In-Memory Cache** | `CacheService` | Redis 7 | Amazon ElastiCache Redis |
| **Task Queue** | `QueueService` | Redis List / PubSub Queue | Amazon SQS |
| **Model Runtime** | `ModelGateway` | Ollama (Local models) | Deployed containerized models |
| **Vector Embeddings** | `EmbeddingService` | Local embedding provider | Production vectorizer |

Configuration is switched via `ENVIRONMENT=local` or `ENVIRONMENT=aws`.

---

## 4. LLM & Model Strategy

- **Fast Model (`FAST_MODEL`, e.g., Qwen 2.5 3B/4B)**:
  - Intent extraction, structured entity parsing, Hinglish understanding.
  - Category classification, lightweight review summarization.
- **Reasoning Model (`REASONING_MODEL`, e.g., Qwen 2.5 7B/8B)**:
  - Deep technical comparisons, pinout/voltage electrical compatibility logic.
  - Evidence contradiction synthesis, verification critic.
- **Vision Model (`VISION_MODEL`, e.g., LLaVA 7B / Qwen-VL)**:
  - Inspection of physical ports, connectors, board layouts.
  - Graceful degradation: if unavailable, marks `visual_verification_status = unavailable` while allowing the recommendation to safely proceed.
- **Startup Validation**:
  `ModelGateway.validate_models()` checks installed checkpoints on boot and reports missing models without silent substitution.

---

## 5. Security & Data Integrity

- **External Data Untrusted**: Web content is treated strictly as data payloads and never inserted into system instruction prompts.
- **SSRF Prevention**: Crawlers enforce strict domain allowlists, block internal IP spaces (`127.0.0.1`, `169.254.169.254`, `10.0.0.0/8`, `192.168.0.0/16`).
- **PII Redaction**: Reviews and user inputs pass through sanitizers removing emails, phone numbers, and identifying tokens.
- **Deterministic Ranking**: The LLM does not calculate numerical rankings; ranking is computed mathematically via weighted formulas and verifiable constraints.
