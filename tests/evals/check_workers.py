#!/usr/bin/env python3
"""
Script para verificar el estado de los workers de Celery
"""

import requests
import time
import json

def check_workers():
    print('Verificando estado de workers...')
    
    try:
        # Dar tiempo a que los workers inicien
        time.sleep(2)
        
        response = requests.get('http://localhost:8000/celery/status')
        
        if response.status_code == 200:
            status = response.json()
            print(f'Estado: {status.get("status", "unknown")}')
            print(f'Redis conectado: {status.get("redis_connected", False)}')
            
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
    print('\nTestando procesamiento asincrono...')
    
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
            print(f'Task enviada: {task_id}')
            
            # Esperar y verificar resultado
            time.sleep(3)
            
            status_response = requests.get(f'http://localhost:8000/celery/task/{task_id}')
            if status_response.status_code == 200:
                task_status = status_response.json()
                print(f'Estado de task: {json.dumps(task_status, indent=2)}')
                return True
            else:
                print(f'Error verificando task: {status_response.status_code}')
                return False
                
        else:
            print(f'Error enviando task: {response.status_code}')
            print(f'Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

if __name__ == "__main__":
    print('=== VERIFICACION DE WORKERS OPTIMIZADOS ===')
    
    workers_ok = check_workers()
    async_ok = test_async_processing()
    
    print('\n=== RESUMEN ===')
    print(f'Workers funcionando: {"SI" if workers_ok else "NO"}')
    print(f'Procesamiento async: {"SI" if async_ok else "NO"}')
    
    if workers_ok and async_ok:
        print('\nEXITO: Sistema optimizado con workers independientes!')
    else:
        print('\nPENDIENTE: Aun necesita optimizacion')
