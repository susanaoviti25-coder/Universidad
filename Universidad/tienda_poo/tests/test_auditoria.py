"""Pruebas US11 (usuarios) y US12 (carritos globales). No necesitan internet."""
import re
import unittest
from pathlib import Path

from app import create_app
from app.models.carrito import Carrito
from app.models.usuario import Usuario
from app.services.excepciones import ErrorDeConexion
from app.services.fake_store_client import FakeStoreClient

CREDENCIALES = {"mor_2314": "83r5^_", "johnd": "m38rmF$", "kevinryan": "kev02937@"}

USUARIOS = [
    {"id": 1, "email": "john@gmail.com", "username": "johnd", "password": "m38rmF$",
     "name": {"firstname": "john", "lastname": "doe"}, "phone": "1-570-236-7033",
     "address": {"city": "kilcoole", "street": "new road", "number": 7682, "zipcode": "12926-3874",
                 "geolocation": {"lat": "-37.3159", "long": "81.1496"}}},
    # Casos límite: objetos anidados nulos o ausentes
    {"id": 2, "email": "sin.datos@x.com", "username": "nulo", "name": None, "address": None, "phone": None},
    {"id": 3, "email": "parcial@x.com", "username": "parcial", "name": {"firstname": "maria"},
     "address": {"city": "cdmx", "geolocation": None}, "phone": "555"},
]
PRODUCTOS = [
    {"id": 1, "title": "Mochila", "price": 10.0, "description": "d", "category": "c", "image": "i"},
    {"id": 2, "title": "Anillo", "price": 20.0, "description": "d", "category": "c", "image": "i"},
]
CARRITOS = [
    {"id": 1, "userId": 1, "date": "2020-03-02T00:00:00.000Z",
     "products": [{"productId": 1, "quantity": 4}, {"productId": 2, "quantity": 1}, {"productId": 99, "quantity": 3}]},
    {"id": 2, "userId": 2, "date": "fecha-rara", "products": []},
    {"id": 3, "userId": 3, "date": "2020-01-02T00:00:02.000Z", "products": None},
]


class Resp:
    def __init__(self, status=200, datos=None):
        self.status_code, self._datos = status, datos

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        if self._datos is None:
            raise ValueError("sin cuerpo")
        return self._datos


class ClienteFalso(FakeStoreClient):
    def __init__(self):
        super().__init__("http://falso")
        self.caido = set()          # rutas que fallan por red
        self.llamadas = []

    def solicitar(self, metodo, ruta, **kw):
        self.llamadas.append((metodo, ruta))
        if ruta in self.caido:
            raise ErrorDeConexion("sin red")
        if ruta == "/auth/login":
            j = kw["json"]
            if CREDENCIALES.get(j["username"]) == j["password"]:
                return Resp(200, {"token": "tok"})
            return Resp(401)
        if ruta == "/users":
            return Resp(200, USUARIOS)
        if ruta == "/carts":
            return Resp(200, CARRITOS)
        if ruta == "/products":
            return Resp(200, PRODUCTOS)
        return Resp(404)


class Base(unittest.TestCase):
    def setUp(self):
        self.cliente = ClienteFalso()
        app = create_app(cliente=self.cliente)
        app.config["TESTING"] = True
        self.http = app.test_client()

    def token(self, url="/login"):
        html = self.http.get(url).get_data(as_text=True)
        return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)

    def entrar(self, usuario):
        return self.http.post("/login", data={
            "csrf_token": self.token(), "username": usuario, "password": CREDENCIALES[usuario]})


class TestModelos(unittest.TestCase):
    def test_usuario_completo(self):
        u = Usuario.desde_dict(USUARIOS[0])
        self.assertEqual(u.nombre_completo, "John Doe")
        self.assertEqual(u.direccion.calle_completa, "new road 7682")
        self.assertEqual(u.direccion.geolocalizacion.lat, "-37.3159")

    def test_usuario_con_anidados_nulos_no_se_cae(self):
        for datos in USUARIOS[1:] + [{}, {"id": "x", "name": 5, "address": []}]:
            u = Usuario.desde_dict(datos)
            self.assertIsInstance(u.a_dict()["direccion"]["calle"], str)

    def test_password_nunca_se_expone(self):
        self.assertNotIn("password", Usuario.desde_dict(USUARIOS[0]).a_dict())
        self.assertNotIn("m38rmF$", str(Usuario.desde_dict(USUARIOS[0])))

    def test_carrito_fecha_y_items(self):
        c = Carrito.desde_dict(CARRITOS[0])
        self.assertEqual(c.fecha_legible, "02/03/2020")
        self.assertEqual(len(c.items), 3)
        self.assertEqual(Carrito.desde_dict(CARRITOS[1]).fecha_legible, "fecha-rara")
        self.assertEqual(Carrito.desde_dict(CARRITOS[2]).items, ())      # products: null
        self.assertEqual(Carrito.desde_dict({}).fecha_legible, "—")


