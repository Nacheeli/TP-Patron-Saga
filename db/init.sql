-- Bases de datos para dev / prod / test
CREATE DATABASE dev_db;
CREATE DATABASE prod_db;
CREATE DATABASE test_db;

-- Otorgar privilegios al rol REAL que definimos en el .env
GRANT ALL PRIVILEGES ON DATABASE dev_db TO admin_ecomerce;
GRANT ALL PRIVILEGES ON DATABASE prod_db TO admin_ecomerce;
GRANT ALL PRIVILEGES ON DATABASE test_db TO admin_ecomerce;