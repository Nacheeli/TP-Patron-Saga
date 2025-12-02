
from typing import Dict, Any
import os

def _get_cache_config() -> Dict[str, Any]:
    
    redis_host = os.getenv('REDIS_HOST')
    if not redis_host:
        raise ValueError("REDIS_HOST environment variable is required")
    
    try:
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
    except ValueError as e:
        raise ValueError(f"REDIS_PORT and REDIS_DB must be integers: {e}")
    
    return {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_REDIS_HOST': redis_host,
        'CACHE_REDIS_PORT': redis_port,
        'CACHE_REDIS_DB': redis_db,
        'CACHE_REDIS_PASSWORD': os.getenv('REDIS_PASSWORD'),
        'CACHE_KEY_PREFIX': 'flask_',
    }


cache_config: Dict[str, Any] = _get_cache_config()