import requests

from app.services.excepciones import ErrorDeConexion


class FakeStoreClient:
    """Capa HTTP única hacia Fake Store API (se puede sustituir en pruebas)."""

    def __init__(self, base_url: str, timeout: float = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http = requests.Session()
        self._http.headers.update(
            {"User-Agent": "Mozilla/5.0 (TiendaPOO)", "Accept": "application/json"}
        )

    def solicitar(self, metodo: str, ruta: str, **kwargs) -> requests.Response:
        try:
            return self._http.request(
                metodo, f"{self._base_url}{ruta}", timeout=self._timeout, **kwargs
            )
        except requests.RequestException as exc:
            raise ErrorDeConexion("No fue posible conectar con el servidor.") from exc
