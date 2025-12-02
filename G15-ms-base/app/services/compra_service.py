
from typing import Dict, Any, Tuple
from flask import current_app
from app.utils.logger_config import setup_logger
from app.utils.http_client import HttpClient
from app.utils.response_validator import validar_respuesta


logger = setup_logger(__name__)


class CompraService:
   

    def comprar(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        
        data_compra = data.get('compra')
        url = current_app.config['COMPRAS_URL']

        logger.info(f"Creando compra: {data_compra}")
        response = HttpClient.post(url, data_compra)

        validar_respuesta(response, expected_code=201)
        return url, response.json()

    def borrar_compra(self, id_compra: str) -> bool:
        
        logger.info(f"Borrando compra con ID: {id_compra}")
        url = f"{current_app.config['COMPRAS_URL']}/{id_compra}"
        response = HttpClient.delete(url)

        if response.status_code == 404:
            logger.warning(f"Compra con ID {id_compra} no encontrada.")
            return False

        validar_respuesta(response, expected_code=204)
        logger.info(f"Compra con ID {id_compra} borrada exitosamente.")
        return True