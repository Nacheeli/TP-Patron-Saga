
# saga_example.py
import logging
from app.services.saga_orchestrator import Saga, Action
from app.services import PagoService, CompraService, StockService
from app import create_app


app = create_app()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def agregar_pago_action(data):
    try:
        logger.info("Iniciando acción de agregar pago.")
        pago_service = PagoService()
        result = pago_service.agregar_pago(data)
        logger.info(f"devolviendo: {result[0]}, {result[1]}")
        return result[0], result[1]  
    except Exception as e:
        logger.error(f"Error en agregar pago: {e}")
        raise

def crear_compra_action(data):
    try:
        logger.info("Iniciando acción de crear compra.")
        compra_service = CompraService()
        result = compra_service.comprar(data)
        logger.info(f"devolviendo {result[0]}, {result[1]}")
        return result[0], result[1]  

    except Exception as e:
        logger.error(f"Error en crear compra: {e}")
        raise


def agregar_stock_action(data):
    try:
        logger.info("Iniciando acción de agregar stock.")
        stock_service = StockService()
        result = stock_service.agregar_stock(data)
        return result[0], result[1]  
    except Exception as e:
        logger.error(f"Error en agregar stock: {e}")
        raise

def compensar_pago_action(id_pago):
    try:
        logger.info(f"Iniciando compensación de pago con id: {id_pago}")
        pago_service = PagoService()
        return pago_service.borrar_pago(id_pago)
    except Exception as e:
        logger.error(f"Error en compensación de pago: {e}")
        raise

def compensar_compra_action(id_compra):
    try:
        logger.info(f"Iniciando compensación de compra con id: {id_compra}")
        compra_service = CompraService()
        return compra_service.borrar_compra(id_compra)
    except Exception as e:
        logger.error(f"Error en compensación de compra: {e}")
        raise

def compensar_stock_action(id_stock):
    try:
        logger.info(f"Iniciando compensación de stock con id: {id_stock}")
        stock_service = StockService()
        return stock_service.borrar_stock(id_stock)
    except Exception as e:
        logger.error(f"Error en compensación de stock: {e}")
        raise

acciones = [
    Action(agregar_pago_action, compensar_pago_action),
    Action(crear_compra_action, compensar_compra_action),
    Action(agregar_stock_action, compensar_stock_action)
]

datos_saga = {
    "pago": {"precio": 100, "medio_pago": "tarjeta de credito", "producto_id": 1},
    "compra": {"producto_id": 1, "fecha_compra": "2025-01-23T10:00:00", "direccion_envio": "Calle 123"},
    "stock": {"producto_id": 1, "cantidad": 10, "entrada_salida": 1, "fecha_transaccion": "2025-01-23T10:00:00"}
}

saga = Saga(acciones, datos_saga)

with app.app_context():
    response = saga.execute()


logger.info(f"Respuesta final de la saga: {response}")
