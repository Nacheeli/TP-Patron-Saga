import os
from app import create_app, db

app = create_app()
app.app_context().push()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        from gunicorn.app.base import BaseApplication

        class GunicornApp(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                config = {key: value for key, value in self.options.items(
                ) if key in self.cfg.settings and value is not None}
                for key, value in config.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            "bind": "0.0.0.0:5003",
            "workers": 3,  # Número de workers para manejar carga
        }
        GunicornApp(app, options).run()
    else:
        app.run(host="0.0.0.0", port=5003, debug=True)
