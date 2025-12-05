-- Script para insertar datos de prueba en la base de datos

-- Insertar productos de prueba
INSERT INTO producto (id, nombre, precio, activado) VALUES 
(1, 'Laptop Dell XPS 13', 1200.00, true),
(2, 'Mouse Logitech MX Master', 99.99, true),
(3, 'Teclado Mecanico RGB', 150.00, true),
(4, 'Monitor LG 27 pulgadas', 350.00, true),
(5, 'Webcam HD 1080p', 75.00, true)
ON CONFLICT (id) DO NOTHING;

-- Insertar stock inicial
INSERT INTO stock (producto_id, fecha_transaccion, cantidad, entrada_salida) VALUES 
(1, CURRENT_TIMESTAMP, 50, 1),
(2, CURRENT_TIMESTAMP, 100, 1),
(3, CURRENT_TIMESTAMP, 75, 1),
(4, CURRENT_TIMESTAMP, 30, 1),
(5, CURRENT_TIMESTAMP, 60, 1)
ON CONFLICT DO NOTHING;

-- Verificar los datos insertados
SELECT 'Productos insertados:' as mensaje;
SELECT * FROM producto;

SELECT 'Stock insertado:' as mensaje;
SELECT * FROM stock;
