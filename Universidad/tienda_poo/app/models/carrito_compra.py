"""Carrito de compra del Cliente (local a su sesión). No confundir con Carrito (US12, histórico de la API)."""
from dataclasses import dataclass

from app.models.producto import Producto

MAX_UNIDADES = 99


@dataclass(frozen=True, slots=True)
class LineaCompra:
    """Un producto del carrito con su cantidad."""

    producto: Producto
    cantidad: int

    @property
    def subtotal(self) -> float:
        return self.producto.price * self.cantidad


class CarritoCompra:
    """{producto_id: cantidad}. Se guarda en la sesión (cookie firmada), por eso solo guarda IDs."""

    def __init__(self, cantidades: dict[int, int] | None = None) -> None:
        self._cantidades: dict[int, int] = dict(cantidades or {})

    # ---- (de)serialización segura: la cookie puede traer basura ----
    @classmethod
    def desde_sesion(cls, datos) -> "CarritoCompra":
        limpio: dict[int, int] = {}
        if isinstance(datos, dict):
            for clave, valor in datos.items():
                try:
                    ident, cant = int(clave), int(valor)
                except (TypeError, ValueError):
                    continue
                if ident > 0 and 1 <= cant <= MAX_UNIDADES:
                    limpio[ident] = cant
        return cls(limpio)

    def a_sesion(self) -> dict[str, int]:
        return {str(i): c for i, c in self._cantidades.items()}

    # ---- operaciones ----
    @staticmethod
    def _validar(cantidad: int) -> None:
        if not 1 <= cantidad <= MAX_UNIDADES:
            raise ValueError(f"La cantidad debe estar entre 1 y {MAX_UNIDADES}.")

    def agregar(self, producto_id: int, cantidad: int = 1) -> None:
        self._validar(cantidad)
        nueva = self._cantidades.get(producto_id, 0) + cantidad
        if nueva > MAX_UNIDADES:
            raise ValueError(f"Máximo {MAX_UNIDADES} unidades por producto.")
        self._cantidades[producto_id] = nueva

    def cambiar(self, producto_id: int, cantidad: int) -> None:
        self._validar(cantidad)
        if producto_id in self._cantidades:
            self._cantidades[producto_id] = cantidad

    def quitar(self, producto_id: int) -> None:
        self._cantidades.pop(producto_id, None)

    def vaciar(self) -> None:
        self._cantidades.clear()

    # ---- consultas ----
    @property
    def cantidades(self) -> dict[int, int]:
        return dict(self._cantidades)

    @property
    def vacio(self) -> bool:
        return not self._cantidades

    @property
    def total_unidades(self) -> int:
        return sum(self._cantidades.values())
