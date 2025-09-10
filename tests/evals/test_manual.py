#!/usr/bin/env python3
"""
Script de pruebas manuales para el AI Agent
Úsalo para probar diferentes funcionalidades paso a paso
"""

import requests
import json
import time
from datetime import datetime


def print_separator():
    print("=" * 60)


def print_step(step, title):
    print(f"\n{step}. {title}")
    print("-" * 40)


def test_health():
    """Test de salud del sistema"""
    print_step("1", "TEST DE SALUD DEL SISTEMA")
    
    try:
        response = requests.get('http://localhost:8000/health')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sistema saludable!")
            print(f"• OpenAI Agent: {data['components']['openai_agent']}")
            print(f"• Langfuse: {data['components']['langfuse']}")
            print(f"• Redis: {data['components']['redis_memory']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def test_message(text, description="Test de mensaje"):
    """Enviar un mensaje al agente"""
    print_step("*", f"{description.upper()}")
    print(f"📝 Enviando: '{text}'")
    
    try:
        payload = {
            "text": text,
            "session_id": f"manual_test_{int(time.time())}",
            "tenant_id": "test_manual",
            "locale": "en"
        }
        
        print("🔄 Procesando...")
        response = requests.post('http://localhost:8000/message', json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta recibida!")
            print(f"💬 Respuesta: {data['reply']}")
            print(f"🎯 Confianza: {data['confidence']}")
            print(f"🛠️ Herramientas usadas: {data['tools_used']}")
            
            # Rate limiting info
            rate_info = data['metadata'].get('rate_limit', {})
            print(f"⚡ Rate limit - Restantes: {rate_info.get('remaining', 'N/A')}")
            
            return True
        elif response.status_code == 429:
            print("⚡ Rate limited - esperando...")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_tools():
    """Ver herramientas disponibles"""
    print_step("2", "HERRAMIENTAS DISPONIBLES")
    
    try:
        response = requests.get('http://localhost:8000/tools/available')
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Total herramientas: {data['total_count']}")
            print(f"📂 Categorías: {', '.join(data['categories'])}")
            
            print("\n🔧 Herramientas básicas:")
            for tool in data['basic_tools']:
                print(f"  • {tool['name']}: {tool['description']}")
                
            print("\n⚡ Herramientas avanzadas:")
            for tool in data['advanced_tools']:
                print(f"  • {tool['name']}: {tool['description']}")
                
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def interactive_mode():
    """Modo interactivo para chatear con el agente"""
    print_step("🗣️", "MODO INTERACTIVO")
    print("Escribe 'salir' para terminar")
    print("Escribe 'limpiar' para nueva sesión")
    
    session_id = f"interactive_{int(time.time())}"
    
    while True:
        try:
            user_input = input("\n💬 Tú: ").strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
                
            if user_input.lower() in ['limpiar', 'clear', 'nueva']:
                session_id = f"interactive_{int(time.time())}"
                print("🔄 Nueva sesión iniciada")
                continue
                
            if not user_input:
                continue
                
            print("🤖 Agente: ", end="", flush=True)
            
            payload = {
                "text": user_input,
                "session_id": session_id,
                "tenant_id": "interactive_test",
                "locale": "en"
            }
            
            response = requests.post('http://localhost:8000/message', json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(data['reply'])
                
                if data['tools_used']:
                    print(f"🛠️ Herramientas usadas: {', '.join(data['tools_used'])}")
                    
            elif response.status_code == 429:
                print("⚡ Rate limited - intenta en unos segundos")
            else:
                print(f"❌ Error {response.status_code}")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Menú principal"""
    print_separator()
    print("🚀 TESTER MANUAL DEL AI AGENT")
    print_separator()
    
    while True:
        print("\n📋 Opciones:")
        print("1. Test de salud del sistema")
        print("2. Ver herramientas disponibles")
        print("3. Test rápido - Horarios de negocio")
        print("4. Test rápido - Programar visita")
        print("5. Test rápido - Enviar email")
        print("6. Modo interactivo (chat)")
        print("7. Test personalizado")
        print("0. Salir")
        
        try:
            opcion = input("\n🎯 Elige una opción (0-7): ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
                
            elif opcion == "1":
                test_health()
                
            elif opcion == "2":
                test_tools()
                
            elif opcion == "3":
                test_message("What are your business hours?", "Test de horarios")
                
            elif opcion == "4":
                test_message("I want to schedule a visit to property ABC123 tomorrow at 2 PM. My name is John Doe, phone 555-1234, email john@email.com", "Test de programación")
                
            elif opcion == "5":
                test_message("Please send an email to client@example.com with subject 'Meeting Reminder' and message 'Don't forget our meeting tomorrow at 3 PM'", "Test de email")
                
            elif opcion == "6":
                interactive_mode()
                
            elif opcion == "7":
                texto = input("📝 Escribe tu mensaje: ")
                if texto.strip():
                    test_message(texto, "Test personalizado")
                    
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
