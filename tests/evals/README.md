# 🧪 Tests & Evaluations

Esta carpeta contiene scripts de testing y evaluación para el AI Agent.

## 📁 Archivos Organizados

### 🔬 **Tests Principales**

#### `test_system_complete.py`
**Test completo del sistema** - El test principal que verifica todos los componentes.

```bash
cd tests/evals
python test_system_complete.py
```

**Qué prueba:**
- ✅ Conectividad básica de la API
- ✅ Health check comprehensivo (6/6 componentes)
- ✅ Herramientas disponibles (8 herramientas)
- ✅ Procesamiento de mensajes con IA
- ✅ Monitoreo y observabilidad
- ✅ Sistema Celery y workers

---

### 🐰 **Tests de Celery & Workers**

#### `check_workers.py`
**Verificación de workers optimizados** - Verifica que los workers independientes funcionen.

```bash
cd tests/evals
python check_workers.py
```

**Qué verifica:**
- 🔍 Estado de workers de Celery
- ⚡ Procesamiento asíncrono
- 📊 Estadísticas de tasks

#### `start_optimized_workers.py`
**Optimización avanzada de workers** - Inicia workers con configuración optimizada.

```bash
cd tests/evals
python start_optimized_workers.py
```

**Características:**
- 🚀 8 workers concurrentes
- 🧵 Pool de threads (compatible Windows)
- 📈 Configuración de alto rendimiento

---

### 🔴 **Tests de Redis**

#### `check_redis.py`
**Verificación de Redis** - Muestra el contenido actual de Redis.

```bash
cd tests/evals
python check_redis.py
```

**Qué muestra:**
- 📊 Keys totales en Redis
- 💭 Conversaciones guardadas
- ⚡ Rate limiting activo
- 🔧 Tasks de Celery

#### `redis_celery_demo.py`
**Demo interactivo de Redis y Celery** - Demuestra cómo funcionan Redis y Celery.

```bash
cd tests/evals
python redis_celery_demo.py
```

**Opciones del demo:**
1. Contenido actual de Redis
2. Demo de memoria conversacional
3. Demo de rate limiting
4. Demo de Celery tasks
5. Todo lo anterior

---

### 🎮 **Test Manual Interactivo**

#### `test_manual.py`
**Tester manual interactivo** - Interface para probar manualmente el sistema.

```bash
cd tests/evals
python test_manual.py
```

**Opciones disponibles:**
1. Test de salud del sistema
2. Ver herramientas disponibles
3. Test rápido - Horarios de negocio
4. Test rápido - Programar visita
5. Test rápido - Enviar email
6. **Modo interactivo (chat)**
7. Test personalizado

---

## 🚀 **Guía de Uso Rápido**

### **Test Completo del Sistema:**
```bash
cd tests/evals
python test_system_complete.py
```

### **Verificar Workers Optimizados:**
```bash
cd tests/evals
python check_workers.py
```

### **Chat Interactivo:**
```bash
cd tests/evals
python test_manual.py
# Elige opción 6 para modo chat
```

### **Ver Estado de Redis:**
```bash
cd tests/evals
python check_redis.py
```

---

## 📊 **Resultados Esperados**

### **Sistema Completamente Funcional:**
```
✅ Tests básicos pasados: 6/6
🎉 SISTEMA COMPLETAMENTE FUNCIONAL!

✨ Características habilitadas:
• OpenAI Agent con respuestas inteligentes
• Langfuse para observabilidad completa
• Memoria conversacional con Redis
• Rate limiting y guardrails de seguridad
• Herramientas de negocio avanzadas
• Monitoreo y error tracking
```

### **Workers Optimizados:**
```
=== RESUMEN ===
Workers funcionando: SI
Procesamiento async: SI

EXITO: Sistema optimizado con workers independientes!
```

---

## 🛠️ **Troubleshooting**

### **Si el test falla:**
1. Verificar que la API esté corriendo: `python -m uvicorn apps.api.main:app --reload --port 8000`
2. Verificar que Redis esté corriendo: `docker-compose up redis -d`
3. Verificar workers: `python check_workers.py`

### **Si Redis está vacío:**
- Es normal al inicio, se llenará con el uso
- Ejecutar algunos tests para generar datos

### **Si Celery no funciona:**
- Usar el script optimizado: `python start_optimized_workers.py`
- En Windows, usar pool de threads: `--pool=threads`

---

## 📈 **Métricas de Performance**

Los tests miden:
- 📊 **Response time** de la API
- 🎯 **Confidence score** del agente (0.95 típico)
- ⚡ **Rate limiting** (60 requests/minuto)
- 🔄 **Workers online** (1+ workers activos)
- 💭 **Conversaciones** guardadas en Redis

---

**¡Todos los tests están optimizados y listos para usar!** 🎉
