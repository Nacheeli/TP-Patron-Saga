import logging
import requests
from flask import current_app
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)
from app.services.stock_service import StockService 

logger = logging.getLogger(__name__)

@retry(
    retry=retry_if_exception_type(requests.RequestException),
    wait=wait_fixed(2),  
    stop=stop_after_attempt(3), 
    reraise=True,
    before_sleep=before_sleep_log(logger, logging.INFO)  
)
def hacer_peticion(url, data):
    try:
        logger.info(f"Enviando petición a {url} con datos: {data}")
        response = requests.post(url, json=data)
        response.raise_for_status()  
        return response
    except requests.RequestException as e:
        logger.error(f"Error en la petición a {url}: {e}")
        raise

class Action:
    def __init__(self, execute_fn, compensate_fn):
        self.execute_fn = execute_fn
        self.compensate_fn = compensate_fn
        self.url = None

    def execute(self, data):
        url, response_data = self.execute_fn(data)
        self.url = url
        return url, response_data

    def compensate(self, id):
        return self.compensate_fn(id)

class Saga:
    def __init__(self, actions, data):
        self.actions = actions
        self.data = data
        self.IDs = []
        self.response = {"message": "OK", "status_code": 201, "data": {"message": "Operación realizada con éxito"}}

    def execute(self):
        saga_data = self.data.copy()

        try:
            stock_data = saga_data.get("stock", {})
            prod_id = stock_data.get("producto_id")
            cantidad = stock_data.get("cantidad")

            if prod_id and cantidad:
                logger.info("Verificación PREVIA: Consultando disponibilidad en ms-inventario...")
                stock_srv = StockService()
                
                hay_stock = stock_srv.validar_stock(prod_id, cantidad)

                if not hay_stock:
                    logger.error("SAGA CANCELADA: No hay stock suficiente.")
                    return {
                        "status_code": 409, 
                        "message": "Stock insuficiente (Validación Previa)", 
                        "data": {"producto_id": prod_id}
                    }
            else:
                logger.warning("Datos de stock incompletos, saltando validación previa.")

        except Exception as e:
            logger.error(f"Error en validación previa de stock: {e}")
            return {"status_code": 500, "message": f"Error validando stock: {str(e)}", "data": None}

        for index, action in enumerate(self.actions):
            try:
                url, response_data = action.execute(saga_data)
        
                datos_relevantes = response_data.get("data", {}).copy()
                logger.info(f"Datos relevantes paso {index}: {datos_relevantes}")
                
                id_generado = datos_relevantes.get("id") or datos_relevantes.get("producto_id")
                self.IDs.append(id_generado)
                
            except Exception as e:
                logger.error(f"FALLO en paso {index}. Iniciando compensación. Error: {e}")
                self.response["status_code"] = 500
                self.response["message"] = "Error durante la ejecución de la saga"
                self.response["data"] = {"error": str(e)}
                self.compensate(index)
                break
        
        logger.info(f"Estado final de IDs: {self.IDs}")
        return self.response

    def compensate(self, index):
        try:
            for i in range(index - 1, -1, -1):  
                action = self.actions[i]
                if i < len(self.IDs) and self.IDs[i] is not None:
                    logger.info(f"Compensando paso {i} con ID {self.IDs[i]}...")
                    action.compensate(self.IDs[i])
                else:
                    logger.warning(f"No hay ID disponible para compensar en el índice {i}")

        except Exception as e:
            logger.exception(f"Error crítico durante la compensación: {e}")