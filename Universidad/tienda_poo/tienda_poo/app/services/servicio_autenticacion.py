from app.models.rol import Rol
from app.models.sesion_usuario import SesionUsuario
from app.services.excepciones import (
    CredencialesInvalidas,
    ErrorDeConexion,
    PerfilNoAsignado,
)
from app.services.fake_store_client import FakeStoreClient


class ServicioAutenticacion:
    """US01: login contra /auth/login y asignación LOCAL del perfil."""

    def __init__(self, cliente: FakeStoreClient, perfiles: dict[str, Rol]) -> None:
        self._cliente = cliente
        self._perfiles = dict(perfiles)

    def iniciar_sesion(self, username: str, password: str) -> SesionUsuario:
        username = username.strip()
        resp = self._cliente.solicitar(
            "POST", "/auth/login", json={"username": username, "password": password}
        )
        if resp.status_code in (400, 401):
            raise CredencialesInvalidas("Usuario o contraseña incorrectos.")
        if not resp.ok:
            raise ErrorDeConexion(f"El servidor respondió {resp.status_code}.")
        try:
            token = resp.json()["token"]
        except (ValueError, KeyError, TypeError) as exc:
            raise ErrorDeConexion("Respuesta inesperada del servidor.") from exc

        rol = self._perfiles.get(username)
        if rol is None:
            raise PerfilNoAsignado("El usuario no tiene un perfil asignado.")
        return SesionUsuario(username=username, token=token, rol=rol)
