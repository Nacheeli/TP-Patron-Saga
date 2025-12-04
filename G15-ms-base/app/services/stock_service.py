from typing import Dict, Any, Tuple
from flask import current_app
from app.utils.logger_config import setup_logger
from app.utils.http_client import HttpClient
from app.utils.response_validator import validar_respuesta

logger = setup_logger(__name__)

class StockService:
   
    def agregar_stock(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        data_stock = data.get('stock')
        url = current_app.config['STOCK_URL']
        logger.info(f"Agregando stock: {data_stock}")
        response = HttpClient.post(url, data_stock)
        validar_respuesta(response, codigo_esperado=201)
        return url, response.json()

    def borrar_stock(self, id_stock: str) -> bool:
        logger.info(f"Borrando stock ID: {id_stock}")
        url = f"{current_app.config['STOCK_URL']}/{id_stock}"
        response = HttpClient.delete(url)
        if response.status_code == 404:
            logger.warning(f"Stock con ID {id_stock} no encontrado.")
            return False
        validar_respuesta(response, codigo_esperado=204)
        logger.info(f"Stock con ID {id_stock} borrado exitosamente.")
        return True

    def validar_stock(self, producto_id: int, cantidad_necesaria: int) -> bool:
        """Consulta al ms-inventario si hay suficiente stock"""
        logger.info(f"Validando stock para producto {producto_id}, cantidad: {cantidad_necesaria}")
        url = f"{current_app.config['STOCK_URL']}/{producto_id}"
        
        response = HttpClient.get(url)
        
        if response.status_code == 404:
            logger.warning(f"Producto {producto_id} no existe en inventario.")
            return False
            
        if response.status_code == 200:
            data = response.json()
            stock_actual = data.get('cantidad', 0) 
            
            if stock_actual >= cantidad_necesaria:
                logger.info("Stock suficiente.")
                return True
            else:
                logger.warning(f"Stock insuficiente. Hay {stock_actual}, se piden {cantidad_necesaria}")
                return False
        
        return False