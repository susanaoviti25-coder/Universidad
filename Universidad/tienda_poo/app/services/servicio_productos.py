from urllib.parse import quote

from app.models.producto import Producto
from app.services.excepciones import ErrorDeConexion, ProductoNoEncontrado
from app.services.fake_store_client import FakeStoreClient


class ServicioProductos:
    """US03, US04 y US05: consumo de /products, categorías y detalle."""

    def __init__(self, cliente: FakeStoreClient) -> None:
        self._cliente = cliente

    @staticmethod
    def _json(resp):
        if not resp.ok:
            raise ErrorDeConexion(f"El servidor respondió {resp.status_code}.")
        try:
            return resp.json()
        except ValueError:
            return None

    def listar(self) -> list[Producto]:
        datos = self._json(self._cliente.solicitar("GET", "/products"))
        if not isinstance(datos, list):
            raise ErrorDeConexion("Respuesta inesperada del servidor.")
        return [Producto.desde_dict(d) for d in datos]

    def categorias(self) -> list[str]:
        datos = self._json(self._cliente.solicitar("GET", "/products/categories"))
        if not isinstance(datos, list):
            raise ErrorDeConexion("Respuesta inesperada del servidor.")
        return [str(c) for c in datos]

    def por_categoria(self, categoria: str) -> list[Producto]:
        ruta = f"/products/category/{quote(categoria, safe='')}"
        datos = self._json(self._cliente.solicitar("GET", ruta))
        if not isinstance(datos, list):
            raise ErrorDeConexion("Respuesta inesperada del servidor.")
        return [Producto.desde_dict(d) for d in datos]

    def obtener(self, producto_id: int) -> Producto:
        try:
            resp = self._cliente.solicitar("GET", f"/products/{producto_id}")
            datos = self._json(resp)
        except ErrorDeConexion as exc:
            raise ProductoNoEncontrado("Producto no disponible") from exc
        # Fake Store API responde 200 con cuerpo vacío si el id no existe.
        if not isinstance(datos, dict) or "id" not in datos:
            raise ProductoNoEncontrado("Producto no disponible")
        return Producto.desde_dict(datos)

    def actualizar(self, producto_id: int, datos: dict) -> None:
        self._json(self._cliente.solicitar("PUT", f"/products/{producto_id}", json=datos))

    def eliminar(self, producto_id: int) -> None:
        self._json(self._cliente.solicitar("DELETE", f"/products/{producto_id}"))
