
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

        validar_respuesta(response, expected_code=201)
        return url, response.json()

    def borrar_stock(self, id_stock: str) -> bool:
        
        logger.info(f"Borrando stock  ID: {id_stock}")
        url = f"{current_app.config['STOCK_URL']}/{id_stock}"
        response = HttpClient.delete(url)

        if response.status_code == 404:
            logger.warning(f"Stock con ID {id_stock} no encontrado.")
            return False

        validar_respuesta(response, expected_code=204)
        logger.info(f"Stock con ID {id_stock} borrado exitosamente.")
        return True
