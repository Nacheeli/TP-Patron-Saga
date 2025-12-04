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
        logger.info("--> PARCHE EXITOSO: Conectando a Base de Datos usando variable de Docker.")
    try:
        db.init_app(app)
        cache.init_app(app, config=cache_config)
        logger.info("Extensiones inicializadas correctamente")
    except Exception as e:
        logger.error(f"Error inicializando extensiones: {e}")
        raise RuntimeError(f"Error inicializando extensiones: {e}")
    
    @app.route('/ping', methods=['GET'])
    def ping():
        """Endpoint de salud del servicio."""
        return {"mensaje": "El servicio de Base está en funcionamiento"}
    
    return app

__all__ = ["create_app", "db", "cache"]
