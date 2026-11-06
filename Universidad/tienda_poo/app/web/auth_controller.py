from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.excepciones import (
    CredencialesInvalidas,
    ErrorApi,
    PerfilNoAsignado,
)
from app.services.servicio_autenticacion import ServicioAutenticacion
from app.web.seguridad import sesion_actual


class AuthController:
    """US01 (login) y US02 (cierre de sesión)."""

    def __init__(self, servicio: ServicioAutenticacion) -> None:
        self._servicio = servicio
        self.blueprint = Blueprint("auth", __name__)
        self.blueprint.add_url_rule("/login", "login", self.login, methods=["GET", "POST"])
        self.blueprint.add_url_rule("/logout", "logout", self.logout, methods=["POST"])

    def login(self):
        if sesion_actual() is not None:
            return redirect(url_for("tienda.catalogo"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if not username or not password:
                flash("Ingresa usuario y contraseña.", "error")
                return render_template("login.html", username=username)
            try:
                sesion = self._servicio.iniciar_sesion(username, password)
            except CredencialesInvalidas:
                flash("Usuario o contraseña incorrectos.", "error")
            except PerfilNoAsignado:
                flash("Tu usuario no tiene un perfil asignado en la aplicación.", "error")
            except ErrorApi:
                flash("No fue posible conectar con el servidor. Intenta de nuevo.", "error")
            else:
                session.clear()
                session["usuario"] = sesion.a_dict()
                return redirect(url_for("tienda.catalogo"))
            return render_template("login.html", username=username)
        return render_template("login.html", username="")

    def logout(self):
        session.clear()  # elimina token, rol y usuario
        flash("Sesión cerrada correctamente.", "exito")
        return redirect(url_for("auth.login"))
