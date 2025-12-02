import logging
from app.services.saga.acciones import SagaAction
logger = logging.getLogger(__name__)

class SagaOrchestrator:
    _INDICES = {
        0: "pago",
        1: "compra",
        2: "stock",
    }

    def __init__(self, acciones, datos):
        self.acciones = acciones
        self.datos = datos.copy()
        self.ids_generados = []  
        self.respuesta = {
            "mensaje": "OK",
            "codigo_estado": 201,
            "datos": {"mensaje": "Operación realizada con éxito"},
        }

    def ejecutar(self):
        saga_datos = self.datos.copy()

        for indice, accion in enumerate(self.acciones):
            try:
                logger.info(f"Ejecutando acción {indice + 1}/{len(self.acciones)}")
                
               
                url, response_data = accion.ejecutar(saga_datos)
                
                
                datos_relevantes = response_data.get("data", {})
                id_generado = datos_relevantes.get("id")
                
                logger.info(f"Acción exitosa. ID generado: {id_generado}")
                self.ids_generados.append(id_generado)

            except Exception as e:
                logger.error(f"Fallo en el paso {indice + 1}: {e}")
                self._manejar_error(e, indice)
                break  
        
        return self.respuesta

    def _manejar_error(self, error, indice_fallido):
        self.respuesta["codigo_estado"] = 500
        self.respuesta["mensaje"] = "Error durante la ejecución de la saga"
        self.respuesta["datos"] = {"error": str(error)}
        
    
        self.ids_generados.append(None)
        
    
        self.compensar(indice_fallido)

    def compensar(self, indice_fallido):
       
        logger.info("Iniciando compensación (Rollback)...")
        
        
        for i in range(indice_fallido - 1, -1, -1):
            id_a_compensar = self.ids_generados[i]
            
            if id_a_compensar:
                logger.info(f"Compensando paso {i + 1} (ID: {id_a_compensar})")
                try:
                    self.acciones[i].compensar(id_a_compensar)
                except Exception as e:
                    logger.critical(f"Error crítico al compensar paso {i + 1}: {e}")