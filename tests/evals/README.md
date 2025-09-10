# 🧪 Tests & Evaluations

This folder contains testing and evaluation scripts for the AI Agent.

## 📁 Organized Files

### 🔬 **Main Tests**

#### `test_system_complete.py`
**Complete system test** - The main test that verifies all components.

```bash
cd tests/evals
python test_system_complete.py
```

**What it tests:**
- ✅ Basic API connectivity
- ✅ Comprehensive health check (6/6 components)
- ✅ Available tools (8 tools)
- ✅ AI message processing
- ✅ Monitoring and observability
- ✅ Celery system and workers

---

### 🐰 **Celery & Workers Tests**

#### `check_workers.py`
**Optimized workers verification** - Verifies that independent workers function.

```bash
cd tests/evals
python check_workers.py
```

**What it verifies:**
- 🔍 Celery workers status
- ⚡ Asynchronous processing
- 📊 Task statistics

#### `start_optimized_workers.py`
**Advanced worker optimization** - Starts workers with optimized configuration.

```bash
cd tests/evals
python start_optimized_workers.py
```

**Features:**
- 🚀 8 concurrent workers
- 🧵 Thread pool (Windows compatible)
- 📈 High-performance configuration

---

### 🔴 **Redis Tests**

#### `check_redis.py`
**Redis verification** - Shows current Redis content.

```bash
cd tests/evals
python check_redis.py
```

**What it shows:**
- 📊 Total keys in Redis
- 💭 Saved conversations
- ⚡ Active rate limiting
- 🔧 Celery tasks

#### `redis_celery_demo.py`
**Interactive Redis and Celery demo** - Demonstrates how Redis and Celery work.

```bash
cd tests/evals
python redis_celery_demo.py
```

**Demo options:**
1. Current Redis content
2. Conversational memory demo
3. Rate limiting demo
4. Celery tasks demo
5. All of the above

---

### 🎮 **Interactive Manual Test**

#### `test_manual.py`
**Interactive manual tester** - Interface to manually test the system.

```bash
cd tests/evals
python test_manual.py
```

**Available options:**
1. System health test
2. View available tools
3. Quick test - Business hours
4. Quick test - Schedule visit
5. Quick test - Send email
6. **Interactive mode (chat)**
7. Custom test

---

## 🚀 **Quick Usage Guide**

### **Complete System Test:**
```bash
cd tests/evals
python test_system_complete.py
```

### **Verify Optimized Workers:**
```bash
cd tests/evals
python check_workers.py
```

### **Interactive Chat:**
```bash
cd tests/evals
python test_manual.py
# Choose option 6 for chat mode
```

### **View Redis Status:**
```bash
cd tests/evals
python check_redis.py
```

---

## 📊 **Expected Results**

### **Fully Functional System:**
```
✅ Basic tests passed: 6/6
🎉 SYSTEM FULLY FUNCTIONAL!

✨ Enabled features:
• OpenAI Agent with intelligent responses
• Langfuse for complete observability
• Conversational memory with Redis
• Rate limiting and security guardrails
• Advanced business tools
• Monitoring and error tracking
```

### **Optimized Workers:**
```
=== SUMMARY ===
Workers functioning: YES
Async processing: YES

SUCCESS: Optimized system with independent workers!
```

---

## 🛠️ **Troubleshooting**

### **If the test fails:**
1. Verify the API is running: `python -m uvicorn apps.api.main:app --reload --port 8000`
2. Verify Redis is running: `docker-compose up redis -d`
3. Verify workers: `python check_workers.py`

### **If Redis is empty:**
- Normal at startup, will fill with usage
- Run some tests to generate data

### **If Celery doesn't work:**
- Use the optimized script: `python start_optimized_workers.py`
- On Windows, use thread pool: `--pool=threads`

---

## 📈 **Performance Metrics**

The tests measure:
- 📊 API **Response time**
- 🎯 Agent **Confidence score** (typical 0.95)
- ⚡ **Rate limiting** (60 requests/minute)
- 🔄 **Workers online** (1+ active workers)
- 💭 **Conversations** saved in Redis

---

**All tests are optimized and ready to use!** 🎉
