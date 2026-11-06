from app.models.carrito import Carrito
from app.services.excepciones import ErrorApi, ErrorDeConexion
from app.services.fake_store_client import FakeStoreClient
from app.services.servicio_productos import ServicioProductos


class ServicioCarritos:
    """US12: consumo de solo lectura de GET /carts, cruzado con GET /products."""

    def __init__(self, cliente: FakeStoreClient, productos: ServicioProductos) -> None:
        self._cliente = cliente
        self._productos = productos

    def listar(self) -> list[Carrito]:
        resp = self._cliente.solicitar("GET", "/carts")
        if not resp.ok:
            raise ErrorDeConexion(f"El servidor respondió {resp.status_code}.")
        try:
            datos = resp.json()
        except ValueError as exc:
            raise ErrorDeConexion("Respuesta inesperada del servidor.") from exc
        if not isinstance(datos, list):
            raise ErrorDeConexion("Respuesta inesperada del servidor.")
        return [Carrito.desde_dict(d) for d in datos if isinstance(d, dict)]

    def titulos_de_productos(self) -> dict[int, str] | None:
        """{id: título} del catálogo, o None si el catálogo no se pudo consultar.

        Un fallo aquí NO tumba el histórico: la pantalla muestra solo los IDs.
        """
        try:
            return {p.id: p.title for p in self._productos.listar()}
        except ErrorApi:
            return None
