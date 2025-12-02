import os
import unittest

from app import create_app, db
from app.models import Stock


class StockTestCase(unittest.TestCase):
    
    def setUp(self):
        # User
        self.IDPRODUCTO_PRUEBA = 1
        self.FECHA_COMPRA_PRUEBA = '2020-01-01:00:00:00'
        self.DIRECCION_ENVIO_PRUEBA = "Calle falsa 123"
    
        os.environ['FLASK_CONTEXT'] = 'testing'
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    def test_stock(self):
        stock = self.__get_stock()

        self.assertEqual(stock.producto_id, self.IDPRODUCTO_PRUEBA)
        self.assertEqual(stock.direccion_envio, self.DIRECCION_ENVIO_PRUEBA)
        self.assertEqual(stock.fecha_stock, self.FECHA_COMPRA_PRUEBA)

    def __get_stock(self):
        stock = Stock()
        stock.producto_id = self.IDPRODUCTO_PRUEBA
        stock.fecha_stock = self.FECHA_COMPRA_PRUEBA
        stock.direccion_envio = self.DIRECCION_ENVIO_PRUEBA

        return stock
    
if __name__ == '__main__':
    unittest.main()