from typing import Tuple
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from db import DatabaseConfig, db
from routes import register_routes
from models import *

def init_app() -> Tuple[Flask, SQLAlchemy, Migrate]: 
    app = Flask(__name__)
    app.secret_key = "secret_123"
    
    db_config = DatabaseConfig()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{db_config.user}@{db_config.host}/{db_config.database}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "static/img"

    db.init_app(app) 
    migrate = Migrate(app, db)
    register_routes(app)

    return app, db, migrate

app, db, migrate = init_app()


if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=3000, debug=True)