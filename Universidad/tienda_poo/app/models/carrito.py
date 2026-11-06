"""Modelos de /carts (US12)."""
from dataclasses import dataclass, field
from datetime import datetime


def _entero(valor) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


@dataclass(frozen=True, slots=True)
class ItemCarrito:
    """Elemento del arreglo 'products': solo trae productId y quantity."""

    producto_id: int
    cantidad: int

    @classmethod
    def desde_dict(cls, datos) -> "ItemCarrito":
        datos = datos if isinstance(datos, dict) else {}
        return cls(
            producto_id=_entero(datos.get("productId")),
            cantidad=_entero(datos.get("quantity")),
        )


@dataclass(frozen=True, slots=True)
class Carrito:
    id: int
    usuario_id: int
    fecha: str
    items: tuple[ItemCarrito, ...] = field(default_factory=tuple)

    @classmethod
    def desde_dict(cls, datos: dict) -> "Carrito":
        productos = datos.get("products")
        productos = productos if isinstance(productos, list) else []
        return cls(
            id=_entero(datos.get("id")),
            usuario_id=_entero(datos.get("userId")),
            fecha=str(datos.get("date") or ""),
            items=tuple(ItemCarrito.desde_dict(p) for p in productos),
        )

    @property
    def fecha_legible(self) -> str:
        """dd/mm/aaaa. Si el formato no se reconoce, devuelve el texto original."""
        if not self.fecha:
            return "—"
        try:
            return datetime.fromisoformat(self.fecha).strftime("%d/%m/%Y")
        except ValueError:
            return self.fecha

    def a_dict(self, titulos: dict[int, str]) -> dict:
        """Cruza cada productId con el catálogo (reto lógico); sin título -> None."""
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "fecha": self.fecha_legible,
            "items": [
                {
                    "producto_id": i.producto_id,
                    "titulo": titulos.get(i.producto_id),
                    "cantidad": i.cantidad,
                }
                for i in self.items
            ],
        }
