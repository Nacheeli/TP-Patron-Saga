import logging
import requests
from flask import Flask
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)
# Importamos el servicio actualizado
from app.services.stock_service import StockService 

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

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

        # --- FIX INICIO: Validación Previa de Stock ---
        # Antes de cobrar (Acción 0), verificamos si hay stock en Inventario
        try:
            # Extraemos datos seguros usando .get para evitar crashes
            stock_data = saga_data.get("stock", {})
            prod_id = stock_data.get("producto_id")
            cantidad = stock_data.get("cantidad")

            if prod_id and cantidad:
                logger.info("Verificación PREVIA: Consultando disponibilidad en ms-inventario...")
                stock_srv = StockService()
                
                # Necesitamos el contexto de la app para leer las URLs de config
                with app.test_request_context(): 
                     hay_stock = stock_srv.validar_stock(prod_id, cantidad)

                if not hay_stock:
                    logger.error("SAGA CANCELADA: No hay stock suficiente.")
                    return {
                        "status_code": 409, 
                        "message": "Stock insuficiente", 
                        "data": {"producto_id": prod_id}
                    }
            else:
                logger.warning("Datos de stock incompletos, saltando validación previa.")

        except Exception as e:
            logger.error(f"Error en validación previa de stock: {e}")
            # Opcional: Decidir si abortar o intentar seguir. 
            # Para seguridad, abortamos.
            return {"status_code": 500, "message": f"Error validando stock: {str(e)}", "data": None}
        # --- FIX FIN ---


        # Si pasó la validación, ejecutamos la SAGA normal
        for index, action in enumerate(self.actions):
            try:
                url, response_data = action.execute(saga_data)
        
                datos_relevantes = response_data.get("data", {}).copy()
                logger.info(f"Datos relevantes paso {index}: {datos_relevantes}")
                
                id_generado = datos_relevantes.pop("id", None)
                self.IDs.append(id_generado)
        
                # Lógica para enviar datos al siguiente paso (si fuera necesario)
                if index == 0:  
                    datos_a_enviar = saga_data.get("pago", {})
                elif index == 1:  
                    datos_a_enviar = saga_data.get("compra", {})
                elif index == 2:  
                    datos_a_enviar = saga_data.get("stock", {})
        
                # Simulamos verificación extra si se requiere
                # (Tu código original tenía un bloque 'hacer_peticion' aquí que parecía redundante
                #  o de prueba, lo mantengo simplificado para que siga el flujo de actions)
                
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
            # Recorre hacia atrás desde el paso que falló
            for i in range(index - 1, -1, -1):  
                action = self.actions[i]
                # Verificamos que tengamos un ID guardado para ese paso
                if i < len(self.IDs) and self.IDs[i] is not None:
                    # OJO: Aquí asumimos que compensate_fn recibe el ID
                    # Tu clase Action llama a self.compensate_fn(id)
                    logger.info(f"Compensando paso {i} con ID {self.IDs[i]}...")
                    action.compensate(self.IDs[i])
                else:
                    logger.warning(f"No hay ID disponible para compensar en el índice {i}")

        except Exception as e:
            logger.exception(f"Error crítico durante la compensación: {e}")

if __name__ == "__main__":
    app.run(debug=True)