import os
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from app.config import cache_config, factory
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

db = SQLAlchemy()
cache = Cache()

def create_app() -> Flask:
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'development')
   
    try:
        config_cls = factory(env)
        app.config.from_object(config_cls)
        logger.info(f"Configuración cargada para ambiente: {env}")
    except Exception as e:
        logger.error(f"Error cargando configuración para {env}: {e}")
    
    uri_docker = os.getenv('SQLALCHEMY_DATABASE_URI')
    if uri_docker:
        app.config['SQLALCHEMY_DATABASE_URI'] = uri_docker
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        logger.info("--> PARCHE BD: Usando URI de Docker.")

    app.config['STOCK_URL'] = os.getenv('STOCK_URL')
    app.config['PAGOS_URL'] = os.getenv('PAGOS_URL')
    app.config['PRODUCTO_URL'] = os.getenv('PRODUCTO_URL')
    app.config['COMPRAS_URL'] = os.getenv('COMPRAS_URL')
    
    logger.info(f"--> PARCHE URLs: Stock={app.config['STOCK_URL']}")

    try:
        db.init_app(app)
        cache.init_app(app, config=cache_config)
        logger.info("Extensiones inicializadas correctamente")
    except Exception as e:
        logger.error(f"Error inicializando extensiones: {e}")
    
    @app.route('/ping', methods=['GET'])
    def ping():
        return {"mensaje": "El servicio de Base está en funcionamiento"}
    
    return app

__all__ = ["create_app", "db", "cache"]