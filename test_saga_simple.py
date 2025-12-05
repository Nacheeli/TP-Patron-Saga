import requests
import json

print("\n" + "="*60)
print("PRUEBA DE LA SAGA - SIMULACION DE COMPRA")
print("="*60)

# Datos de prueba
datos_saga = {
    "pago": {
        "precio": 500,
        "medio_pago": "tarjeta",
        "producto_id": 1
    },
    "compra": {
        "producto_id": 1,
        "fecha_compra": "2025-12-05",
        "direccion": "UTN San Rafael"
    },
    "stock": {
        "producto_id": 1,
        "cantidad": 2,
        "entrada_salida": 2
    }
}

print("\nDatos de la transaccion:")
print(json.dumps(datos_saga, indent=2))

# URL del orquestador (ajustar según tu configuración)
# Como no hay puerto expuesto, esto es solo para documentar
print("\n[INFO] Los servicios estan corriendo internamente en Docker")
print("[INFO] Para probar la saga, ejecuta test_compra.py desde dentro del contenedor")
print("\nComandos para probar manualmente:")
print("  docker exec -it orquestador_service python -c \"from app import create_app; app = create_app(); print(app.config)\"")
print("\n" + "="*60)
