from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.models.carrito_compra import MAX_UNIDADES, CarritoCompra
from app.services.excepciones import ErrorApi
from app.services.servicio_compra import ServicioCompra
from app.web.seguridad import ROLES_COMPRA, roles_permitidos


def _leer() -> CarritoCompra:
    return CarritoCompra.desde_sesion(session.get("carrito"))


def _guardar(carrito: CarritoCompra) -> None:
    session["carrito"] = carrito.a_sesion()


class CompraController:
    """Carrito de compra (agregar, ver, cambiar cantidad, quitar, vaciar). Solo el Cliente."""

    def __init__(self, servicio: ServicioCompra) -> None:
        self._servicio = servicio
        bp = self.blueprint = Blueprint("compra", __name__)
        solo_cliente = roles_permitidos(*ROLES_COMPRA)
        bp.add_url_rule("/mi-carrito", "ver", solo_cliente(self.ver))
        bp.add_url_rule(
            "/mi-carrito/agregar/<int:producto_id>", "agregar", solo_cliente(self.agregar), methods=["POST"]
        )
        bp.add_url_rule(
            "/mi-carrito/cantidad/<int:producto_id>", "cambiar", solo_cliente(self.cambiar), methods=["POST"]
        )
        bp.add_url_rule(
            "/mi-carrito/quitar/<int:producto_id>", "quitar", solo_cliente(self.quitar), methods=["POST"]
        )
        bp.add_url_rule("/mi-carrito/vaciar", "vaciar", solo_cliente(self.vaciar), methods=["POST"])

    def ver(self):
        carrito = _leer()
        try:
            lineas, faltantes = self._servicio.detallar(carrito)
        except ErrorApi:
            return render_template("mi_carrito.html", lineas=[], total=0, error=True, max_unidades=MAX_UNIDADES), 502
        if faltantes:                      # producto que ya no existe en el catálogo: se retira
            for ident in faltantes:
                carrito.quitar(ident)
            _guardar(carrito)
            flash("Se retiraron del carrito productos que ya no están disponibles.", "aviso")
        return render_template(
            "mi_carrito.html", lineas=lineas, total=self._servicio.total(lineas),
            error=False, max_unidades=MAX_UNIDADES,
        )

    def agregar(self, producto_id: int):
        cantidad = self._cantidad()
        if cantidad is None:
            return redirect(url_for("tienda.detalle", producto_id=producto_id))
        try:
            producto = self._servicio.verificar_producto(producto_id)   # no se agrega lo que no existe
        except ErrorApi:
            flash("Producto no disponible", "alerta")
            return redirect(url_for("tienda.catalogo"))
        carrito = _leer()
        try:
            carrito.agregar(producto_id, cantidad)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("tienda.detalle", producto_id=producto_id))
        _guardar(carrito)
        flash(f"«{producto.title}» se agregó al carrito.", "exito")
        return redirect(url_for("tienda.detalle", producto_id=producto_id))

    def cambiar(self, producto_id: int):
        cantidad = self._cantidad()
        if cantidad is not None:
            carrito = _leer()
            try:
                carrito.cambiar(producto_id, cantidad)
            except ValueError as exc:
                flash(str(exc), "error")
            else:
                _guardar(carrito)
        return redirect(url_for("compra.ver"))

    def quitar(self, producto_id: int):
        carrito = _leer()
        carrito.quitar(producto_id)
        _guardar(carrito)
        flash("Producto quitado del carrito.", "exito")
        return redirect(url_for("compra.ver"))

    def vaciar(self):
        _guardar(CarritoCompra())
        flash("Carrito vaciado.", "exito")
        return redirect(url_for("compra.ver"))

    @staticmethod
    def _cantidad() -> int | None:
        try:
            return int(request.form.get("cantidad", "1"))
        except ValueError:
            flash("La cantidad debe ser un número entero.", "error")
            return None
