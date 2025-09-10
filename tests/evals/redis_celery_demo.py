#!/usr/bin/env python3
"""
Demo de cómo funcionan Redis y Celery en el AI Agent
"""

import redis
import requests
import json
import time
from agents_core.config.settings import settings


def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)


def show_redis_usage():
    """Mostrar cómo se usa Redis en el sistema"""
    print_section("🔴 REDIS - USOS EN EL SISTEMA")
    
    try:
        redis_client = redis.from_url(settings.get_redis_url_for_memory(), decode_responses=True)
        
        # 1. MEMORIA CONVERSACIONAL
        print("\n1️⃣ MEMORIA CONVERSACIONAL:")
        conv_keys = [k for k in redis_client.keys('*') if k.startswith('conversation:')]
        print(f"   • Conversaciones guardadas: {len(conv_keys)}")
        
        if conv_keys:
            sample_key = conv_keys[0]
            messages = redis_client.llen(sample_key)
            print(f"   • Ejemplo: {sample_key}")
            print(f"   • Mensajes en esta conversación: {messages}")
            
            # Mostrar un mensaje de ejemplo
            if messages > 0:
                sample_msg = redis_client.lindex(sample_key, -1)
                if sample_msg:
                    try:
                        msg_data = json.loads(sample_msg)
                        print(f"   • Último mensaje: {msg_data.get('message', 'N/A')[:50]}...")
                    except:
                        print(f"   • Último mensaje: {sample_msg[:50]}...")
        
        # 2. RATE LIMITING
        print("\n2️⃣ RATE LIMITING:")
        rate_keys = [k for k in redis_client.keys('*') if k.startswith('rate_limit:')]
        print(f"   • Contadores de rate limit activos: {len(rate_keys)}")
        
        if rate_keys:
            sample_rate = rate_keys[0]
            count = redis_client.get(sample_rate)
            ttl = redis_client.ttl(sample_rate)
            print(f"   • Ejemplo: {sample_rate}")
            print(f"   • Requests usados: {count}")
            print(f"   • Expira en: {ttl} segundos")
        
        # 3. CELERY TASKS
        print("\n3️⃣ CELERY TASKS:")
        celery_keys = [k for k in redis_client.keys('*') if 'celery' in k.lower() or k in ['agent_tasks', 'unacked']]
        print(f"   • Keys relacionadas con Celery: {len(celery_keys)}")
        
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
        print(f"❌ Error conectando a Redis: {e}")


def demo_conversation_memory():
    """Demostrar cómo funciona la memoria conversacional"""
    print_section("💭 DEMO: MEMORIA CONVERSACIONAL")
    
    session_id = f"demo_memory_{int(time.time())}"
    
    print(f"📝 Iniciando conversación con session_id: {session_id}")
    
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
        print(f"🤖 Agente: {data1['reply'][:100]}...")
    
    time.sleep(1)
    
    # Mensaje 2 (debería recordar el contexto)
    print("\n🗣️ Usuario: 'What did I just ask you?'")
    response2 = requests.post('http://localhost:8000/message', json={
        'text': "What did I just ask you?",
        'session_id': session_id,  # Misma sesión
        'tenant_id': 'demo_tenant',
        'locale': 'en'
    })
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"🤖 Agente: {data2['reply'][:100]}...")
        print("\n✅ El agente debería recordar la pregunta anterior!")
    
    # Verificar en Redis
    try:
        redis_client = redis.from_url(settings.get_redis_url_for_memory(), decode_responses=True)
        conv_key = f"conversation:demo_tenant:{session_id}"
        messages = redis_client.llen(conv_key)
        print(f"\n📊 Mensajes guardados en Redis: {messages}")
    except Exception as e:
        print(f"❌ Error verificando Redis: {e}")


def demo_rate_limiting():
    """Demostrar rate limiting"""
    print_section("⚡ DEMO: RATE LIMITING")
    
    session_id = f"rate_test_{int(time.time())}"
    
    print("📝 Enviando múltiples mensajes rápidamente...")
    print("   (Rate limit: 60 requests por minuto por sesión)")
    
    for i in range(5):
        print(f"\n🔄 Mensaje {i+1}/5")
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
            print(f"   ✅ Éxito - Restantes: {remaining}")
        elif response.status_code == 429:
            print(f"   ⚡ Rate limited!")
            break
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        time.sleep(0.5)


def demo_celery_tasks():
    """Demostrar tasks de Celery"""
    print_section("🔧 DEMO: CELERY TASKS")
    
    print("📝 Probando Celery tasks...")
    
    # 1. Test directo de task
    print("\n1️⃣ Ejecución directa de task:")
    response = requests.post('http://localhost:8000/celery/process-direct')
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Task ejecutada: {result}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # 2. Enviar mensaje asíncrono
    print("\n2️⃣ Procesamiento asíncrono de mensaje:")
    response = requests.post('http://localhost:8000/message/async', json={
        'text': "Process this asynchronously",
        'session_id': f"async_test_{int(time.time())}",
        'tenant_id': 'async_test',
        'locale': 'en'
    })
    
    if response.status_code == 202:
        result = response.json()
        task_id = result.get('task_id')
        print(f"   ✅ Task enviada: {task_id}")
        
        # Verificar estado
        if task_id:
            time.sleep(2)
            status_response = requests.get(f'http://localhost:8000/celery/task/{task_id}')
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   📊 Estado: {status}")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # 3. Estado de workers
    print("\n3️⃣ Estado de Celery workers:")
    response = requests.get('http://localhost:8000/celery/status')
    if response.status_code == 200:
        status = response.json()
        print(f"   📊 Estado: {status['status']}")
        print(f"   🔗 Redis conectado: {status['redis_connected']}")
        if 'message' in status:
            print(f"   💡 Info: {status['message']}")
    else:
        print(f"   ❌ Error: {response.status_code}")


def main():
    print("🚀 DEMO: REDIS Y CELERY EN AI AGENT")
    
    print("\n📋 ¿Qué quieres ver?")
    print("1. Contenido actual de Redis")
    print("2. Demo de memoria conversacional")
    print("3. Demo de rate limiting")
    print("4. Demo de Celery tasks")
    print("5. Todo lo anterior")
    print("0. Salir")
    
    try:
        opcion = input("\n🎯 Elige una opción (0-5): ").strip()
        
        if opcion == "0":
            print("👋 ¡Hasta luego!")
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
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
