# 🚀 Advanced AI Agent System

## **Sistema Completo de Agente IA Enterprise-Ready**

Un sistema de agente de IA robusto y escalable construido con **FastAPI**, **PydanticAI**, **Redis**, **Celery**, y múltiples funcionalidades avanzadas.

---

## 🎯 **Funcionalidades Principales**

### ✅ **Arquitectura Core**
- 🤖 **Agente IA Inteligente** con PydanticAI + OpenAI
- 🔧 **Sistema Multi-Tenant** con configuraciones personalizadas
- 📊 **API RESTful** completa con FastAPI
- 🔄 **Procesamiento Asíncrono** con Celery Workers

### ✅ **Memoria & Persistencia**
- 🧠 **Memoria Conversacional** persistente con Redis
- 💾 **Resúmenes de Sesión** automáticos
- 🔄 **Context Awareness** entre mensajes
- 📝 **Historial de Conversaciones** completo

### ✅ **Observabilidad & Monitoreo**
- 📈 **Langfuse Integration** para trazabilidad completa
- 🔍 **Error Tracking** avanzado con métricas
- 📊 **Performance Monitoring** en tiempo real
- 🚨 **Health Checks** comprensivos

### ✅ **Seguridad & Guardrails**
- 🛡️ **Input Validation** con detección de prompt injection
- 🔒 **PII Detection & Masking** automático
- ⚡ **Rate Limiting** por sesión/usuario
- 🚫 **Output Filtering** para respuestas apropiadas

### ✅ **Herramientas de Negocio**
- 📅 **Scheduling & Calendar** management
- 📧 **Email & Notifications** automáticas
- 🔍 **Document Search** inteligente
- 💳 **Payment Processing** integrado
- 🏢 **Business Hours & Property Info**

### ✅ **Integraciones Avanzadas**
- 🔗 **Webhooks** con retry automático
- 💾 **Caching** inteligente para performance
- 🐳 **Docker & Compose** ready
- 🔄 **Background Tasks** con Celery

---

## 🚀 **Quick Start**

### 1. **Setup Environment**
```bash
# Clone y setup
git clone <repo>
cd agent

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. **Configuración**
```bash
# Copiar variables de entorno
cp .env.example .env

# Editar .env con tus keys
OPENAI_API_KEY=your_openai_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

### 3. **Ejecutar con Docker (Recomendado)**
```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 4. **Ejecutar Local (Desarrollo)**
```bash
# Levantar Redis
docker-compose up redis -d

# Ejecutar API
python -m uvicorn apps.api.main:app --reload --port 8000

# (Opcional) Ejecutar Celery Worker
python -m celery -A workers.celery_worker.app worker --loglevel=info
```

---

## 📚 **API Endpoints**

### **Core Messaging**
- `POST /message` - Procesar mensaje del usuario
- `POST /message/async` - Procesamiento asíncrono con Celery

### **Monitoreo & Salud**
- `GET /health` - Health check básico
- `GET /monitoring/health` - Health check comprehensivo
- `GET /monitoring/errors` - Estadísticas de errores
- `GET /monitoring/performance/{endpoint}` - Métricas de performance

### **Herramientas & Configuración**
- `GET /tools/available` - Lista de herramientas disponibles
- `GET /config/{tenant_id}` - Configuración del tenant
- `GET /metrics/system` - Métricas del sistema

### **Celery & Background Tasks**
- `GET /celery/status` - Estado de workers
- `GET /celery/queue-status` - Estado de colas
- `POST /celery/test` - Probar tarea
- `POST /celery/process-direct` - Ejecutar tarea directamente

### **Webhooks**
- `POST /webhooks/subscribe` - Suscribirse a webhooks
- `GET /webhooks/{tenant_id}` - Ver suscripciones
- `DELETE /webhooks/{tenant_id}/{webhook_id}` - Eliminar webhook
- `POST /webhooks/test` - Probar webhook

---

## 🔧 **Testing**

### **Test API Básico**
```bash
python test_api.py
```

### **Test Funcionalidades Avanzadas**
```bash
# Test completo del sistema
python -c "
import requests

# Test health
response = requests.get('http://localhost:8000/monitoring/health')
print('Health:', response.json()['overall_status'])

# Test herramientas
response = requests.get('http://localhost:8000/tools/available')
print('Tools:', response.json()['total_count'])

# Test mensaje
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

## 🏗️ **Arquitectura**

```
agent/
├── agents_core/              # Core del sistema
│   ├── config/               # Configuraciones
│   ├── orchestrator/         # Agente principal
│   ├── schemas/              # Modelos de datos
│   ├── tools/                # Herramientas del agente
│   ├── memory/               # Gestión de memoria
│   ├── observability/        # Langfuse integration
│   ├── guardrails/           # Validaciones de seguridad
│   ├── middleware/           # Rate limiting & caching
│   ├── monitoring/           # Error tracking
│   └── webhooks/             # Sistema de webhooks
├── apps/api/                 # FastAPI application
├── workers/celery_worker/    # Celery workers
├── infra/                    # Docker & deployment
└── tests/                    # Tests & evaluations
```

---

## 🔧 **Configuración Avanzada**

### **Variables de Entorno**
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Redis
REDIS_URL=redis://localhost:6379/0

# Langfuse (Opcional)
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
# Por defecto: 60 requests/minuto por sesión
# Configurable por endpoint en el código
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

## 📊 **Monitoreo**

### **Métricas Disponibles**
- ✅ Response times por endpoint
- ✅ Error rates y tipos
- ✅ Rate limiting stats
- ✅ Memory usage (conversaciones)
- ✅ Tool usage statistics
- ✅ Webhook delivery stats

### **Health Check**
```bash
curl http://localhost:8000/monitoring/health
```

Respuesta típica:
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

## 🚀 **Producción**

### **Docker Deployment**
```bash
# Build & deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose up --scale worker=3
```

### **Environment Variables**
- Set todas las API keys requeridas
- Configure Redis para persistencia
- Set up Langfuse para observabilidad
- Configure webhooks para integraciones

---

## 🤝 **Contribución**

1. Fork del repositorio
2. Crear feature branch
3. Implementar cambios
4. Añadir tests
5. Actualizar documentación
6. Submit PR

---

## 📄 **Licencia**

MIT License - ver `LICENSE` file para detalles.

---

## 🏆 **Estado del Proyecto**

**🎉 SISTEMA COMPLETO Y PRODUCTION-READY**

- ✅ **Core Functionality**: 100% completado
- ✅ **Security**: Guardrails implementados
- ✅ **Observability**: Langfuse integrado
- ✅ **Performance**: Caching & rate limiting
- ✅ **Scalability**: Celery workers
- ✅ **Monitoring**: Error tracking & health checks
- ✅ **Integration**: Webhooks & APIs
- ✅ **Documentation**: Completa

**Total: 8/8 funcionalidades principales implementadas** 🚀

---

## 🆘 **Soporte**

- 📧 Email: support@ai-agent.com
- 📖 Docs: [Documentation](./docs/)
- 🐛 Issues: [GitHub Issues](./issues)
- 💬 Discord: [Community](./discord)
