class CacheHelper:
    """
    Clase auxiliar para manejar la caché de forma centralizada.
    """
    def __init__(self, cache_instance, default_timeout=60):
        self.cache = cache_instance
        self.default_timeout = default_timeout

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value, timeout=None):
        self.cache.set(key, value, timeout or self.default_timeout)

    def delete(self, key):
        self.cache.delete(key)