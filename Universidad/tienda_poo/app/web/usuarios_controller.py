from flask import Blueprint, jsonify, render_template

from app.services.excepciones import ErrorApi
from app.services.servicio_usuarios import ServicioUsuarios
from app.web.seguridad import ROLES_AUDITORIA, roles_permitidos


class UsuariosController:
    """US11: directorio de usuarios. Solo Administrador o Auditor. Solo lectura (únicamente GET)."""

    def __init__(self, servicio: ServicioUsuarios) -> None:
        self._servicio = servicio
        bp = self.blueprint = Blueprint("usuarios", __name__)
        bp.add_url_rule("/usuarios", "lista", roles_permitidos(*ROLES_AUDITORIA)(self.lista))
        bp.add_url_rule(
            "/api/usuarios", "api_lista", roles_permitidos(*ROLES_AUDITORIA)(self.api_lista)
        )

    def lista(self):
        return render_template("usuarios.html")

    def api_lista(self):
        try:
            usuarios = self._servicio.listar()
        except ErrorApi:
            return jsonify(error="No fue posible cargar los usuarios."), 502
        return jsonify([u.a_dict() for u in usuarios])
