import os
import requests
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

class HttpClient:
    
    DEFAULT_TIMEOUT = 10

    @staticmethod
    def _verify_ssl():
       
        return os.getenv("FLASK_ENV", "development").lower() == "production"

    @classmethod
    def _request(cls, method, url, **kwargs):
       
        logger.debug(f"Petición {method} a: {url}")
        
        
        return requests.request(
            method=method,
            url=url,
            verify=cls._verify_ssl(),
            timeout=cls.DEFAULT_TIMEOUT,
            **kwargs
        )

    @classmethod
    def get(cls, url, headers=None):
        return cls._request("GET", url, headers=headers)

    @classmethod
    def post(cls, url, json=None, headers=None):
        return cls._request("POST", url, json=json, headers=headers)

    @classmethod
    def put(cls, url, json=None, headers=None):
        return cls._request("PUT", url, json=json, headers=headers)

    @classmethod
    def delete(cls, url, headers=None):
        return cls._request("DELETE", url, headers=headers)