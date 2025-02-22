import os
from decouple import config as ENV

DEBUG = True

SECRET_KEY = ENV("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
        SGBD = 'postgresql',
        usuario = ENV("USUARIO"),
        senha = ENV("SENHA"),
        servidor = 'localhost',
        database = ENV("DATABASE")
    )

SQLALCHEMY_TRACK_MODIFICATIONS = False

UPLOAD_PATH = os.path.dirname(os.path.abspath(__file__)) + '/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}