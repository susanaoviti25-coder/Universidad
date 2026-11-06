"""Modelos de /users (US11). Soportan objetos anidados sin caerse por referencias nulas."""
from dataclasses import dataclass, field


def _texto(valor) -> str:
    """Convierte cualquier valor del JSON a texto; None -> ''."""
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


def _dict(valor) -> dict:
    """Devuelve el valor solo si es un objeto JSON; si es None u otro tipo -> {}."""
    return valor if isinstance(valor, dict) else {}


@dataclass(frozen=True, slots=True)
class Geolocalizacion:
    lat: str = ""
    lng: str = ""

    @classmethod
    def desde_dict(cls, datos) -> "Geolocalizacion":
        datos = _dict(datos)
        return cls(lat=_texto(datos.get("lat")), lng=_texto(datos.get("long")))

    @property
    def disponible(self) -> bool:
        return bool(self.lat or self.lng)


@dataclass(frozen=True, slots=True)
class Direccion:
    ciudad: str = ""
    calle: str = ""
    numero: str = ""
    codigo_postal: str = ""
    geolocalizacion: Geolocalizacion = field(default_factory=Geolocalizacion)

    @classmethod
    def desde_dict(cls, datos) -> "Direccion":
        datos = _dict(datos)
        return cls(
            ciudad=_texto(datos.get("city")),
            calle=_texto(datos.get("street")),
            numero=_texto(datos.get("number")),
            codigo_postal=_texto(datos.get("zipcode")),
            geolocalizacion=Geolocalizacion.desde_dict(datos.get("geolocation")),
        )

    @property
    def calle_completa(self) -> str:
        return f"{self.calle} {self.numero}".strip()


@dataclass(frozen=True, slots=True)
class Usuario:
    """Usuario de Fake Store API. NO se guarda el campo 'password' que envía la API."""

    id: int
    username: str
    email: str
    telefono: str
    nombre: str
    apellido: str
    direccion: Direccion = field(default_factory=Direccion)

    @classmethod
    def desde_dict(cls, datos: dict) -> "Usuario":
        nombre = _dict(datos.get("name"))
        try:
            ident = int(datos.get("id", 0) or 0)
        except (TypeError, ValueError):
            ident = 0
        return cls(
            id=ident,
            username=_texto(datos.get("username")),
            email=_texto(datos.get("email")),
            telefono=_texto(datos.get("phone")),
            nombre=_texto(nombre.get("firstname")),
            apellido=_texto(nombre.get("lastname")),
            direccion=Direccion.desde_dict(datos.get("address")),
        )

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}".strip().title()

    def a_dict(self) -> dict:
        d = self.direccion
        return {
            "id": self.id,
            "nombre_completo": self.nombre_completo,
            "email": self.email,
            "telefono": self.telefono,
            "username": self.username,
            "direccion": {
                "calle": d.calle_completa,
                "ciudad": d.ciudad,
                "codigo_postal": d.codigo_postal,
                "lat": d.geolocalizacion.lat,
                "lng": d.geolocalizacion.lng,
            },
        }
