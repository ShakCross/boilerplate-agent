#!/usr/bin/env python3
import sys
import os
import redis

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from agents_core.config.settings import settings

print('=== CONTENIDO ACTUAL DE REDIS ===')
try:
    redis_client = redis.from_url(settings.get_redis_url_for_memory(), decode_responses=True)
    keys = redis_client.keys('*')
    print(f'Total keys en Redis: {len(keys)}')
    
    if keys:
        print('\nKeys encontradas:')
        for key in keys[:10]:
            key_type = redis_client.type(key)
            print(f'  • {key} ({key_type})')
        if len(keys) > 10:
            print(f'  ... y {len(keys) - 10} mas')
    else:
        print('Redis esta vacio')
        
except Exception as e:
    print(f'Error: {e}')
