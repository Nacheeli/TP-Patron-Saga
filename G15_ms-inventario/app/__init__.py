import os
from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import cache_config, factory
import redis
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
cache = Cache()

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', '')
redis_db = int(os.getenv('REDIS_DB', 0))

redis_uri = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

redis_client = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    password=redis_password,
    decode_responses=True
)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri=redis_uri
)

try:
    redis_client.ping()
    logger.info("Conexión a Redis exitosa.")
except redis.ConnectionError as e:
    logger.error(f"Error al conectar con Redis: {e}")

def create_app():
    app = Flask(__name__)
    app_context = os.getenv('FLASK_ENV', 'development')
    
    try:
        app.config.from_object(factory(app_context))
    except Exception as e:
        logger.error(f"Error al cargar la configuración: {e}")

    uri_docker = os.getenv('SQLALCHEMY_DATABASE_URI')
    if uri_docker:
        app.config['SQLALCHEMY_DATABASE_URI'] = uri_docker
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        logger.info("--> PARCHE EXITOSO: Usando URI de base de datos desde Docker.")

    try:
        db.init_app(app)
        cache.init_app(app, config=cache_config)
        limiter.init_app(app)
    except Exception as e:
        raise RuntimeError(f"Error al inicializar extensiones: {e}")

    try:
        from app.routes import Stock
        app.register_blueprint(Stock, url_prefix='/api/v1')
    except Exception as e:
        raise RuntimeError(f"Error al registrar blueprints: {e}")

    @app.route('/ping', methods=['GET'])
    def ping():
        return {"message": "El servicio de stocks está en funcionamiento"}

    return app
