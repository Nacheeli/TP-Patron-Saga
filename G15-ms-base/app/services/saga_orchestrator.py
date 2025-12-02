
import logging
import requests
from flask import Flask
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      stop_after_attempt, wait_fixed)

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

        for index, action in enumerate(self.actions):
            try:
                url, response_data = action.execute(saga_data)
        
                datos_relevantes = response_data.get("data", {}).copy()
                logger.info(f"Datos relevantes: {datos_relevantes}")
                id_generado = datos_relevantes.pop("id", None)
                logger.info(f"ID generado: {id_generado}")
                self.IDs.append(id_generado)
        
                
                if index == 0:  
                    datos_a_enviar = saga_data["pago"]
                elif index == 1:  
                    datos_a_enviar = saga_data["compra"]
                elif index == 2:  
                    datos_a_enviar = saga_data["stock"]
        
                with app.test_request_context():
                    response = hacer_peticion(url, datos_a_enviar)
        
                if response.status_code == 201:
                    logger.info(f"ID generado: {id_generado}")
                else:
                    self.response["status_code"] = response.status_code
                    self.response["message"] = response.json().get('message')
                    self.response["data"] = response.json().get('data')
                    self.compensate(index)
                    break
                
            except Exception as e:
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
                    url_compensacion = f"{action.url}/{self.IDs[i]}"
                    response = requests.delete(url_compensacion)
                    logger.info(f"Compensación realizada en {url_compensacion}: {response.status_code}")
                else:
                    logger.warning(f"No hay ID disponible para compensar en el índice {i}")

        except Exception as e:
            logger.exception(f"Error en la compensación: {e}")

if __name__ == "__main__":
    app.run(debug=True)