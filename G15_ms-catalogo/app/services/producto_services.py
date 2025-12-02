from app import cache, redis_client
from app.models import Producto
from app.repositories import ProductoRepository
from contextlib import contextmanager
import time
class ProductoService:
    CACHE_TIMEOUT = 300  
    REDIS_LOCK_TIMEOUT = 10 

    def __init__(self, repository=None):
        self.repository = repository or ProductoRepository()

    @contextmanager
    def redis_lock(self, producto_id: int):
        lock_key = f"producto_lock_{producto_id}"
        lock_value = str(time.time())

        if redis_client.set(lock_key, lock_value, ex=self.REDIS_LOCK_TIMEOUT, nx=True):
            try:
                yield
            finally:
                redis_client.delete(lock_key)
        else:
            raise Exception(
                f"El recurso está bloqueado para el producto {producto_id}.")

    def all(self) -> list[Producto]:
        cached_productos = cache.get('productos')
        if cached_productos is None:
            productos = self.repository.get_all()
            if productos:
                cache.set('productos', productos, timeout=self.CACHE_TIMEOUT)
            return productos
        return cached_productos

    def add(self, producto: Producto) -> Producto:
        new_producto = self.repository.save(producto)
        cache.set(f'producto_{new_producto.id}',
                  new_producto, timeout=self.CACHE_TIMEOUT)
        cache.delete('productos') 
        return new_producto

    def update(self, producto_id: int, updated_producto: Producto) -> Producto:
        with self.redis_lock(producto_id):
            existing_producto = self.find(producto_id)
            if not existing_producto:
                raise Exception(
                    f"Producto con ID {producto_id} no encontrado.")

            if updated_producto.precio < 0:
                raise ValueError("El precio no puede ser negativo.")

            existing_producto.nombre = updated_producto.nombre
            existing_producto.precio = updated_producto.precio
            existing_producto.activado = updated_producto.activado

            saved_producto = self.repository.save(existing_producto)

            cache.set(f'producto_{producto_id}',
                      saved_producto, timeout=self.CACHE_TIMEOUT)
            cache.delete('productos')

            return saved_producto

    def delete(self, producto_id: int) -> bool:
        with self.redis_lock(producto_id):
            deleted = self.repository.delete(producto_id)
            if deleted:
                cache.delete(f'producto_{producto_id}')
                cache.delete('productos')
            return deleted

    def find(self, producto_id: int) -> Producto:
        cached_producto = cache.get(f'producto_{producto_id}')
        if cached_producto is None:
            producto = self.repository.get_by_id(producto_id)
            if producto:
                cache.set(f'producto_{producto_id}',
                          producto, timeout=self.CACHE_TIMEOUT)
            return producto
        return cached_producto
