import logging
import sys
from app import create_app
from app.services.saga_orchestrator import Saga, Action
from app.services.pago_service import PagoService
from app.services.compra_service import CompraService
from app.services.stock_service import StockService

# Configurar logs para ver qué pasa en la consola
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("TestSaga")

app = create_app()

# --- DEFINICIÓN DE ACCIONES ---
def agregar_pago_action(data):
    print("   [1/3] 💳 Cobrando al usuario...")
    service = PagoService()
    return service.agregar_pago(data)

def compensar_pago_action(id):
    print(f"   [⏪] Anulando Pago ID {id}...")
    service = PagoService()
    return service.eliminar_pago(id)

def crear_compra_action(data):
    print("   [2/3] 🧾 Creando factura de compra...")
    service = CompraService()
    return service.comprar(data)

def compensar_compra_action(id):
    print(f"   [⏪] Borrando Factura ID {id}...")
    service = CompraService()
    return service.borrar_compra(id)

def agregar_stock_action(data):
    print("   [3/3] 📦 Reservando stock en depósito...")
    service = StockService()
    return service.agregar_stock(data)

def compensar_stock_action(id):
    print(f"   [⏪] Devolviendo Stock ID {id}...")
    service = StockService()
    return service.borrar_stock(id)

# --- ARMADO DE LA SAGA ---
acciones = [
    Action(agregar_pago_action, compensar_pago_action),
    Action(crear_compra_action, compensar_compra_action),
    Action(agregar_stock_action, compensar_stock_action)
]

# Datos de prueba (Cliente compra 5 unidades del Producto 1)
datos_saga = {
    "pago": {"precio": 500, "medio_pago": "tarjeta de credito", "producto_id": 1},
    "compra": {"producto_id": 1, "fecha_compra": "2025-12-04T10:30:00", "direccion_envio": "UTN San Rafael, Mendoza"},
    "stock": {"producto_id": 1, "cantidad": 5, "entrada_salida": 2, "fecha_transaccion": "2025-12-05T19:30:00"}
}

# --- EJECUCIÓN ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 INICIANDO PRUEBA DE SAGA DE COMERCIO ELECTRÓNICO")
    print("="*50)
    
    saga = Saga(acciones, datos_saga)
    
    with app.app_context():
        resultado = saga.execute()
    
    print("\n" + "="*50)
    print("📊 RESULTADO FINAL:")
    print(f"Estado: {resultado.get('status_code')}")
    print(f"Mensaje: {resultado.get('message')}")
    print("="*50 + "\n")