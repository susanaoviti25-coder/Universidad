from dataclasses import dataclass

from app.models.rol import Rol


@dataclass(frozen=True, slots=True)
class SesionUsuario:
    """Datos de sesión guardados de forma local (cookie firmada de Flask)."""

    username: str
    token: str
    rol: Rol

    def a_dict(self) -> dict:
        return {"username": self.username, "token": self.token, "rol": self.rol.value}

    @classmethod
    def desde_dict(cls, datos: dict) -> "SesionUsuario":
        return cls(
            username=datos["username"],
            token=datos["token"],
            rol=Rol(datos["rol"]),  # ValueError si el rol no es válido
        )
