from flask import Blueprint, jsonify, render_template

from app.services.excepciones import ErrorApi
from app.services.servicio_carritos import ServicioCarritos
from app.web.seguridad import ROLES_AUDITORIA, roles_permitidos


class CarritosController:
    """US12: histórico global de carritos. Solo Administrador o Auditor. Solo lectura (únicamente GET)."""

    def __init__(self, servicio: ServicioCarritos) -> None:
        self._servicio = servicio
        bp = self.blueprint = Blueprint("carritos", __name__)
        bp.add_url_rule("/carritos", "lista", roles_permitidos(*ROLES_AUDITORIA)(self.lista))
        bp.add_url_rule(
            "/api/carritos", "api_lista", roles_permitidos(*ROLES_AUDITORIA)(self.api_lista)
        )

    def lista(self):
        return render_template("carritos.html")

    def api_lista(self):
        try:
            carritos = self._servicio.listar()
        except ErrorApi:
            return jsonify(error="No fue posible cargar los carritos."), 502
        titulos = self._servicio.titulos_de_productos()
        return jsonify(
            catalogo_disponible=titulos is not None,
            carritos=[c.a_dict(titulos or {}) for c in carritos],
        )
