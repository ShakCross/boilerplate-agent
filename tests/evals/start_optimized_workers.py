#!/usr/bin/env python3
"""
Script to start optimized Celery workers
"""

import subprocess
import sys
import time
import signal
import psutil
import os

def kill_existing_workers():
    """Terminate existing Celery workers"""
    print("🔄 Terminating existing workers...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'celery' in cmdline and 'worker' in cmdline and 'agents_core' not in cmdline:
                print(f"   Terminating process: {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    
    time.sleep(2)

def start_optimized_workers():
    """Start optimized workers"""
    print("🚀 Starting optimized workers...")
    
    # Optimized configuration for Windows
    cmd = [
        sys.executable, '-m', 'celery',
        '-A', 'workers.celery_worker.app',
        'worker',
        '--loglevel=info',
        '--pool=threads',
        '--concurrency=8',  # More workers
        '--prefetch-multiplier=1',  # Better distribution
        '--without-gossip',  # Less overhead
        '--without-mingle',  # Faster startup
        '--without-heartbeat'  # Less overhead
    ]
    
    print(f"   Command: {' '.join(cmd)}")
    
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
        print("   Waiting for initialization...")
        
        # Show initial output
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 seconds maximum
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
    """Verify that workers are functioning"""
    print("🔍 Verifying workers...")
    
    import requests
    
    try:
        time.sleep(3)  # Give time to initialize
        
        response = requests.get('http://localhost:8000/celery/status', timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            workers_online = status.get('workers_online', 0)
            redis_connected = status.get('redis_connected', False)
            
            print(f"   Workers online: {workers_online}")
            print(f"   Redis connected: {redis_connected}")
            
            if workers_online > 0 and redis_connected:
                print("   ✅ Workers functioning correctly!")
                return True
            else:
                print("   ⚠️ Workers not detected")
                return False
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_async_task():
    """Test async task"""
    print("🧪 Testing async task...")
    
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
            print(f"   Task sent: {task_id}")
            
            # Check result
            time.sleep(5)
            status_response = requests.get(f'http://localhost:8000/celery/task/{task_id}', timeout=10)
            
            if status_response.status_code == 200:
                task_status = status_response.json()
                status = task_status.get('status', 'UNKNOWN')
                ready = task_status.get('ready', False)
                
                print(f"   Status: {status}")
                print(f"   Completed: {ready}")
                
                if ready and status == 'SUCCESS':
                    print("   ✅ Task processed successfully!")
                    return True
                else:
                    print("   ⚠️ Task still processing or failed")
                    return False
            else:
                print(f"   ❌ Error checking task: {status_response.status_code}")
                return False
        else:
            print(f"   ❌ Error sending task: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("  🚀 INDEPENDENT WORKERS OPTIMIZATION")
    print("=" * 60)
    
    try:
        # 1. Terminate existing workers
        kill_existing_workers()
        
        # 2. Start optimized workers
        process = start_optimized_workers()
        if not process:
            print("❌ Could not start workers")
            return
        
        # 3. Verify workers
        workers_ok = verify_workers()
        
        # 4. Test async task
        async_ok = test_async_task()
        
        # 5. Summary
        print("\n" + "=" * 60)
        print("  📊 OPTIMIZATION SUMMARY")
        print("=" * 60)
        print(f"Optimized workers: {'✅ YES' if workers_ok else '❌ NO'}")
        print(f"Async processing: {'✅ YES' if async_ok else '❌ NO'}")
        
        if workers_ok and async_ok:
            print("\n🎉 OPTIMIZATION SUCCESSFUL!")
            print("   • Independent workers functioning")
            print("   • Asynchronous processing active")
            print("   • Maximum performance achieved")
            
            print(f"\n💡 Workers running on PID: {process.pid}")
            print("   To stop them: Ctrl+C or kill the process")
            
            # Keep workers running
            try:
                print("\n⏳ Keeping workers active... (Ctrl+C to stop)")
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping workers...")
                process.terminate()
                
        else:
            print("\n⚠️ PARTIAL OPTIMIZATION")
            print("   • Some components need adjustments")
            process.terminate()
            
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
