from requests import Response
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

class ServiceError(Exception): pass
class ValidationError(ServiceError): pass
class NotFoundError(ServiceError): pass
class ConflictError(ServiceError): pass
class ServerError(ServiceError): pass

def validar_respuesta(response: Response, codigo_esperado: int = 200):
   
    if response.status_code == codigo_esperado:
        return

    
    code = response.status_code
    
    if code == 404:
        msg = "Recurso no encontrado."
        logger.error(f"Error {code}: {msg}")
        raise NotFoundError(msg)

    elif code == 409:
        msg = "Conflicto: El recurso ya existe."
        logger.error(f"Error {code}: {msg}")
        raise ConflictError(msg)

    elif code == 422:
        try:
            detalle = response.json().get('errors', 'Sin detalles')
        except Exception:
            detalle = response.text 
            
        msg = f"Datos inválidos: {detalle}"
        logger.error(f"Error {code}: {msg}")
        raise ValidationError(msg)

    elif code >= 500:
        msg = "Error interno del servidor remoto."
        logger.error(f"Error {code}: {msg}")
        raise ServerError(msg)

   
    msg_fallback = f"Error inesperado: {code} - {response.text}"
    logger.error(msg_fallback)
    raise ServiceError(msg_fallback)