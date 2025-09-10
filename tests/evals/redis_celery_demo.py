#!/usr/bin/env python3
"""
Demo of how Redis and Celery work in the AI Agent
"""
import sys
import os
import redis

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import requests
import json
import time
from agents_core.config.settings import settings


def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)


def show_redis_usage():
    """Show how Redis is used in the system"""
    print_section("🔴 REDIS - SYSTEM USAGE")
    
    try:
        redis_client = redis.from_url(settings.get_redis_url_for_memory(), decode_responses=True)
        
        # 1. CONVERSATIONAL MEMORY
        print("\n1️⃣ CONVERSATIONAL MEMORY:")
        conv_keys = [k for k in redis_client.keys('*') if k.startswith('conversation:')]
        print(f"   • Saved conversations: {len(conv_keys)}")
        
        if conv_keys:
            sample_key = conv_keys[0]
            messages = redis_client.llen(sample_key)
            print(f"   • Example: {sample_key}")
            print(f"   • Messages in this conversation: {messages}")
            
            # Mostrar un mensaje de ejemplo
            if messages > 0:
                sample_msg = redis_client.lindex(sample_key, -1)
                if sample_msg:
                    try:
                        msg_data = json.loads(sample_msg)
                        print(f"   • Last message: {msg_data.get('message', 'N/A')[:50]}...")
                    except:
                        print(f"   • Last message: {sample_msg[:50]}...")
        
        # 2. RATE LIMITING
        print("\n2️⃣ RATE LIMITING:")
        rate_keys = [k for k in redis_client.keys('*') if k.startswith('rate_limit:')]
        print(f"   • Active rate limit counters: {len(rate_keys)}")
        
        if rate_keys:
            sample_rate = rate_keys[0]
            count = redis_client.get(sample_rate)
            ttl = redis_client.ttl(sample_rate)
            print(f"   • Example: {sample_rate}")
            print(f"   • Requests used: {count}")
            print(f"   • Expires in: {ttl} seconds")
        
        # 3. CELERY TASKS
        print("\n3️⃣ CELERY TASKS:")
        celery_keys = [k for k in redis_client.keys('*') if 'celery' in k.lower() or k in ['agent_tasks', 'unacked']]
        print(f"   • Keys related to Celery: {len(celery_keys)}")
        
        for key in celery_keys[:3]:
            key_type = redis_client.type(key)
            if key_type == 'list':
                length = redis_client.llen(key)
                print(f"   • {key} ({key_type}): {length} items")
            elif key_type == 'hash':
                length = redis_client.hlen(key)
                print(f"   • {key} ({key_type}): {length} fields")
            else:
                print(f"   • {key} ({key_type})")
                
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")


def demo_conversation_memory():
    """Demonstrate how conversational memory works"""
    print_section("💭 DEMO: CONVERSATIONAL MEMORY")
    
    session_id = f"demo_memory_{int(time.time())}"
    
    print(f"📝 Starting conversation with session_id: {session_id}")
    
    # Mensaje 1
    print("\n🗣️ Usuario: 'Hi, what's your name?'")
    response1 = requests.post('http://localhost:8000/message', json={
        'text': "Hi, what's your name?",
        'session_id': session_id,
        'tenant_id': 'demo_tenant',
        'locale': 'en'
    })
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"🤖 Agent: {data1['reply'][:100]}...")
    
    time.sleep(1)
    
    # Mensaje 2 (debería recordar el contexto)
    print("\n🗣️ Usuario: 'What was my last question?'")
    response2 = requests.post('http://localhost:8000/message', json={
        'text': "What was my last question?",
        'session_id': session_id,  # Misma sesión
        'tenant_id': 'demo_tenant',
        'locale': 'en'
    })
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"🤖 Agent: {data2['reply'][:100]}...")
        print("\n✅ The agent should remember the previous question!")
    
    # Verificar en Redis
    try:
        redis_client = redis.from_url(settings.get_redis_url_for_memory(), decode_responses=True)
        conv_key = f"conversation:demo_tenant:{session_id}"
        messages = redis_client.llen(conv_key)
        print(f"\n📊 Messages saved in Redis: {messages}")
    except Exception as e:
        print(f"❌ Error checking Redis: {e}")


def demo_rate_limiting():
    """Demonstrate rate limiting"""
    print_section("⚡ DEMO: RATE LIMITING")
    
    session_id = f"rate_test_{int(time.time())}"
    
    print("📝 Sending multiple messages quickly...")
    print("   (Rate limit: 60 requests per minute per session)")
    
    for i in range(5):
        print(f"\n🔄 Message {i+1}/5")
        response = requests.post('http://localhost:8000/message', json={
            'text': f"Test message {i+1}",
            'session_id': session_id,
            'tenant_id': 'rate_test',
            'locale': 'en'
        })
        
        if response.status_code == 200:
            data = response.json()
            rate_info = data['metadata'].get('rate_limit', {})
            remaining = rate_info.get('remaining', 'N/A')
            print(f"   ✅ Success - Remaining: {remaining}")
        elif response.status_code == 429:
            print(f"   ⚡ Rate limited!")
            break
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        time.sleep(0.5)


def demo_celery_tasks():
    """Demonstrate Celery tasks"""
    print_section("🔧 DEMO: CELERY TASKS")
    
    print("📝 Testing Celery tasks...")
    
    # 1. Direct task test
    print("\n1️⃣ Direct task execution:")
    response = requests.post('http://localhost:8000/celery/process-direct')
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Task executed: {result}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # 2. Send async message
    print("\n2️⃣ Asynchronous message processing:")
    response = requests.post('http://localhost:8000/message/async', json={
        'text': "Process this asynchronously",
        'session_id': f"async_test_{int(time.time())}",
        'tenant_id': 'async_test',
        'locale': 'en'
    })
    
    if response.status_code == 202:
        result = response.json()
        task_id = result.get('task_id')
        print(f"   ✅ Task sent: {task_id}")
        
        # Check status
        if task_id:
            time.sleep(2)
            status_response = requests.get(f'http://localhost:8000/celery/task/{task_id}')
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   📊 Status: {status}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # 3. Worker status
    print("\n3️⃣ Celery worker status:")
    response = requests.get('http://localhost:8000/celery/status')
    if response.status_code == 200:
        status = response.json()
        print(f"   📊 Status: {status['status']}")
        print(f"   🔗 Redis connected: {status['redis_connected']}")
        if 'message' in status:
            print(f"   💡 Info: {status['message']}")
    else:
        print(f"   ❌ Error: {response.status_code}")


def main():
    print("🚀 DEMO: REDIS AND CELERY IN AI AGENT")
    
    print("\n📋 What do you want to see?")
    print("1. Current Redis content")
    print("2. Conversational memory demo")
    print("3. Rate limiting demo")
    print("4. Celery tasks demo")
    print("5. All of the above")
    print("0. Exit")
    
    try:
        opcion = input("\n🎯 Choose an option (0-5): ").strip()
        
        if opcion == "0":
            print("👋 Goodbye!")
            return
        elif opcion == "1":
            show_redis_usage()
        elif opcion == "2":
            demo_conversation_memory()
        elif opcion == "3":
            demo_rate_limiting()
        elif opcion == "4":
            demo_celery_tasks()
        elif opcion == "5":
            show_redis_usage()
            demo_conversation_memory()
            demo_rate_limiting()
            demo_celery_tasks()
        else:
            print("❌ Invalid option")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
