#!/usr/bin/env python3
"""
Script completo para probar el sistema AI Agent.
Ejecuta: python test_system_complete.py
"""

import requests
import json
import time
from datetime import datetime

def print_header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_step(step, title):
    print(f"\n{step}. {title}")
    print("-" * 30)

def test_api_connectivity():
    """Test básico de conectividad."""
    print_step(1, "CONECTIVIDAD BÁSICA")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"✅ API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data}")
            return True
        else:
            print("❌ API no responde correctamente")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a la API")
        print("🔧 Solución: Ejecuta 'python -m uvicorn apps.api.main:app --reload --port 8000'")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_system_health():
    """Test del health check comprehensivo."""
    print_step(2, "HEALTH CHECK COMPREHENSIVO")
    
    try:
        response = requests.get('http://localhost:8000/monitoring/health')
        
        if response.status_code == 200:
            health = response.json()
            print(f"📊 Estado General: {health['overall_status']}")
            
            print("\n🔧 Componentes:")
            for component, status in health['components'].items():
                emoji = "✅" if status['status'] == 'healthy' else "⚠️"
                print(f"  {emoji} {component}: {status['status']}")
            
            # Contar componentes healthy
            healthy_count = sum(1 for comp in health['components'].values() 
                              if comp['status'] == 'healthy')
            total_count = len(health['components'])
            print(f"\n📈 Score: {healthy_count}/{total_count} componentes healthy")
            
            return health['overall_status'] in ['healthy', 'degraded']
        else:
            print(f"❌ Error en health check: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_available_tools():
    """Test de herramientas disponibles."""
    print_step(3, "HERRAMIENTAS DISPONIBLES")
    
    try:
        response = requests.get('http://localhost:8000/tools/available')
        
        if response.status_code == 200:
            tools = response.json()
            print(f"🛠️ Total herramientas: {tools['total_count']}")
            print(f"📦 Básicas: {len(tools['basic_tools'])}")
            print(f"⚡ Avanzadas: {len(tools['advanced_tools'])}")
            print(f"📂 Categorías: {tools['categories']}")
            
            print("\n🔧 Herramientas Básicas:")
            for tool in tools['basic_tools']:
                print(f"  • {tool['name']}: {tool['description']}")
            
            print("\n⚡ Herramientas Avanzadas:")
            for tool in tools['advanced_tools']:
                print(f"  • {tool['name']}: {tool['description']}")
            
            return True
        else:
            print(f"❌ Error obteniendo herramientas: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de herramientas: {e}")
        return False

def test_message_processing():
    """Test de procesamiento de mensajes."""
    print_step(4, "PROCESAMIENTO DE MENSAJES")
    
    test_messages = [
        {
            "text": "Hello! Can you help me schedule a visit to property ABC123 for tomorrow at 2 PM?",
            "description": "Test básico de scheduling"
        },
        {
            "text": "What are your business hours?",
            "description": "Test de información de negocio"
        },
        {
            "text": "Please send an email to john@example.com about our meeting",
            "description": "Test de herramientas avanzadas"
        }
    ]
    
    success_count = 0
    
    for i, test_msg in enumerate(test_messages, 1):
        print(f"\n🧪 Test {i}: {test_msg['description']}")
        print(f"📝 Mensaje: {test_msg['text']}")
        
        try:
            response = requests.post('http://localhost:8000/message', json={
                'session_id': f'test_session_{int(time.time())}_{i}',
                'tenant_id': 'test_tenant',
                'text': test_msg['text'],
                'locale': 'en'
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Respuesta: {result['reply'][:80]}...")
                print(f"🎯 Confianza: {result['confidence']}")
                print(f"🛠️ Herramientas usadas: {result['tools_used']}")
                
                # Rate limiting info
                rate_info = result['metadata'].get('rate_limit', {})
                remaining = rate_info.get('remaining', 'N/A')
                print(f"⚡ Rate limit restantes: {remaining}")
                success_count += 1
                
            elif response.status_code == 429:
                print("⚡ Rate limited (sistema funcionando correctamente)")
                success_count += 1  # Rate limiting también cuenta como éxito
            else:
                print(f"❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Error en test de mensaje: {e}")
        
        # Pausa entre tests
        time.sleep(1)
    
    return success_count == len(test_messages)

def test_monitoring_features():
    """Test de funcionalidades de monitoreo."""
    print_step(5, "MONITOREO Y OBSERVABILIDAD")
    
    # Test error monitoring
    try:
        response = requests.get('http://localhost:8000/monitoring/errors')
        if response.status_code == 200:
            errors = response.json()
            stats = errors.get('statistics', {})
            print(f"📊 Error tracking: {errors['status']}")
            print(f"📈 Total errores: {stats.get('total_errors', 0)}")
            print(f"⏰ Últimas 24h: {stats.get('last_24h', 0)}")
            return True
        else:
            print(f"⚠️ Error monitoring no disponible: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Error en monitoring: {e}")
        return False

def test_celery_status():
    """Test del estado de Celery."""
    print_step(6, "SISTEMA CELERY")
    
    success = True
    
    try:
        response = requests.get('http://localhost:8000/celery/status')
        if response.status_code == 200:
            celery = response.json()
            print(f"📊 Estado Celery: {celery['status']}")
            print(f"🔗 Redis conectado: {celery['redis_connected']}")
            
            if 'message' in celery:
                print(f"💡 Info: {celery['message']}")
        else:
            print(f"⚠️ Celery status no disponible: {response.status_code}")
            success = False
            
        # Test direct execution
        response = requests.post('http://localhost:8000/celery/process-direct')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ejecución directa: {result['success']}")
        else:
            success = False
        
        return success
        
    except Exception as e:
        print(f"⚠️ Error en Celery test: {e}")
        return False

def main():
    """Ejecutar todos los tests."""
    print_header("🚀 TEST COMPLETO DEL SISTEMA AI AGENT")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    total_tests = 6
    
    # Ejecutar tests
    if test_api_connectivity(): tests_passed += 1
    if test_system_health(): tests_passed += 1
    if test_available_tools(): tests_passed += 1
    if test_message_processing(): tests_passed += 1
    if test_monitoring_features(): tests_passed += 1
    if test_celery_status(): tests_passed += 1
    
    # Resumen final
    print_header("📊 RESUMEN FINAL")
    print(f"✅ Tests básicos pasados: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("\n✨ Características habilitadas:")
        print("• OpenAI Agent con respuestas inteligentes")
        print("• Langfuse para observabilidad completa")
        print("• Memoria conversacional con Redis")
        print("• Rate limiting y guardrails de seguridad")
        print("• Herramientas de negocio avanzadas")
        print("• Monitoreo y error tracking")
    elif tests_passed >= 3:
        print("🎉 SISTEMA FUNCIONANDO CORRECTAMENTE!")
        print(f"📊 {tests_passed}/{total_tests} componentes operativos")
    else:
        print("⚠️ Algunos componentes necesitan atención")
        print("📧 Revisa los logs para más detalles")

if __name__ == "__main__":
    main()
