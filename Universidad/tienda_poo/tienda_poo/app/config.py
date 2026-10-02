"""Configuración central de la aplicación."""
import os

from app.models.rol import Rol


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
    FAKE_STORE_URL = "https://fakestoreapi.com"
    HTTP_TIMEOUT = 10  # segundos

    # US01/US05: la API no maneja roles, por eso se asignan de forma LOCAL.
    # Clave = username de Fake Store API, valor = perfil dentro de la app.
    PERFILES_LOCALES = {
        "mor_2314": Rol.ADMINISTRADOR,
        "johnd": Rol.CLIENTE,
        "kevinryan": Rol.AUDITOR,
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
