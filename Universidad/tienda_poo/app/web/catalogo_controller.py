from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models.rol import Rol
from app.services.excepciones import ErrorApi
from app.services.servicio_productos import ServicioProductos
from app.web.seguridad import login_requerido, roles_permitidos, sesion_actual


class CatalogoController:
    """US03 (catálogo), US04 (filtro por categoría) y US05 (detalle por rol)."""

    def __init__(self, servicio: ServicioProductos) -> None:
        self._servicio = servicio
        bp = self.blueprint = Blueprint("tienda", __name__)
        bp.add_url_rule("/", "inicio", self.inicio)
        bp.add_url_rule("/catalogo", "catalogo", login_requerido(self.catalogo))
        bp.add_url_rule("/api/categorias", "api_categorias", login_requerido(self.api_categorias))
        bp.add_url_rule("/api/productos", "api_productos", login_requerido(self.api_productos))
        bp.add_url_rule("/producto/<int:producto_id>", "detalle", login_requerido(self.detalle))
        bp.add_url_rule(
            "/producto/<int:producto_id>/editar", "editar",
            roles_permitidos(Rol.ADMINISTRADOR)(self.editar), methods=["GET", "POST"],
        )
        bp.add_url_rule(
            "/producto/<int:producto_id>/eliminar", "eliminar",
            roles_permitidos(Rol.ADMINISTRADOR)(self.eliminar), methods=["POST"],
        )

    def inicio(self):
        destino = "tienda.catalogo" if sesion_actual() else "auth.login"
        return redirect(url_for(destino))

    def catalogo(self):
        return render_template("catalogo.html")

    # ---- endpoints JSON que consume el JavaScript del catálogo ----
    def api_categorias(self):
        try:
            return jsonify(self._servicio.categorias())
        except ErrorApi:
            return jsonify(error="No fue posible cargar las categorías."), 502

    def api_productos(self):
        categoria = request.args.get("categoria", "").strip()
        try:
            productos = (
                self._servicio.por_categoria(categoria)
                if categoria
                else self._servicio.listar()
            )
        except ErrorApi:
            return jsonify(error="No fue posible cargar los productos."), 502
        return jsonify([p.a_dict() for p in productos])

    # ---- US05 ----
    def detalle(self, producto_id: int):
        try:
            producto = self._servicio.obtener(producto_id)
        except ErrorApi:
            flash("Producto no disponible", "alerta")
            return redirect(url_for("tienda.catalogo"))
        return render_template("detalle.html", producto=producto)

    def editar(self, producto_id: int):
        try:
            producto = self._servicio.obtener(producto_id)
        except ErrorApi:
            flash("Producto no disponible", "alerta")
            return redirect(url_for("tienda.catalogo"))

        try:
            categorias = self._servicio.categorias()
        except ErrorApi:
            categorias = []
        if producto.category not in categorias:
            categorias.append(producto.category)

        if request.method == "POST":
            datos, error = self._validar(request.form)
            if error:
                flash(error, "error")
                return render_template("editar.html", producto=producto, categorias=categorias), 400
            try:
                self._servicio.actualizar(producto_id, {**datos, "image": producto.image})
            except ErrorApi:
                flash("No fue posible guardar los cambios. Intenta de nuevo.", "error")
                return render_template("editar.html", producto=producto, categorias=categorias), 502
            flash(
                "Cambios enviados. Fake Store API simula la edición y no la persiste.",
                "exito",
            )
            return redirect(url_for("tienda.detalle", producto_id=producto_id))
        return render_template("editar.html", producto=producto, categorias=categorias)

    def eliminar(self, producto_id: int):
        try:
            self._servicio.eliminar(producto_id)
        except ErrorApi:
            flash("No fue posible eliminar el producto. Intenta de nuevo.", "error")
            return redirect(url_for("tienda.detalle", producto_id=producto_id))
        flash("Producto eliminado. Fake Store API simula el borrado y no lo persiste.", "exito")
        return redirect(url_for("tienda.catalogo"))

    @staticmethod
    def _validar(form):
        titulo = form.get("title", "").strip()
        descripcion = form.get("description", "").strip()
        categoria = form.get("category", "").strip()
        try:
            precio = float(form.get("price", ""))
        except ValueError:
            return None, "El precio debe ser un número."
        if not titulo or not descripcion or not categoria:
            return None, "Título, descripción y categoría son obligatorios."
        if precio <= 0:
            return None, "El precio debe ser mayor que cero."
        return {
            "title": titulo, "price": precio,
            "description": descripcion, "category": categoria,
        }, None
