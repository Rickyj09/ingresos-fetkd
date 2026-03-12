import os
from dotenv import load_dotenv

# Carga variables del .env desde la raíz del proyecto
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLite en PythonAnywhere (archivo dentro del proyecto)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "app.db")
    )