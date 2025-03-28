from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  MetaData
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config
from flask_ckeditor import CKEditor

# Initialize the Database
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })



db = SQLAlchemy(model_class=Base)

login_manager = LoginManager()

bootstrap = Bootstrap5()

ckeditor = CKEditor()


def create_app():
    # Create a flask instance
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Initialize the bootstrap
    bootstrap.init_app(app)

    # Create LoginManager
    login_manager.init_app(app)
    login_manager.login_view = "login"

    ckeditor.init_app(app)

    #Import routes and models
    from app.routes import register_routes
    from app import models

    register_routes(app=app, login_manager=login_manager)


    migrate = Migrate()
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    return app