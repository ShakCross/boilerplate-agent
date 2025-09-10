# AI Agent Boilerplate — FastAPI + PydanticAI + OpenAI + Langfuse + Celery (No Postgres/pgvector)

This document provides a complete boilerplate for building **ChatGPT-like AI Agents** without an auxiliary Postgres/pgvector brain.  
The stack is simplified for prototyping and pure LLM/chatbot use cases.

- FastAPI + PydanticAI  
- OpenAI (function calling / tools)  
- Observability with Langfuse  
- Queue with Celery (for background tasks)  

It includes architecture, repo structure, schemas, prompts, guardrails, reusable modules, and ready-to-copy snippets.

---

## 1) Architecture (single-turn flow)

- **Gateway** (FastAPI) normalizes input → `MessageDTO`.  
- **Pre-guardrails**: moderation/antispam, nonsense detection, length limits.  
- **Orchestrator** (PydanticAI Agent) with tools:  
  - `schedule_visit` / `create_lead` (business tools examples)  
  - `get_business_hours` (structured FAQ)  
- **Memory**: short summary + last N; tenant config (tone, disclaimers).  
- **LLM** (OpenAI) with function calling invokes tools and produces final answer.  
- **Post-guardrails**: output checks (tone, PII, abstention if low confidence).  
- **Langfuse** traces everything (request → tools → LLM).  
- **Celery**: optional for background ETL or API calls.  

---

## 2) Repository structure (monorepo)

```
/agents-core/
  /config/             # TenantConfig, settings
  /orchestrator/       # PydanticAI Agent(s), instructions, toolsets
  /tools/              # business tools + schemas (pydantic)
  /guardrails/         # input/output filters, nonsense classifier
  /memory/             # conversational summary + store
  /observability/      # langfuse wrappers
  /schemas/            # DTOs FastAPI + I/O tools
/apps/
  /api/                # FastAPI app (routers)
/workers/
  /celery_worker/      # background tasks
/infra/
  docker-compose.yml
/tests/
  evals/               # suites per vertical + fixtures
```

---

## 3) Dependencies (poetry/requirements)

```
fastapi uvicorn pydantic-ai "openai>=1.40" langfuse
python-dotenv pydantic-settings
celery redis  # or rabbitmq
```

---

## 4) Environment variables

```
OPENAI_API_KEY=...
REDIS_URL=redis://redis:6379/0
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LLM_MODEL=gpt-4o-mini
```

---

## 5) Orchestrator (PydanticAI Agent + tools)

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings
from pydantic import BaseModel
from typing import Dict
import os

class Deps(BaseModel):
    tenant: Dict
    session_summary: str = ""
    language: str = "en"

agent = Agent(
    model=os.getenv("LLM_MODEL", "openai:gpt-4o-mini"),
    deps_type=Deps,
    instructions=(
        "You are a multi-domain assistant. "
        "1) Be concise. 2) Use session context. "
        "3) Abstain if lacking data. 4) Respect tenant tone. "
        "5) Reply in user language."
    ),
    model_settings=ModelSettings(temperature=0.2, max_tokens=500),
)
```

---

## 6) Example business tool

```python
from pydantic import BaseModel

class ScheduleVisitIn(BaseModel):
    property_id: str
    datetime_iso: str
    name: str
    phone: str

class ScheduleVisitOut(BaseModel):
    confirmation_id: str
    status: str

@agent.tool
async def schedule_visit(ctx, data: ScheduleVisitIn) -> ScheduleVisitOut:
    # Call CRM/calendar…
    return ScheduleVisitOut(confirmation_id="abc123", status="ok")
```

---

## 7) FastAPI endpoint + Langfuse

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agents_core.orchestrator.agent import agent, Deps
from langfuse import observe

app = FastAPI()

class MessageDTO(BaseModel):
    session_id: str
    tenant_id: str
    text: str
    locale: str = "en"

@app.post("/message")
@observe(name="chat-turn")
async def message(dto: MessageDTO):
    deps = Deps(tenant={}, session_summary="", language=dto.locale)
    result = await agent.run(dto.text, deps=deps)
    return {"reply": result.output_text}
```

---

## 8) Guardrails

- **Input**: moderation (OpenAI), nonsense detection, prompt injection.  
- **Output**: check tone, redact PII, abstain if low confidence.  

---

## 9) Conversational Memory

- Store **short summary** + last N messages (in Redis or in-memory).  
- Hash last answer to avoid repetition.  

---

## 10) Multi-tenant

- `TenantConfig` defines tone, disclaimers, enabled tools.  
- Sessions tied to tenant_id.  

---

## 11) Observability (Langfuse)

- `@observe` spans on endpoints, tools, and agent runs.  
- Capture latency, errors, costs.  

---

## 12) Docker Compose (services)

```yaml
services:
  redis:
    image: redis:7
    ports: ["6379:6379"]
  api:
    build: .
    command: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on: [redis]
    ports: ["8000:8000"]
  worker:
    build: .
    command: celery -A workers.celery_worker.app.celery worker -l INFO
    environment:
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on: [redis]
```

---

## 13) Base prompt (instructions)

```
You are a multi-domain, truthful and concise assistant.
Rules:
1) Do not repeat. Use session context.
2) If user goes off-topic/nonsense, offer 2–3 relevant options or ask for clarification; escalate to human if persists.
3) If you lack certainty, abstain and request missing info. Never invent policies/prices/schedules.
4) Apply tenant tone and policies.
5) Keep answers short; use bullets when appropriate.
```

---

## 14) Example fallback (nonsense)

```
I'm not sure what you mean. Would you like help with:
A) [option 1], B) [option 2], or C) [option 3]?
```

---

## 15) Notes & design choices

- **No Postgres/pgvector**: this agent is LLM-only, similar to ChatGPT.  
- **Faster prototyping**: fewer infra pieces (Redis + Celery only).  
- **Limitations**: no RAG, cannot ground answers in external documents.  
- **Use cases**: customer support bots, structured Q&A, vertical assistants where external KB is not required. 


Herramientas: Disponibles pero no siempre usadas (comportamiento normal de OpenAI)

cada que necesites reiniciar el servidor avisame para hacerlo yo manualmente, actualmente esta corriendo en el port 8000

diferentes idiomas