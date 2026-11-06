from app.models.usuario import Usuario
from app.services.excepciones import ErrorDeConexion
from app.services.fake_store_client import FakeStoreClient


class ServicioUsuarios:
    """US11: consumo de solo lectura de GET /users."""

    def __init__(self, cliente: FakeStoreClient) -> None:
        self._cliente = cliente

    def listar(self) -> list[Usuario]:
        resp = self._cliente.solicitar("GET", "/users")
        if not resp.ok:
            raise ErrorDeConexion(f"El servidor respondió {resp.status_code}.")
        try:
            datos = resp.json()
        except ValueError as exc:
            raise ErrorDeConexion("Respuesta inesperada del servidor.") from exc
        if not isinstance(datos, list):
            raise ErrorDeConexion("Respuesta inesperada del servidor.")
        return [Usuario.desde_dict(d) for d in datos if isinstance(d, dict)]
