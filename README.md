# Product Advisor

**Ask for a product in plain English or Hinglish. Get real, verified recommendations with live buy links — not guesses.**

Product Advisor is an AI shopping assistant. You describe what you want ("gaming laptop under 80k", "mujhe 20 se 30 hazar ke beech phone chahiye", "iPhone 15 Pro"), and it searches its own product catalog first, and if that isn't enough, it goes out and searches Amazon **live** for real, currently-listed products — with real prices, real reviews, and real buy links. It never makes up a price or a product.

---

## Architecture 

<img width="746" height="954" alt="Untitled Diagram drawio" src="https://github.com/user-attachments/assets/6441709b-50ca-49da-b11e-ca69ceb3d13a" />


## What it does

- **Understands natural language and Hinglish** — budgets, brands, specific models, and use cases, without needing a rigid search form.
- **Searches its internal catalog first** (fast) using both keyword and semantic search.
- **Falls back to a live web search** (Amazon, via [Browserbase](https://www.browserbase.com/)) only when the catalog doesn't have enough good matches — so most searches stay fast, and rare/unusual ones still work.
- **Never invents data.** Every price, spec, and review shown is scraped from a real product page at search time. If something can't be verified, it's honestly marked "unknown" instead of guessed.
- **Stays scoped to what you asked for.** Search "Samsung phone" and you get Samsung phones. Search "iPhone 15 Pro" and you get that model — not every other iPhone in the catalog.
- **Shows its work.** Every recommendation comes with evidence (why it was picked), pros/cons from real reviews, and direct buy links to Amazon/Flipkart.
- **Two ways to search**: a structured search page, or a conversational chat interface — both go through the same underlying pipeline.

---

## How it's built

A user's query flows through a chain of specialized steps (agents), each doing one job:

```
Your question
   ↓
Query Understanding   → figures out budget, brand, category, model, language
   ↓
Retrieval              → searches the internal catalog (Postgres + OpenSearch)
   ↓
Not enough good matches? → Browserbase searches the live web for real listings
   ↓
Ranking                → scores and filters candidates against your constraints
   ↓
Evidence & Verification → checks every claim is backed by real data
   ↓
Recommendations        → ranked results with buy links, reviews, and reasoning
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11+, Pydantic v2 |
| Catalog search | OpenSearch (keyword + vector search) |
| Database | PostgreSQL |
| Live web search | Browserbase + Playwright |
| Local AI models | Ollama (Qwen for reasoning, vision model for images) |
| Cache & storage | Redis, MinIO (S3-compatible) |

Runs locally via Docker Compose today; built to port to AWS (Aurora, OpenSearch Serverless, S3, ECS) without changing the application logic.

---

## Running it locally

### 1. Prerequisites
- Docker Engine & Docker Compose (or Colima on macOS: `colima start`)
- Python 3.11+
- Node.js 20+

### 2. Configure environment
```bash
cp .env.example .env
```
Add your `BROWSERBASE_API_KEY` here to enable live web search — without it, the app still works using only the internal catalog.

### 3. Start everything
```bash
docker compose up -d
```

### 4. Check it's healthy
```bash
python3 scripts/verify_services.py
```

### 5. Open it
Frontend: [http://localhost:3000](http://localhost:3000)

---

## Service endpoints

| Service | URL |
|---|---|
| Web app | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/v1/ready |
| OpenSearch | http://localhost:9200 |
| MinIO console | http://localhost:9001 (`minioadmin` / `minioadmin`) |
| Ollama | http://localhost:11434 |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

---

## More details

See [docs/architecture.md](docs/architecture.md) for the full technical architecture.
