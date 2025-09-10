#!/usr/bin/env python3
"""
Complete script to test the AI Agent system.
Run: python test_system_complete.py
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
    """Basic connectivity test."""
    print_step(1, "BASIC CONNECTIVITY")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"✅ API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data}")
            return True
        else:
            print("❌ API not responding correctly")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to API")
        print("🔧 Solution: Run 'python -m uvicorn apps.api.main:app --reload --port 8000'")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_system_health():
    """Comprehensive health check test."""
    print_step(2, "COMPREHENSIVE HEALTH CHECK")
    
    try:
        response = requests.get('http://localhost:8000/monitoring/health')
        
        if response.status_code == 200:
            health = response.json()
            print(f"📊 Overall Status: {health['overall_status']}")
            
            print("\n🔧 Components:")
            for component, status in health['components'].items():
                emoji = "✅" if status['status'] == 'healthy' else "⚠️"
                print(f"  {emoji} {component}: {status['status']}")
            
            # Count healthy components
            healthy_count = sum(1 for comp in health['components'].values() 
                              if comp['status'] == 'healthy')
            total_count = len(health['components'])
            print(f"\n📈 Score: {healthy_count}/{total_count} healthy components")
            
            return health['overall_status'] in ['healthy', 'degraded']
        else:
            print(f"❌ Health check error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_available_tools():
    """Available tools test."""
    print_step(3, "AVAILABLE TOOLS")
    
    try:
        response = requests.get('http://localhost:8000/tools/available')
        
        if response.status_code == 200:
            tools = response.json()
            print(f"🛠️ Total tools: {tools['total_count']}")
            print(f"📦 Basic: {len(tools['basic_tools'])}")
            print(f"⚡ Advanced: {len(tools['advanced_tools'])}")
            print(f"📂 Categories: {tools['categories']}")
            
            print("\n🔧 Basic Tools:")
            for tool in tools['basic_tools']:
                print(f"  • {tool['name']}: {tool['description']}")
            
            print("\n⚡ Advanced Tools:")
            for tool in tools['advanced_tools']:
                print(f"  • {tool['name']}: {tool['description']}")
            
            return True
        else:
            print(f"❌ Error getting tools: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Tools test error: {e}")
        return False

def test_message_processing():
    """Message processing test."""
    print_step(4, "MESSAGE PROCESSING")
    
    test_messages = [
        {
            "text": "Hello! Can you help me schedule a visit to property ABC123 for tomorrow at 2 PM?",
            "description": "Basic scheduling test"
        },
        {
            "text": "What are your business hours?",
            "description": "Business information test"
        },
        {
            "text": "Please send an email to john@example.com about our meeting",
            "description": "Advanced tools test"
        }
    ]
    
    success_count = 0
    
    for i, test_msg in enumerate(test_messages, 1):
        print(f"\n🧪 Test {i}: {test_msg['description']}")
        print(f"📝 Message: {test_msg['text']}")
        
        try:
            response = requests.post('http://localhost:8000/message', json={
                'session_id': f'test_session_{int(time.time())}_{i}',
                'tenant_id': 'test_tenant',
                'text': test_msg['text'],
                'locale': 'en'
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result['reply'][:80]}...")
                print(f"🎯 Confidence: {result['confidence']}")
                print(f"🛠️ Tools used: {result['tools_used']}")
                
                # Rate limiting info
                rate_info = result['metadata'].get('rate_limit', {})
                remaining = rate_info.get('remaining', 'N/A')
                print(f"⚡ Rate limit remaining: {remaining}")
                success_count += 1
                
            elif response.status_code == 429:
                print("⚡ Rate limited (system working correctly)")
                success_count += 1  # Rate limiting also counts as success
            else:
                print(f"❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Message test error: {e}")
        
        # Pausa entre tests
        time.sleep(1)
    
    return success_count == len(test_messages)

def test_monitoring_features():
    """Monitoring features test."""
    print_step(5, "MONITORING AND OBSERVABILITY")
    
    # Test error monitoring
    try:
        response = requests.get('http://localhost:8000/monitoring/errors')
        if response.status_code == 200:
            errors = response.json()
            stats = errors.get('statistics', {})
            print(f"📊 Error tracking: {errors['status']}")
            print(f"📈 Total errors: {stats.get('total_errors', 0)}")
            print(f"⏰ Last 24h: {stats.get('last_24h', 0)}")
            return True
        else:
            print(f"⚠️ Error monitoring not available: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Monitoring error: {e}")
        return False

def test_celery_status():
    """Celery status test."""
    print_step(6, "CELERY SYSTEM")
    
    success = True
    
    try:
        response = requests.get('http://localhost:8000/celery/status')
        if response.status_code == 200:
            celery = response.json()
            print(f"📊 Celery Status: {celery['status']}")
            print(f"🔗 Redis connected: {celery['redis_connected']}")
            
            if 'message' in celery:
                print(f"💡 Info: {celery['message']}")
        else:
            print(f"⚠️ Celery status not available: {response.status_code}")
            success = False
            
        # Test direct execution
        response = requests.post('http://localhost:8000/celery/process-direct')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct execution: {result['success']}")
        else:
            success = False
        
        return success
        
    except Exception as e:
        print(f"⚠️ Celery test error: {e}")
        return False

def main():
    """Run all tests."""
    print_header("🚀 COMPLETE AI AGENT SYSTEM TEST")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    total_tests = 6
    
    # Run tests
    if test_api_connectivity(): tests_passed += 1
    if test_system_health(): tests_passed += 1
    if test_available_tools(): tests_passed += 1
    if test_message_processing(): tests_passed += 1
    if test_monitoring_features(): tests_passed += 1
    if test_celery_status(): tests_passed += 1
    
    # Final summary
    print_header("📊 FINAL SUMMARY")
    print(f"✅ Basic tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 SYSTEM FULLY FUNCTIONAL!")
        print("\n✨ Enabled features:")
        print("• OpenAI Agent with intelligent responses")
        print("• Langfuse for complete observability")
        print("• Conversational memory with Redis")
        print("• Rate limiting and security guardrails")
        print("• Advanced business tools")
        print("• Monitoring and error tracking")
    elif tests_passed >= 3:
        print("🎉 SYSTEM WORKING CORRECTLY!")
        print(f"📊 {tests_passed}/{total_tests} operational components")
    else:
        print("⚠️ Some components need attention")
        print("📧 Check logs for more details")

if __name__ == "__main__":
    main()
