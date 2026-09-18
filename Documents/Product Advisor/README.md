# Product Advisor

AI-powered multimodal product recommendation and intelligence platform supporting **Consumer Electronics** and **Electronic Components**.

Designed for local development first with 100% portability to AWS (Aurora, OpenSearch Serverless, S3, ElastiCache, SQS, ECS Fargate) without altering core application logic, agent workflows, or API contracts.

---

## Technology Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+, Pydantic v2, SQLAlchemy (asyncpg)
- **Search**: OpenSearch 2.12 (BM25 keyword + vector search)
- **Database**: PostgreSQL 16 (local) / Amazon Aurora (AWS)
- **Storage**: MinIO (local) / Amazon S3 (AWS)
- **Cache & Queue**: Redis 7 (local) / Amazon ElastiCache & SQS (AWS)
- **LLM Runtime**: Ollama (local) / Containerized LLMs (AWS)
- **Models**:
  - Fast Model: Qwen 2.5 (3B / 4B)
  - Reasoning Model: Qwen 2.5 (7B / 8B)
  - Vision Model: LLaVA 7B / Qwen-VL

---

## Quick Start (Local Environment)

### 1. Prerequisites
- Docker Engine & Docker Compose (or Colima on macOS: `colima start`)
- Python 3.11+
- Node.js 20+

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Start Infrastructure & Application
```bash
# Start all containers via Docker Compose
docker compose up -d

# Or run the automated startup script:
./scripts/start.sh
```

### 4. Verify Infrastructure Health
```bash
python3 scripts/verify_services.py
```

---

## Service Endpoints

| Service | Endpoint | Details |
| :--- | :--- | :--- |
| **Frontend Web App** | [http://localhost:3000](http://localhost:3000) | Next.js Dashboard & Chat UI |
| **FastAPI Backend** | [http://localhost:8000](http://localhost:8000) | REST API & LangGraph Gateway |
| **Interactive Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger OpenAPI UI |
| **Readiness Probe** | [http://localhost:8000/api/v1/ready](http://localhost:8000/api/v1/ready) | Deep service connectivity check |
| **OpenSearch** | [http://localhost:9200](http://localhost:9200) | Cluster health & retrieval index |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | Credentials: `minioadmin` / `minioadmin` |
| **MinIO S3 API** | [http://localhost:9000](http://localhost:9000) | S3-compatible object storage |
| **Ollama Runtime** | [http://localhost:11434](http://localhost:11434) | Model runtime |
| **Redis** | `localhost:6379` | Cache & task queue |
| **PostgreSQL** | `localhost:5432` | Relational source of truth |

---

## Architecture & Phases

See [docs/architecture.md](docs/architecture.md) for full architectural specifications.

- **Phase 1 (Complete)**: Project foundation, Docker Compose, service abstractions, health probes, and verification.
- **Phase 2**: Database models & Alembic migrations.
- **Phase 3**: Storage abstraction.
- **Phase 4**: OpenSearch & hybrid retrieval.
- **Phase 5**: Open-web asynchronous ingestion.
- **Phase 6**: ModelGateway integration (Qwen 4B / 8B).
- **Phases 7-13**: Specialist agents (Query Understanding, Review, Parts/Compatibility, Vision, Ranking, Evidence).
- **Phase 14**: Frontend integration.
- **Phase 15**: Multi-modal evaluation & testing.
- **Phase 16**: AWS cloud adapters.
