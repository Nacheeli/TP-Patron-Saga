TP Patron Saga - Desarrollo de Software

DESCRIPCION DEL PROYECTO

Este es un sistema de comercio electronico implementado con el patron Saga para manejar transacciones distribuidas. El sistema tiene 4 microservicios principales (Catalogo, Compras, Inventario y Pagos) coordinados por un Orquestador que ejecuta la saga.

ARQUITECTURA

- ms-orquestador: Implementa el patron Saga para coordinar las transacciones
- ms-catalogo: Maneja el catalogo de productos (Puerto 5003)
- ms-compras: Gestiona las ordenes de compra (Puerto 5000)
- ms-inventario: Controla el stock de productos (Puerto 5001)
- ms-pagos: Procesa los pagos (Puerto 5002)
- PostgreSQL: Base de datos compartida
- Redis: Sistema de cache y almacenamiento para Rate Limiting
- Traefik: API Gateway y balanceador de carga

PATRONES IMPLEMENTADOS

- Patron Saga Orquestado: Coordinacion de transacciones distribuidas con compensacion automatica
- Rate Limiting: Control de trafico con Flask-Limiter (100 peticiones por minuto)
- Retry con Tenacity: Reintentos automaticos en llamadas entre servicios
- Cache con Redis: Mejora de performance en consultas frecuentes
- Circuit Breaker: No implementado (opcional segun el trabajo practico)

COMO LEVANTAR EL PROYECTO

Prerequisitos:
- Docker y Docker Compose instalados
- Puerto 5000, 5001, 5002, 5003, 5005, 5432, 6379 y 80/443 disponibles

Paso 1: Crear la red de Docker
docker network create red1

Paso 2: Levantar servicios de infraestructura
cd ms_servicios
docker-compose -f docker-compose.redis.yml up -d
docker-compose -f docker-compose.traefik.yml up -d
cd ..

Paso 3: Levantar base de datos
docker-compose -f docker-compose.postgres.yml up -d

Paso 4: Levantar microservicios (en este orden)
cd G15_ms-catalogo
docker-compose -f docker-compose-producto.yml up -d
cd ..

cd G15_ms-inventario
docker-compose -f docker-compose.stock.yml up -d
cd ..

cd G15_ms-pagos
docker-compose -f docker-compose.pagos.yml up -d
cd ..

cd G15_ms-compras
docker-compose -f docker-compose.compra.yml up -d
cd ..

Paso 5: Levantar el orquestador
cd G15-ms-base
docker-compose -f docker-compose.yml up -d
cd ..

VERIFICAR QUE TODO ESTE FUNCIONANDO

Verificar servicios individuales:
- Catalogo: http://localhost:5003/ping
- Compras: http://localhost:5000/ping
- Inventario: http://localhost:5001/ping
- Pagos: http://localhost:5002/ping
- Orquestador: http://localhost:5005/ping

Verificar logs:
docker logs ms-orquestador
docker logs producto_service
docker logs stock_service
docker logs pagos_service
docker logs ms-compras

EJECUTAR UNA PRUEBA DE LA SAGA

Opcion 1: Usar el script de prueba incluido
cd G15-ms-base
python test_compra.py

Opcion 2: Ver todos los contenedores
docker ps

DETENER EL PROYECTO

Para detener todos los servicios:
docker-compose -f G15-ms-base/docker-compose.yml down
docker-compose -f G15_ms-compras/docker-compose.compra.yml down
docker-compose -f G15_ms-pagos/docker-compose.pagos.yml down
docker-compose -f G15_ms-inventario/docker-compose.stock.yml down
docker-compose -f G15_ms-catalogo/docker-compose-producto.yml down
docker-compose -f docker-compose.postgres.yml down
docker-compose -f ms_servicios/docker-compose.redis.yml down
docker-compose -f ms_servicios/docker-compose.traefik.yml down

ESTRUCTURA DE LA SAGA

La saga ejecuta 3 pasos en orden:
1. Agregar Pago: Se cobra al cliente
2. Crear Compra: Se genera la factura
3. Agregar Stock: Se reserva el inventario

Si alguno falla, se ejecutan las compensaciones en orden inverso:
1. Si falla Stock: Se borra la compra y se anula el pago
2. Si falla Compra: Se anula el pago
3. Si falla Pago: No hay compensacion

Ademas, antes de iniciar la saga, se valida que haya stock suficiente. Si no hay, la saga ni siquiera inicia.

CONFIGURACION

Todas las variables de entorno estan en el archivo .env en la raiz del proyecto:
- POSTGRES_USER=admin_ecomerce
- POSTGRES_PASSWORD=1234
- POSTGRES_DB=ecommercedb
- POSTGRES_PORT=5432
- FLASK_ENV=development
- REDIS_HOST=redis_service
- REDIS_PORT=6379
- REDIS_PASSWORD= (vacio por defecto)

REPOSITORIOS ORIGINALES

Al principio del proyecto trabajamos los diferentes microservicios en diferentes repositorios, por eso algunos commits no figuran en el historial. Enlaces:

- Orquestador: https://github.com/GiulianaBettiol/ms-base
- Pagos: https://github.com/AlejandroRA10/G15_ms-pagos
- Inventario: https://github.com/Nacheeli/G15_ms-inventario
- Servicios: https://github.com/FrancoV20/ms_servicios
- Catalogo: https://github.com/CandelaVulcano/G15_ms-catalogo
- Compras: https://github.com/JimenaMarol/G15_ms-compras

ENDPOINTS DISPONIBLES

Catalogo (Puerto 5003):
- GET /api/v1/producto - Listar productos
- GET /api/v1/producto/{id} - Obtener producto
- POST /api/v1/producto - Crear producto
- PUT /api/v1/producto/{id} - Actualizar producto

Inventario (Puerto 5001):
- GET /api/v1/stock - Listar stock
- GET /api/v1/stock/{producto_id} - Obtener stock de un producto
- POST /api/v1/stock - Agregar stock
- DELETE /api/v1/stock/{id} - Eliminar stock

Pagos (Puerto 5002):
- GET /api/v1/pagos - Listar pagos
- GET /api/v1/pagos/{id} - Obtener pago
- POST /api/v1/pagos - Crear pago
- DELETE /api/v1/pagos/{id} - Eliminar pago

Compras (Puerto 5000):
- GET /api/v1/compra - Listar compras
- GET /api/v1/compra/{id} - Obtener compra
- POST /api/v1/compra - Crear compra
- DELETE /api/v1/compra/{id} - Eliminar compra
