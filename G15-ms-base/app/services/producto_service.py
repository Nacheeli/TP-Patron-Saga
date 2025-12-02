from typing import Dict, Any, Optional
from flask import current_app

from app.utils.logger_config import setup_logger
from app.utils.http_client import HttpClient
from app.utils.response_validator import validar_respuesta


logger = setup_logger(__name__)


class ProductoService:
    
    
    def obtener_producto(self, producto_id: str) -> Optional[Dict[str, Any]]:
        
        logger.info(f"Obteniendo producto: {producto_id}")
        url = f"{current_app.config['PRODUCTO_URL']}/{producto_id}"
        response = HttpClient.get(url)

        if response.status_code == 404:
            logger.warning(f"Producto con ID {producto_id} no encontrado.")
            return None

        validar_respuesta(response, expected_code=200)
        return response.json()

    def validar_disponibilidad(self, producto_id: str, cantidad: int) -> bool:
        
        logger.info(f"Validando disponibilidad de producto {producto_id} para {cantidad} unidades.")
        url = f"{current_app.config['PRODUCTO_URL']}/{producto_id}"
        response = HttpClient.get(url)

        if response.status_code == 404:
            logger.warning(f"Producto con ID {producto_id} no encontrado.")
            return False

        validar_respuesta(response, expected_code=200)
        
        producto = response.json()
        stock_disponible = producto.get("stock", 0)
        
        if stock_disponible >= cantidad:
            logger.info(f"Producto {producto_id} tiene stock suficiente ({stock_disponible} disponibles).")
            return True
        
        logger.warning(f"Producto {producto_id} no tiene stock suficiente ({stock_disponible} disponibles).")
        return False
