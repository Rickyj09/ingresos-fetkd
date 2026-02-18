import os
from dotenv import load_dotenv

# Carga variables del .env desde la raíz del proyecto
load_dotenv()

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:1234@127.0.0.1:3306/ingresos_fetkd?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False