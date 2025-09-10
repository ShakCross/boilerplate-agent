# 🚀 Advanced AI Agent System

## **Complete Enterprise-Ready AI Agent System**

A robust and scalable AI agent system built with **FastAPI**, **PydanticAI**, **Redis**, **Celery**, and multiple advanced features.

---

## 🎯 **Main Features**

### ✅ **Core Architecture**
- 🤖 **Intelligent AI Agent** with PydanticAI + OpenAI
- 🔧 **Multi-Tenant System** with personalized configurations
- 📊 **Complete RESTful API** with FastAPI
- 🔄 **Asynchronous Processing** with Celery Workers

### ✅ **Memory & Persistence**
- 🧠 **Persistent Conversational Memory** with Redis
- 💾 **Automatic Session Summaries**
- 🔄 **Context Awareness** between messages
- 📝 **Complete Conversation History**

### ✅ **Observability & Monitoring**
- 📈 **Langfuse Integration** for complete traceability
- 🔍 **Advanced Error Tracking** with metrics
- 📊 **Real-time Performance Monitoring**
- 🚨 **Comprehensive Health Checks**

### ✅ **Security & Guardrails**
- 🛡️ **Input Validation** with prompt injection detection
- 🔒 **Automatic PII Detection & Masking**
- ⚡ **Rate Limiting** per session/user
- 🚫 **Output Filtering** for appropriate responses

### ✅ **Business Tools**
- 📅 **Scheduling & Calendar** management
- 📧 **Automatic Email & Notifications**
- 🔍 **Intelligent Document Search**
- 💳 **Integrated Payment Processing**
- 🏢 **Business Hours & Property Info**

### ✅ **Advanced Integrations**
- 🔗 **Webhooks** with automatic retry
- 💾 **Intelligent Caching** for performance
- 🐳 **Docker & Compose** ready
- 🔄 **Background Tasks** with Celery

---

## 🚀 **Quick Start**

### 1. **Setup Environment**
```bash
# Clone and setup
git clone <repo>
cd agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configuration**
```bash
# Copy environment variables
cp .env.example .env

# Edit .env with your keys
OPENAI_API_KEY=your_openai_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

### 3. **Run with Docker (Recommended)**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. **Run Locally (Development)**
```bash
# Start Redis
docker-compose up redis -d

# Run API
python -m uvicorn apps.api.main:app --reload --port 8000

# (Optional) Run Celery Worker
python -m celery -A workers.celery_worker.app worker --loglevel=info
```

---

## 📚 **API Endpoints**

### **Core Messaging**
- `POST /message` - Process user message
- `POST /message/async` - Asynchronous processing with Celery

### **Monitoring & Health**
- `GET /health` - Basic health check
- `GET /monitoring/health` - Comprehensive health check
- `GET /monitoring/errors` - Error statistics
- `GET /monitoring/performance/{endpoint}` - Performance metrics

### **Tools & Configuration**
- `GET /tools/available` - List of available tools
- `GET /config/{tenant_id}` - Tenant configuration
- `GET /metrics/system` - System metrics

### **Celery & Background Tasks**
- `GET /celery/status` - Worker status
- `GET /celery/queue-status` - Queue status
- `POST /celery/test` - Test task
- `POST /celery/process-direct` - Execute task directly

### **Webhooks**
- `POST /webhooks/subscribe` - Subscribe to webhooks
- `GET /webhooks/{tenant_id}` - View subscriptions
- `DELETE /webhooks/{tenant_id}/{webhook_id}` - Delete webhook
- `POST /webhooks/test` - Test webhook

---

## 🔧 **Testing**

### **Basic API Test**
```bash
python test_api.py
```

### **Advanced Features Test**
```bash
# Complete system test
python -c "
import requests

# Test health
response = requests.get('http://localhost:8000/monitoring/health')
print('Health:', response.json()['overall_status'])

# Test tools
response = requests.get('http://localhost:8000/tools/available')
print('Tools:', response.json()['total_count'])

# Test message
response = requests.post('http://localhost:8000/message', json={
    'session_id': 'test_001',
    'tenant_id': 'demo',
    'text': 'Schedule a visit for tomorrow at 2 PM',
    'locale': 'en'
})
print('Reply:', response.json()['reply'][:100])
"
```

---

## 🏗️ **Architecture**

```
agent/
├── agents_core/              # System core
│   ├── config/               # Configurations
│   ├── orchestrator/         # Main agent
│   ├── schemas/              # Data models
│   ├── tools/                # Agent tools
│   ├── memory/               # Memory management
│   ├── observability/        # Langfuse integration
│   ├── guardrails/           # Security validations
│   ├── middleware/           # Rate limiting & caching
│   ├── monitoring/           # Error tracking
│   └── webhooks/             # Webhook system
├── apps/api/                 # FastAPI application
├── workers/celery_worker/    # Celery workers
├── infra/                    # Docker & deployment
└── tests/                    # Tests & evaluations
```

---

## 🔧 **Advanced Configuration**

### **Environment Variables**
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Redis
REDIS_URL=redis://localhost:6379/0

# Langfuse (Optional)
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...

# LLM Config
LLM_MODEL=gpt-4o-mini
MAX_TOKENS=500
TEMPERATURE=0.2

# Environment
ENVIRONMENT=local
DEBUG=false

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### **Rate Limiting**
```python
# Default: 60 requests/minute per session
# Configurable per endpoint in code
```

### **Webhooks**
```json
{
  "webhook_id": "my_webhook_001",
  "tenant_id": "my_tenant",
  "url": "https://my-app.com/webhook",
  "events": ["message_processed", "error_occurred"],
  "secret": "webhook_secret_key"
}
```

---

## 📊 **Monitoring**

### **Available Metrics**
- ✅ Response times per endpoint
- ✅ Error rates and types
- ✅ Rate limiting stats
- ✅ Memory usage (conversations)
- ✅ Tool usage statistics
- ✅ Webhook delivery stats

### **Health Check**
```bash
curl http://localhost:8000/monitoring/health
```

Typical response:
```json
{
  "overall_status": "healthy",
  "components": {
    "openai_agent": {"status": "healthy"},
    "redis_memory": {"status": "healthy"},
    "rate_limiter": {"status": "healthy"},
    "error_tracking": {"status": "healthy"}
  }
}
```

---

## 🚀 **Production**

### **Docker Deployment**
```bash
# Build & deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose up --scale worker=3
```

### **Environment Variables**
- Set all required API keys
- Configure Redis for persistence
- Set up Langfuse for observability
- Configure webhooks for integrations

---

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Update documentation
6. Submit PR

---

## 📄 **License**

MIT License - see `LICENSE` file for details.

---

## 🏆 **Project Status**

**🎉 COMPLETE AND PRODUCTION-READY SYSTEM**

- ✅ **Core Functionality**: 100% completed
- ✅ **Security**: Guardrails implemented
- ✅ **Observability**: Langfuse integrated
- ✅ **Performance**: Caching & rate limiting
- ✅ **Scalability**: Celery workers
- ✅ **Monitoring**: Error tracking & health checks
- ✅ **Integration**: Webhooks & APIs
- ✅ **Documentation**: Complete

**Total: 8/8 main features implemented** 🚀

---

## 🆘 **Support**

- 📧 Email: support@ai-agent.com
- 📖 Docs: [Documentation](./docs/)
- 🐛 Issues: [GitHub Issues](./issues)
- 💬 Discord: [Community](./discord)

