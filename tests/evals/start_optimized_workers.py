#!/usr/bin/env python3
"""
Script para iniciar workers optimizados de Celery
"""

import subprocess
import sys
import time
import signal
import psutil
import os

def kill_existing_workers():
    """Terminar workers de Celery existentes"""
    print("🔄 Terminando workers existentes...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'celery' in cmdline and 'worker' in cmdline and 'agents_core' not in cmdline:
                print(f"   Terminando proceso: {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    
    time.sleep(2)

def start_optimized_workers():
    """Iniciar workers optimizados"""
    print("🚀 Iniciando workers optimizados...")
    
    # Configuración optimizada para Windows
    cmd = [
        sys.executable, '-m', 'celery',
        '-A', 'workers.celery_worker.app',
        'worker',
        '--loglevel=info',
        '--pool=threads',
        '--concurrency=8',  # Más workers
        '--prefetch-multiplier=1',  # Mejor distribución
        '--without-gossip',  # Menos overhead
        '--without-mingle',  # Inicio más rápido
        '--without-heartbeat'  # Menos overhead
    ]
    
    print(f"   Comando: {' '.join(cmd)}")
    
    try:
        # Iniciar proceso en background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print(f"   PID: {process.pid}")
        print("   Esperando inicialización...")
        
        # Mostrar output inicial
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 segundos máximo
            line = process.stdout.readline()
            if line:
                print(f"   {line.strip()}")
                if 'ready' in line.lower():
                    break
        
        return process
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def verify_workers():
    """Verificar que los workers están funcionando"""
    print("🔍 Verificando workers...")
    
    import requests
    
    try:
        time.sleep(3)  # Dar tiempo a inicializar
        
        response = requests.get('http://localhost:8000/celery/status', timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            workers_online = status.get('workers_online', 0)
            redis_connected = status.get('redis_connected', False)
            
            print(f"   Workers online: {workers_online}")
            print(f"   Redis conectado: {redis_connected}")
            
            if workers_online > 0 and redis_connected:
                print("   ✅ Workers funcionando correctamente!")
                return True
            else:
                print("   ⚠️ Workers no detectados")
                return False
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_async_task():
    """Probar task asíncrona"""
    print("🧪 Probando task asíncrona...")
    
    import requests
    
    try:
        # Enviar task
        response = requests.post('http://localhost:8000/message/async', json={
            'text': 'Test optimized workers performance',
            'session_id': f'perf_test_{int(time.time())}',
            'tenant_id': 'performance_test',
            'locale': 'en'
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            print(f"   Task enviada: {task_id}")
            
            # Verificar resultado
            time.sleep(5)
            status_response = requests.get(f'http://localhost:8000/celery/task/{task_id}', timeout=10)
            
            if status_response.status_code == 200:
                task_status = status_response.json()
                status = task_status.get('status', 'UNKNOWN')
                ready = task_status.get('ready', False)
                
                print(f"   Estado: {status}")
                print(f"   Completada: {ready}")
                
                if ready and status == 'SUCCESS':
                    print("   ✅ Task procesada exitosamente!")
                    return True
                else:
                    print("   ⚠️ Task aún procesando o falló")
                    return False
            else:
                print(f"   ❌ Error verificando task: {status_response.status_code}")
                return False
        else:
            print(f"   ❌ Error enviando task: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("  🚀 OPTIMIZACIÓN DE WORKERS INDEPENDIENTES")
    print("=" * 60)
    
    try:
        # 1. Terminar workers existentes
        kill_existing_workers()
        
        # 2. Iniciar workers optimizados
        process = start_optimized_workers()
        if not process:
            print("❌ No se pudieron iniciar los workers")
            return
        
        # 3. Verificar workers
        workers_ok = verify_workers()
        
        # 4. Probar task asíncrona
        async_ok = test_async_task()
        
        # 5. Resumen
        print("\n" + "=" * 60)
        print("  📊 RESUMEN DE OPTIMIZACIÓN")
        print("=" * 60)
        print(f"Workers optimizados: {'✅ SÍ' if workers_ok else '❌ NO'}")
        print(f"Procesamiento async: {'✅ SÍ' if async_ok else '❌ NO'}")
        
        if workers_ok and async_ok:
            print("\n🎉 ¡OPTIMIZACIÓN EXITOSA!")
            print("   • Workers independientes funcionando")
            print("   • Procesamiento asíncrono activo")
            print("   • Máximo rendimiento alcanzado")
            
            print(f"\n💡 Workers ejecutándose en PID: {process.pid}")
            print("   Para detenerlos: Ctrl+C o kill el proceso")
            
            # Mantener workers corriendo
            try:
                print("\n⏳ Manteniendo workers activos... (Ctrl+C para detener)")
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo workers...")
                process.terminate()
                
        else:
            print("\n⚠️ OPTIMIZACIÓN PARCIAL")
            print("   • Algunos componentes necesitan ajustes")
            process.terminate()
            
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
