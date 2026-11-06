"""Fábrica de la aplicación (composición de objetos / inyección de dependencias)."""
from flask import Flask

from app.config import Config
from app.services.fake_store_client import FakeStoreClient
from app.services.servicio_autenticacion import ServicioAutenticacion
from app.services.servicio_carritos import ServicioCarritos
from app.services.servicio_compra import ServicioCompra
from app.services.servicio_productos import ServicioProductos
from app.services.servicio_usuarios import ServicioUsuarios
from app.web.auth_controller import AuthController
from app.web.carritos_controller import CarritosController
from app.web.catalogo_controller import CatalogoController
from app.web.compra_controller import CompraController
from app.web.usuarios_controller import UsuariosController
from app.web.seguridad import Seguridad


def create_app(cliente: FakeStoreClient | None = None, config: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    cliente = cliente or FakeStoreClient(
        app.config["FAKE_STORE_URL"], app.config["HTTP_TIMEOUT"]
    )
    servicio_auth = ServicioAutenticacion(cliente, app.config["PERFILES_LOCALES"])
    servicio_productos = ServicioProductos(cliente)
    servicio_usuarios = ServicioUsuarios(cliente)                      # US11
    servicio_carritos = ServicioCarritos(cliente, servicio_productos)  # US12
    servicio_compra = ServicioCompra(servicio_productos)               # carrito de compra

    Seguridad().registrar(app)
    app.register_blueprint(AuthController(servicio_auth).blueprint)
    app.register_blueprint(CatalogoController(servicio_productos).blueprint)
    app.register_blueprint(UsuariosController(servicio_usuarios).blueprint)
    app.register_blueprint(CarritosController(servicio_carritos).blueprint)
    app.register_blueprint(CompraController(servicio_compra).blueprint)
    return app
