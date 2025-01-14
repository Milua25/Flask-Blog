import os

class Config():
    SECRET_KEY = os.getenv("SECRET_KEY")
    # configure the SQLite database, relative to the app instance folder
    SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"