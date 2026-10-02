"""Sesión local, control de acceso por rol, CSRF y cabeceras de caché."""
import hmac
import secrets
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.models.rol import Rol
from app.models.sesion_usuario import SesionUsuario


def sesion_actual() -> SesionUsuario | None:
    """Lee el perfil ESTRICTAMENTE de la sesión local (no consulta la API)."""
    datos = session.get("usuario")
    if not datos:
        return None
    try:
        return SesionUsuario.desde_dict(datos)
    except (KeyError, ValueError, TypeError):
        session.pop("usuario", None)
        return None


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if sesion_actual() is None:
            if request.path.startswith("/api/"):
                return jsonify(error="No autenticado"), 401
            flash("Debes iniciar sesión para continuar.", "aviso")
            return redirect(url_for("auth.login"))
        return vista(*args, **kwargs)

    return envoltura


def roles_permitidos(*roles: Rol):
    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            usuario = sesion_actual()
            if usuario is None or usuario.rol not in roles:
                abort(403)
            return vista(*args, **kwargs)

        return login_requerido(envoltura)

    return decorador


def _token_csrf() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


class Seguridad:
    def registrar(self, app: Flask) -> None:
        @app.before_request
        def verificar_csrf():
            if request.method == "POST":
                enviado = request.form.get("csrf_token", "")
                esperado = session.get("csrf", "")
                if not esperado or not hmac.compare_digest(enviado, esperado):
                    abort(400)

        @app.after_request
        def sin_cache(resp):
            # Evita ver páginas privadas con el botón "atrás" tras cerrar sesión (US02).
            if request.endpoint != "static":
                resp.headers["Cache-Control"] = "no-store"
            return resp

        @app.context_processor
        def contexto():
            usuario = sesion_actual()
            return {
                "usuario": usuario,
                "es_admin": bool(usuario and usuario.rol is Rol.ADMINISTRADOR),
                "csrf_token": _token_csrf,
            }

        mensajes = {
            400: "Solicitud no válida o formulario expirado. Recarga la página.",
            403: "No tienes permisos para realizar esta acción.",
            404: "La página que buscas no existe.",
        }

        def manejador(error):
            codigo = error.code or 500
            return render_template(
                "error.html", codigo=codigo, mensaje=mensajes.get(codigo, "Error")
            ), codigo

        for codigo in mensajes:
            app.register_error_handler(codigo, manejador)
