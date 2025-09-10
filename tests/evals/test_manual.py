#!/usr/bin/env python3
"""
Manual testing script for the AI Agent
Use it to test different functionalities step by step
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
    """System health test"""
    print_step("1", "SYSTEM HEALTH TEST")
    
    try:
        response = requests.get('http://localhost:8000/monitoring/health')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ System healthy!")
            print(f"• Overall status: {data['overall_status']}")
            print(f"• OpenAI Agent: {data['components']['openai_agent']['status']}")
            print(f"• Langfuse: {data['components']['langfuse']['status']}")
            print(f"• Redis: {data['components']['redis_memory']['status']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def test_message(text, description="Message test"):
    """Send a message to the agent"""
    print_step("*", f"{description.upper()}")
    print(f"📝 Sending: '{text}'")
    
    try:
        payload = {
            "text": text,
            "session_id": f"manual_test_{int(time.time())}",
            "tenant_id": "test_manual",
            "locale": "en"
        }
        
        print("🔄 Processing...")
        response = requests.post('http://localhost:8000/message', json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received!")
            print(f"💬 Response: {data['reply']}")
            print(f"🎯 Confidence: {data['confidence']}")
            print(f"🛠️ Tools used: {data['tools_used']}")
            
            # Rate limiting info
            rate_info = data['metadata'].get('rate_limit', {})
            print(f"⚡ Rate limit - Remaining: {rate_info.get('remaining', 'N/A')}")
            
            return True
        elif response.status_code == 429:
            print("⚡ Rate limited - waiting...")
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_tools():
    """View available tools"""
    print_step("2", "AVAILABLE TOOLS")
    
    try:
        response = requests.get('http://localhost:8000/tools/available')
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Total tools: {data['total_count']}")
            print(f"📂 Categories: {', '.join(data['categories'])}")
            
            print("\n🔧 Basic tools:")
            for tool in data['basic_tools']:
                print(f"  • {tool['name']}: {tool['description']}")
                
            print("\n⚡ Advanced tools:")
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
    """Interactive mode to chat with the agent"""
    print_step("🗣️", "INTERACTIVE MODE")
    print("Type 'exit' to quit")
    print("Type 'clear' for new session")
    
    session_id = f"interactive_{int(time.time())}"
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() in ['limpiar', 'clear', 'nueva']:
                session_id = f"interactive_{int(time.time())}"
                print("🔄 New session started")
                continue
                
            if not user_input:
                continue
                
            print("🤖 Agent: ", end="", flush=True)
            
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
                    print(f"🛠️ Tools used: {', '.join(data['tools_used'])}")
                    
            elif response.status_code == 429:
                print("⚡ Rate limited - try again in a few seconds")
            else:
                print(f"❌ Error {response.status_code}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main menu"""
    print_separator()
    print("🚀 AI AGENT MANUAL TESTER")
    print_separator()
    
    while True:
        print("\n📋 Options:")
        print("1. System health test")
        print("2. View available tools")
        print("3. Quick test - Business hours")
        print("4. Quick test - Schedule visit")
        print("5. Quick test - Send email")
        print("6. Interactive mode (chat)")
        print("7. Custom test")
        print("0. Exit")
        
        try:
            opcion = input("\n🎯 Choose an option (0-7): ").strip()
            
            if opcion == "0":
                print("👋 Goodbye!")
                break
                
            elif opcion == "1":
                test_health()
                
            elif opcion == "2":
                test_tools()
                
            elif opcion == "3":
                test_message("What are your business hours?", "Schedule test")
                
            elif opcion == "4":
                test_message("I want to schedule a visit to property ABC123 tomorrow at 2 PM. My name is John Doe, phone 555-1234, email john@email.com", "Programming test")
                
            elif opcion == "5":
                test_message("Please send an email to client@example.com with subject 'Meeting Reminder' and message 'Don't forget our meeting tomorrow at 3 PM'", "Email test")
                
            elif opcion == "6":
                interactive_mode()
                
            elif opcion == "7":
                texto = input("📝 Write your message: ")
                if texto.strip():
                    test_message(texto, "Custom test")
                    
            else:
                print("❌ Invalid option")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
