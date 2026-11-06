class ErrorApi(Exception):
    """Base de los errores al consumir Fake Store API."""


class ErrorDeConexion(ErrorApi):
    """Sin internet, timeout, caída del servidor o respuesta inesperada."""


class CredencialesInvalidas(ErrorApi):
    """Usuario o contraseña incorrectos."""


class PerfilNoAsignado(ErrorApi):
    """El usuario existe en la API pero no tiene perfil local asignado."""


class ProductoNoEncontrado(ErrorApi):
    """El producto no existe o la consulta falló."""
