# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # redirect unauthorized users

def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )

    # local static path for uploads
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # aws s3 settings (for prod)
    app.config["USE_S3"] = os.getenv("USE_S3", "false").lower() == "true"
    app.config["S3_BUCKET_NAME"] = os.getenv("S3_BUCKET_NAME")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    #blueprints
    from .routes.main import main
    from .routes.auth import auth
    from .routes.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    return app
