# AI Agent Boilerplate

AI Agent boilerplate using FastAPI + PydanticAI + OpenAI + Langfuse + Celery (No Database)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your actual API keys
```

### 3. Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGFUSE_PUBLIC_KEY`: Your Langfuse public key  
- `LANGFUSE_SECRET_KEY`: Your Langfuse secret key

### 4. Start Redis (Required)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7

# Or install Redis locally
```

### 5. Run the Application

```bash
# Development mode
poetry run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Or with Python directly
python -m uvicorn apps.api.main:app --reload
```

## 📁 Project Structure

```
/agents-core/          # Core agent logic
  /config/            # Configuration and settings
  /orchestrator/      # PydanticAI Agent implementation
  /tools/             # Business tools and functions
  /guardrails/        # Input/output validation
  /memory/            # Conversational memory
  /observability/     # Langfuse integration
  /schemas/           # Data models and DTOs
/apps/
  /api/               # FastAPI application
/workers/
  /celery_worker/     # Background task workers
/infra/               # Infrastructure configuration
/tests/               # Tests and evaluations
```

## 🔧 Current Status

✅ Basic project structure created  
✅ Dependencies configured  
✅ Environment template ready  
✅ Configuration module implemented  
✅ FastAPI endpoints working  
✅ Health checks and error handling  
✅ Docker setup completed  
⏳ PydanticAI agent setup (next step)  
⏳ Langfuse integration  
⏳ Example business tools  

## 🚀 Quick Test

```bash
# Start the API
PYTHONPATH=. python -m uvicorn apps.api.main:app --reload

# Test endpoints
python test_api.py
```

## 🐳 Docker Usage

```bash
# Build and run with Docker Compose
cd infra
docker-compose up --build

# API will be available at http://localhost:8000
```

## 📖 Next Steps

1. Set up PydanticAI agent with OpenAI
2. Add example business tools (schedule_visit, etc.)
3. Integrate Langfuse observability
4. Add guardrails and validation
5. Set up Celery workers for background tasks
6. Add conversation memory

## 🤝 Contributing

This is a boilerplate project for AI agents. Feel free to modify and extend as needed for your use case.
