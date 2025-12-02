from app import cache, db
from app.models import Pagos
from app.repositories import PagosRepository

import time
import random
import logging

# Config logger
logger = logging.getLogger(__name__)

class PagosService:
    def __init__(self, repository=None, cache_helper=None):
        from app.services import CacheHelper
        self.repository = repository or PagosRepository()
        self.cache = cache_helper or CacheHelper(cache)
    
    def all(self) -> list[Pagos]:
        cached_pagos = self.cache.get('pagos')
        if cached_pagos is None:
            pagos = self.repository.get_all()
            if pagos:
                self.cache.set('pagos', pagos)
            return pagos
        return cached_pagos

    def realizar_transaccion(self, pago: Pagos) -> dict:
        """
        Endpoint 1: Realiza una transacción que retorna 200 o 409 aleatoriamente
        """
        logger.info("Procesando pago... Conectando con pasarela...")
        time.sleep(random.uniform(1, 3))

        if random.random() < 0.2:
            logger.warning("Pago rechazado por la pasarela de pagos.")
            return {"status": "error", "code": 409, "data": None}

        try:
            new_pago = self.repository.save(pago)
            self.cache.set(f'pagos_{new_pago.id}', new_pago)
            self.cache.delete('pagos')
            logger.info(f"Pago {new_pago.id} procesado exitosamente.")
            return {"status": "success", "code": 200, "data": new_pago}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al agregar el pago: {e}")
            return {"status": "error", "code": 500, "data": None}

    def compensar_pago(self, pago_id: int) -> bool:
        """
        Endpoint 2: Realiza la compensación (reembolso) de un pago
        Siempre retorna éxito (200)
        """
        logger.info(f"Iniciando compensación para el pago {pago_id}...")
        
        try:
            pago = self.repository.get_by_id(pago_id)
            if not pago:
                logger.warning(f"Pago {pago_id} no encontrado para compensación.")
                return False

            time.sleep(random.uniform(0.5, 1.5))

            self.repository.delete(pago_id)
            self.cache.delete(f'pagos_{pago_id}')
            self.cache.delete('pagos')
            
            logger.info(f"Compensación del pago {pago_id} realizada exitosamente.")
            return True
            
        except Exception as e:
            logger.error(f"Error al compensar el pago {pago_id}: {e}")
            db.session.rollback()
            return False

    def find(self, pago_id: int) -> Pagos:
        cached_pago = self.cache.get(f'pagos_{pago_id}')
        if cached_pago is None:
            pago = self.repository.get_by_id(pago_id)
            if pago:
                self.cache.set(f'pagos_{pago_id}', pago)
            return pago
        return cached_pago
        
    def update(self, pago_id: int, new_data: Pagos) -> Pagos:
        try:
            pago = self.repository.get_by_id(pago_id)
            if not pago:
                return None
    
            for key, value in new_data.__dict__.items():
                if value is not None:
                    setattr(pago, key, value)
    
            updated_pago = self.repository.save(pago)
            self.cache.set(f'pagos_{pago.id}', updated_pago)
            self.cache.delete('pagos')
            return updated_pago
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar el pago con ID {pago_id}: {e}")
            raise
