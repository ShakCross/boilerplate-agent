#!/usr/bin/env python3
"""
Script to check the status of Celery workers
"""

import requests
import time
import json

def check_workers():
    print('Checking worker status...')
    
    try:
        # Give time for workers to start
        time.sleep(2)
        
        response = requests.get('http://localhost:8000/celery/status')
        
        if response.status_code == 200:
            status = response.json()
            print(f'Status: {status.get("status", "unknown")}')
            print(f'Redis connected: {status.get("redis_connected", False)}')
            
            if 'workers_online' in status:
                print(f'Workers online: {status["workers_online"]}')
            
            if 'message' in status:
                print(f'Info: {status["message"]}')
                
            if 'stats' in status:
                print(f'Stats: {json.dumps(status["stats"], indent=2)}')
                
            return status.get("status") == "healthy"
            
        else:
            print(f'Error HTTP: {response.status_code}')
            print(f'Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

def test_async_processing():
    print('\nTesting asynchronous processing...')
    
    try:
        response = requests.post('http://localhost:8000/message/async', json={
            'text': 'Test async processing with workers',
            'session_id': f'worker_test_{int(time.time())}',
            'tenant_id': 'worker_test',
            'locale': 'en'
        })
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            print(f'Task sent: {task_id}')
            
            # Wait and check result
            time.sleep(3)
            
            status_response = requests.get(f'http://localhost:8000/celery/task/{task_id}')
            if status_response.status_code == 200:
                task_status = status_response.json()
                print(f'Task status: {json.dumps(task_status, indent=2)}')
                return True
            else:
                print(f'Error checking task: {status_response.status_code}')
                return False
                
        else:
            print(f'Error sending task: {response.status_code}')
            print(f'Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

if __name__ == "__main__":
    print('=== OPTIMIZED WORKERS VERIFICATION ===')
    
    workers_ok = check_workers()
    async_ok = test_async_processing()
    
    print('\n=== SUMMARY ===')
    print(f'Workers functioning: {"YES" if workers_ok else "NO"}')
    print(f'Async processing: {"YES" if async_ok else "NO"}')
    
    if workers_ok and async_ok:
        print('\nSUCCESS: Optimized system with independent workers!')
    else:
        print('\nPENDING: Still needs optimization')
