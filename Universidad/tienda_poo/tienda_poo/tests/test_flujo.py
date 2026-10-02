"""Pruebas sin internet: se reemplaza FakeStoreClient por un cliente falso."""
import re
import unittest

from app import create_app
from app.services.excepciones import ErrorDeConexion
from app.services.fake_store_client import FakeStoreClient

PRODUCTOS = [
    {"id": 1, "title": "Mochila", "price": 109.95, "description": "Desc 1",
     "category": "men's clothing", "image": "http://x/1.jpg", "rating": {"rate": 3.9, "count": 120}},
    {"id": 2, "title": "Anillo", "price": 10.5, "description": "Desc 2",
     "category": "jewelery", "image": "http://x/2.jpg", "rating": {"rate": 4.1, "count": 50}},
]
USUARIOS = {"mor_2314": "83r5^_", "johnd": "m38rmF$", "kevinryan": "kev02937@", "sinperfil": "x"}


class RespuestaFalsa:
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
        self.caido = False
        self.llamadas = []

    def solicitar(self, metodo, ruta, **kw):
        self.llamadas.append((metodo, ruta))
        if self.caido:
            raise ErrorDeConexion("sin red")
        if ruta == "/auth/login":
            j = kw["json"]
            if USUARIOS.get(j["username"]) == j["password"]:
                return RespuestaFalsa(200, {"token": "tok123"})
            return RespuestaFalsa(401)
        if metodo == "GET" and ruta == "/products":
            return RespuestaFalsa(200, PRODUCTOS)
        if metodo == "GET" and ruta == "/products/categories":
            return RespuestaFalsa(200, ["men's clothing", "jewelery"])
        if metodo == "GET" and ruta.startswith("/products/category/"):
            cat = ruta.rsplit("/", 1)[1].replace("%27", "'").replace("%20", " ")
            return RespuestaFalsa(200, [p for p in PRODUCTOS if p["category"] == cat])
        if metodo == "GET" and ruta.startswith("/products/"):
            pid = int(ruta.rsplit("/", 1)[1])
            return RespuestaFalsa(200, next((p for p in PRODUCTOS if p["id"] == pid), None))
        if metodo in ("PUT", "DELETE"):
            return RespuestaFalsa(200, {"id": 1})
        return RespuestaFalsa(404)


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
            "csrf_token": self.token(), "username": usuario, "password": USUARIOS[usuario]})


class TestLoginLogout(Base):
    def test_login_correcto_guarda_perfil_local(self):
        r = self.entrar("mor_2314")
        self.assertEqual(r.status_code, 302)
        with self.http.session_transaction() as s:
            self.assertEqual(s["usuario"]["rol"], "Administrador")
            self.assertEqual(s["usuario"]["token"], "tok123")

    def test_credenciales_invalidas(self):
        r = self.http.post("/login", data={"csrf_token": self.token(), "username": "johnd", "password": "mal"})
        self.assertIn("incorrectos", r.get_data(as_text=True))

    def test_usuario_sin_perfil(self):
        r = self.entrar("sinperfil")
        self.assertIn("perfil asignado", r.get_data(as_text=True))

    def test_logout_limpia_sesion_y_bloquea_catalogo(self):
        self.entrar("johnd")
        t = self.token("/catalogo")
        r = self.http.post("/logout", data={"csrf_token": t})
        self.assertEqual(r.status_code, 302)
        with self.http.session_transaction() as s:
            self.assertNotIn("usuario", s)
        self.assertEqual(self.http.get("/catalogo").status_code, 302)

    def test_post_sin_csrf_es_rechazado(self):
        self.assertEqual(self.http.post("/login", data={"username": "a", "password": "b"}).status_code, 400)


class TestCatalogo(Base):
    def test_api_requiere_sesion(self):
        self.assertEqual(self.http.get("/api/productos").status_code, 401)

    def test_lista_y_filtro(self):
        self.entrar("kevinryan")
        self.assertEqual(len(self.http.get("/api/productos").get_json()), 2)
        r = self.http.get("/api/productos?categoria=men's clothing").get_json()
        self.assertEqual([p["id"] for p in r], [1])
        self.assertEqual(self.http.get("/api/categorias").get_json(), ["men's clothing", "jewelery"])

    def test_error_de_red_devuelve_502(self):
        self.entrar("johnd")
        self.cliente.caido = True
        self.assertEqual(self.http.get("/api/productos").status_code, 502)


class TestDetalle(Base):
    def test_cliente_y_auditor_no_ven_controles(self):
        for u in ("johnd", "kevinryan"):
            self.setUp()
            self.entrar(u)
            html = self.http.get("/producto/1").get_data(as_text=True)
            self.assertIn("Mochila", html)
            self.assertNotIn("Editar", html)
            self.assertNotIn("Eliminar", html)

    def test_admin_ve_controles(self):
        self.entrar("mor_2314")
        html = self.http.get("/producto/1").get_data(as_text=True)
        self.assertIn("Editar", html)
        self.assertIn("Eliminar", html)

    def test_producto_inexistente_alerta_y_regresa_al_catalogo(self):
        self.entrar("johnd")
        r = self.http.get("/producto/999")
        self.assertEqual(r.headers["Location"], "/catalogo")
        html = self.http.get("/catalogo").get_data(as_text=True)
        self.assertIn("Producto no disponible", html)

    def test_cliente_no_puede_eliminar_ni_editar(self):
        self.entrar("johnd")
        t = self.token("/producto/1")
        self.assertEqual(self.http.post("/producto/1/eliminar", data={"csrf_token": t}).status_code, 403)
        self.assertEqual(self.http.get("/producto/1/editar").status_code, 403)

    def test_admin_elimina_y_edita(self):
        self.entrar("mor_2314")
        t = self.token("/producto/1")
        r = self.http.post("/producto/1/eliminar", data={"csrf_token": t})
        self.assertEqual(r.headers["Location"], "/catalogo")
        self.assertIn(("DELETE", "/products/1"), self.cliente.llamadas)
        r = self.http.post("/producto/1/editar", data={
            "csrf_token": t, "title": "Nuevo", "price": "12.5", "description": "d", "category": "jewelery"})
        self.assertEqual(r.status_code, 302)
        self.assertIn(("PUT", "/products/1"), self.cliente.llamadas)
        r = self.http.post("/producto/1/editar", data={
            "csrf_token": t, "title": "Nuevo", "price": "abc", "description": "d", "category": "jewelery"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