class TestUsuarios(Base):
    def test_admin_y_auditor_ven_la_lista(self):
        for u in ("mor_2314", "kevinryan"):
            self.setUp()
            self.entrar(u)
            self.assertEqual(self.http.get("/usuarios").status_code, 200)
            datos = self.http.get("/api/usuarios").get_json()
            self.assertEqual(len(datos), 3)
            self.assertEqual(datos[0]["nombre_completo"], "John Doe")
            self.assertEqual(datos[0]["email"], "john@gmail.com")
            self.assertEqual(datos[0]["telefono"], "1-570-236-7033")
            self.assertEqual(datos[0]["username"], "johnd")
            self.assertEqual(datos[1]["nombre_completo"], "")          # anidado nulo sin caída
            self.assertNotIn("password", self.http.get("/api/usuarios").get_data(as_text=True))

    def test_cliente_bloqueado_en_pagina_y_api(self):
        self.entrar("johnd")
        self.assertEqual(self.http.get("/usuarios").status_code, 403)
        r = self.http.get("/api/usuarios")
        self.assertEqual(r.status_code, 403)
        self.assertIn("error", r.get_json())
        self.assertNotIn(("GET", "/users"), self.cliente.llamadas)      # ni siquiera consulta la API

    def test_cliente_no_ve_el_boton_en_el_menu(self):
        self.entrar("johnd")
        html = self.http.get("/catalogo").get_data(as_text=True)
        self.assertNotIn("/usuarios", html)
        self.assertNotIn("/carritos", html)

    def test_admin_y_auditor_ven_el_menu(self):
        for u in ("mor_2314", "kevinryan"):
            self.setUp()
            self.entrar(u)
            html = self.http.get("/catalogo").get_data(as_text=True)
            self.assertIn('href="/usuarios"', html)
            self.assertIn('href="/carritos"', html)

    def test_sin_sesion(self):
        self.assertEqual(self.http.get("/usuarios").status_code, 302)
        self.assertEqual(self.http.get("/api/usuarios").status_code, 401)

    def test_error_de_red_devuelve_502(self):
        self.entrar("kevinryan")
        self.cliente.caido.add("/users")
        self.assertEqual(self.http.get("/api/usuarios").status_code, 502)

    def test_solo_lectura(self):
        self.entrar("mor_2314")
        t = self.token("/usuarios")
        for ruta in ("/usuarios", "/api/usuarios"):
            self.assertEqual(self.http.post(ruta, data={"csrf_token": t}).status_code, 405)
            self.assertEqual(self.http.put(ruta).status_code, 405)
            self.assertEqual(self.http.delete(ruta).status_code, 405)
        html = self.http.get("/usuarios").get_data(as_text=True)
        self.assertNotIn("<form", html.split("</header>")[1])           # ningún formulario en la pantalla


class TestCarritos(Base):
    def test_listado_con_titulos_cruzados(self):
        self.entrar("kevinryan")
        self.assertEqual(self.http.get("/carritos").status_code, 200)
        j = self.http.get("/api/carritos").get_json()
        self.assertTrue(j["catalogo_disponible"])
        c1 = j["carritos"][0]
        self.assertEqual((c1["id"], c1["usuario_id"], c1["fecha"]), (1, 1, "02/03/2020"))
        self.assertEqual([(i["producto_id"], i["titulo"], i["cantidad"]) for i in c1["items"]],
                         [(1, "Mochila", 4), (2, "Anillo", 1), (99, None, 3)])
        self.assertEqual(j["carritos"][1]["items"], [])
        self.assertEqual(j["carritos"][2]["items"], [])                  # products null

    def test_si_falla_el_catalogo_se_muestran_solo_ids(self):
        self.entrar("mor_2314")
        self.cliente.caido.add("/products")
        r = self.http.get("/api/carritos")
        self.assertEqual(r.status_code, 200)
        j = r.get_json()
        self.assertFalse(j["catalogo_disponible"])
        self.assertTrue(all(i["titulo"] is None for i in j["carritos"][0]["items"]))

    def test_cliente_bloqueado(self):
        self.entrar("johnd")
        self.assertEqual(self.http.get("/carritos").status_code, 403)
        self.assertEqual(self.http.get("/api/carritos").status_code, 403)
        self.assertNotIn(("GET", "/carts"), self.cliente.llamadas)

    def test_sin_sesion(self):
        self.assertEqual(self.http.get("/carritos").status_code, 302)
        self.assertEqual(self.http.get("/api/carritos").status_code, 401)

    def test_error_de_red_devuelve_502(self):
        self.entrar("kevinryan")
        self.cliente.caido.add("/carts")
        self.assertEqual(self.http.get("/api/carritos").status_code, 502)

    def test_solo_lectura(self):
        self.entrar("kevinryan")
        t = self.token("/carritos")
        for ruta in ("/carritos", "/api/carritos"):
            self.assertEqual(self.http.post(ruta, data={"csrf_token": t}).status_code, 405)
            self.assertEqual(self.http.delete(ruta).status_code, 405)
        html = self.http.get("/carritos").get_data(as_text=True)
        self.assertNotIn("<form", html.split("</header>")[1])
        ruta_js = Path(__file__).resolve().parent.parent / "app" / "static" / "js" / "carritos.js"
        js = ruta_js.read_text(encoding="utf-8")
        for prohibido in ("DELETE", "PUT", "POST", "Eliminar", "Editar"):
            self.assertNotIn(prohibido, js)


if __name__ == "__main__":
    unittest.main()
