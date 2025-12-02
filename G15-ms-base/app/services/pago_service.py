
from typing import Dict, Any, Tuple
from flask import current_app
from app.utils.logger_config import setup_logger
from app.utils.http_client import HttpClient
from app.utils.response_validator import validar_respuesta

logger = setup_logger(__name__)

class PagoService:
   

    def agregar_pago(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
       
        data_pago = data.get('pago')
        url = current_app.config['PAGOS_URL']

        logger.info(f"Crear pago: {data_pago}")
        response = HttpClient.post(url, data_pago)

        validar_respuesta(response, expected_code=201)
        return url, response.json()

    def eliminar_pago(self, id_pago: str) -> bool:
       
        logger.info(f"Borrando pago con ID: {id_pago}")
        url = f"{current_app.config['PAGOS_URL']}/{id_pago}"
        response = HttpClient.delete(url)

        if response.status_code == 404:
            logger.warning(f"Pago con ID {id_pago} no encontrado.")
            return False

        validar_respuesta(response, expected_code=204)
        logger.info(f"Pago con ID {id_pago} borrado exitosamente.")
        return True
