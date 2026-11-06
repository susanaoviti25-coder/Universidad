from dataclasses import asdict, dataclass


@dataclass(slots=True)
class Producto:
    """Modelo que empata con el JSON de Fake Store API (/products)."""

    id: int
    title: str
    price: float
    description: str
    category: str
    image: str
    rate: float = 0.0
    count: int = 0

    @classmethod
    def desde_dict(cls, datos: dict) -> "Producto":
        rating = datos.get("rating") or {}
        return cls(
            id=int(datos["id"]),
            title=str(datos.get("title", "")),
            price=float(datos.get("price", 0)),
            description=str(datos.get("description", "")),
            category=str(datos.get("category", "")),
            image=str(datos.get("image", "")),
            rate=float(rating.get("rate", 0) or 0),
            count=int(rating.get("count", 0) or 0),
        )

    def a_dict(self) -> dict:
        return asdict(self)
