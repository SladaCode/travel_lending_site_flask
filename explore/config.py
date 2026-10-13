import os
from dotenv import load_dotenv
import re

load_dotenv()  #Подгружает файлы из .env

db_dir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(db_dir, "tours.db")  #Адрес БД
    SQLALCHEMY_TRACK_MODIFICATIONS = False  #Отключает лишние уведомления SQLAlchemy

class DevelopmentConfig(Config):
    DEBUG = True  #Режим отладки вкл
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me") 

class ProductionConfig(Config):
    DEBUG = False  #Режим отладки выкл
    SECRET_KEY = os.environ["SECRET_KEY"]
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY не задан!")