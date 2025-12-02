

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
        raise RuntimeError(f"Error cargando configuración para {env}: {e}")
    
   
    try:
        db.init_app(app)
        cache.init_app(app, config=cache_config)
        logger.info("Extensiones inicializadas correctamente")
    except Exception as e:
        logger.error(f"Error inicializando extensiones: {e}")
        raise RuntimeError(f"Error inicializando extensiones: {e}")
    
    # Ruta de salud
    @app.route('/ping', methods=['GET'])
    def ping():
        """Endpoint de salud del servicio."""
        return {"mensaje": "El servicio de Base está en funcionamiento"}
    
    return app


__all__ = ["create_app", "db", "cache"]


