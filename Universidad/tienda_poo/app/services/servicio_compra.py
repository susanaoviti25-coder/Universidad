from app.models.carrito_compra import CarritoCompra, LineaCompra
from app.models.producto import Producto
from app.services.servicio_productos import ServicioProductos


class ServicioCompra:
    """Carrito de compra: valida productos y calcula líneas/total con precios del catálogo."""

    def __init__(self, productos: ServicioProductos) -> None:
        self._productos = productos

    def verificar_producto(self, producto_id: int) -> Producto:
        """Lanza ProductoNoEncontrado si no existe (no se agrega al carrito)."""
        return self._productos.obtener(producto_id)

    def detallar(self, carrito: CarritoCompra) -> tuple[list[LineaCompra], list[int]]:
        """Devuelve (líneas, ids que ya no existen en el catálogo). Lanza ErrorApi si falla la red."""
        if carrito.vacio:
            return [], []
        catalogo = {p.id: p for p in self._productos.listar()}
        lineas, faltantes = [], []
        for ident, cantidad in carrito.cantidades.items():
            if ident in catalogo:
                lineas.append(LineaCompra(catalogo[ident], cantidad))
            else:
                faltantes.append(ident)
        return lineas, faltantes

    @staticmethod
    def total(lineas: list[LineaCompra]) -> float:
        return sum(l.subtotal for l in lineas)
