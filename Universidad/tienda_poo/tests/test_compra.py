"""Pruebas del carrito de compra (agregar, ver, cambiar, quitar, vaciar). Sin internet."""
import re
import unittest

from app import create_app
from app.models.carrito_compra import MAX_UNIDADES, CarritoCompra
from app.services.excepciones import ErrorDeConexion
from app.services.fake_store_client import FakeStoreClient

CREDENCIALES = {"mor_2314": "83r5^_", "johnd": "m38rmF$", "kevinryan": "kev02937@"}
PRODUCTOS = [
    {"id": 1, "title": "Mochila", "price": 10.0, "description": "d", "category": "c", "image": "i"},
    {"id": 2, "title": "Anillo", "price": 20.5, "description": "d", "category": "c", "image": "i"},
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
        self.caido = set()

    def solicitar(self, metodo, ruta, **kw):
        if ruta in self.caido:
            raise ErrorDeConexion("sin red")
        if ruta == "/auth/login":
            j = kw["json"]
            return Resp(200, {"token": "t"}) if CREDENCIALES.get(j["username"]) == j["password"] else Resp(401)
        if ruta == "/products":
            return Resp(200, PRODUCTOS)
        if ruta.startswith("/products/") and ruta.rsplit("/", 1)[1].isdigit():
            pid = int(ruta.rsplit("/", 1)[1])
            return Resp(200, next((p for p in PRODUCTOS if p["id"] == pid), None))
        return Resp(404)


class TestModelo(unittest.TestCase):
    def test_agregar_acumula_y_limita(self):
        c = CarritoCompra()
        c.agregar(1, 2); c.agregar(1, 3)
        self.assertEqual(c.cantidades, {1: 5})
        with self.assertRaises(ValueError):
            c.agregar(1, MAX_UNIDADES)          # 5 + 99 > 99
        for malo in (0, -1, MAX_UNIDADES + 1):
            with self.assertRaises(ValueError):
                c.agregar(2, malo)
        self.assertEqual(c.cantidades, {1: 5})  # nada cambió

    def test_cambiar_quitar_vaciar(self):
        c = CarritoCompra({1: 1, 2: 2})
        c.cambiar(1, 7); c.quitar(2)
        self.assertEqual(c.cantidades, {1: 7})
        self.assertEqual(c.total_unidades, 7)
        c.vaciar()
        self.assertTrue(c.vacio)

    def test_desde_sesion_ignora_basura(self):
        c = CarritoCompra.desde_sesion({"1": 2, "abc": 1, "2": "x", "3": 0, "4": 500, "-1": 2, "5": None})
        self.assertEqual(c.cantidades, {1: 2})
        for raro in (None, [], "texto", 5):
            self.assertTrue(CarritoCompra.desde_sesion(raro).vacio)


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

    def agregar(self, pid, cantidad="1"):
        return self.http.post(f"/mi-carrito/agregar/{pid}",
                              data={"csrf_token": self.token("/catalogo"), "cantidad": cantidad})

    def guardado(self):
        with self.http.session_transaction() as s:
            return s.get("carrito")


class TestCompra(Base):
    def test_cliente_agrega_y_ve_el_carrito(self):
        self.entrar("johnd")
        r = self.agregar(1, "2")
        self.assertEqual(r.status_code, 302)
        self.agregar(2, "1"); self.agregar(1, "1")                    # 1 se acumula: 3
        self.assertEqual(self.guardado(), {"1": 3, "2": 1})
        html = self.http.get("/mi-carrito").get_data(as_text=True)
        for esperado in ("Mochila", "Anillo", "$10.00", "$20.50", "$30.00", "$50.50"):
            self.assertIn(esperado, html)                             # precio, subtotal 3x10 y total

    def test_mensaje_de_exito_y_contador_en_menu(self):
        self.entrar("johnd")
        self.agregar(1, "2")
        html = self.http.get("/producto/1").get_data(as_text=True)
        self.assertIn("se agregó al carrito", html)
        self.assertIn("Agregar al carrito", html)
        self.assertIn('contador-carrito">2<', html)

    def test_producto_inexistente_no_se_agrega(self):
        self.entrar("johnd")
        r = self.agregar(999)
        self.assertEqual(r.headers["Location"], "/catalogo")
        self.assertIsNone(self.guardado())
        self.assertIn("Producto no disponible", self.http.get("/catalogo").get_data(as_text=True))

    def test_cantidades_invalidas(self):
        self.entrar("johnd")
        for mala in ("0", "-3", "abc", "100", ""):
            self.agregar(1, mala)
        self.assertFalse(self.guardado())                             # nada se guardó

    def test_cambiar_quitar_vaciar(self):
        self.entrar("johnd")
        self.agregar(1, "2"); self.agregar(2, "1")
        t = self.token("/mi-carrito")
        self.http.post("/mi-carrito/cantidad/1", data={"csrf_token": t, "cantidad": "5"})
        self.assertEqual(self.guardado(), {"1": 5, "2": 1})
        self.http.post("/mi-carrito/cantidad/1", data={"csrf_token": t, "cantidad": "0"})   # inválido: no cambia
        self.assertEqual(self.guardado()["1"], 5)
        self.http.post("/mi-carrito/quitar/2", data={"csrf_token": t})
        self.assertEqual(self.guardado(), {"1": 5})
        self.http.post("/mi-carrito/vaciar", data={"csrf_token": t})
        self.assertEqual(self.guardado(), {})
        self.assertIn("Tu carrito está vacío", self.http.get("/mi-carrito").get_data(as_text=True))

    def test_error_de_red_al_ver_el_carrito_conserva_los_datos(self):
        self.entrar("johnd")
        self.agregar(1, "2")
        self.cliente.caido.add("/products")
        r = self.http.get("/mi-carrito")
        self.assertEqual(r.status_code, 502)
        self.assertIn("Reintentar", r.get_data(as_text=True))
        self.assertEqual(self.guardado(), {"1": 2})

    def test_producto_que_desaparece_del_catalogo_se_retira(self):
        self.entrar("johnd")
        with self.http.session_transaction() as s:
            s["carrito"] = {"1": 1, "77": 4}
        html = self.http.get("/mi-carrito").get_data(as_text=True)
        self.assertIn("ya no están disponibles", html)
        self.assertEqual(self.guardado(), {"1": 1})

    def test_cookie_manipulada_no_rompe(self):
        self.entrar("johnd")
        with self.http.session_transaction() as s:
            s["carrito"] = {"x": "y", "1": 9999}
        self.assertEqual(self.http.get("/mi-carrito").status_code, 200)

    def test_logout_vacia_el_carrito(self):
        self.entrar("johnd")
        self.agregar(1)
        self.http.post("/logout", data={"csrf_token": self.token("/producto/1")})
        self.assertIsNone(self.guardado())


class TestPermisos(Base):
    def test_admin_y_auditor_sin_boton_ni_acceso(self):
        for u in ("mor_2314", "kevinryan"):
            self.setUp()
            self.entrar(u)
            html = self.http.get("/producto/1").get_data(as_text=True)
            self.assertNotIn("Agregar al carrito", html)
            self.assertNotIn("/mi-carrito", self.http.get("/catalogo").get_data(as_text=True))
            self.assertEqual(self.http.get("/mi-carrito").status_code, 403)
            self.assertEqual(self.agregar(1).status_code, 403)
            self.assertIsNone(self.guardado())

    def test_cliente_ve_boton_y_menu(self):
        self.entrar("johnd")
        self.assertIn("Agregar al carrito", self.http.get("/producto/1").get_data(as_text=True))
        self.assertIn('href="/mi-carrito"', self.http.get("/catalogo").get_data(as_text=True))

    def test_cliente_sigue_sin_usuarios_ni_historico(self):
        self.entrar("johnd")
        self.assertEqual(self.http.get("/usuarios").status_code, 403)
        self.assertEqual(self.http.get("/carritos").status_code, 403)

    def test_sin_sesion_y_sin_csrf(self):
        self.assertEqual(self.http.get("/mi-carrito").status_code, 302)
        self.assertEqual(self.http.post("/mi-carrito/agregar/1", data={"cantidad": "1"}).status_code, 400)
        self.entrar("johnd")
        self.assertEqual(self.http.post("/mi-carrito/agregar/1", data={"cantidad": "1"}).status_code, 400)

    def test_agregar_no_toca_el_historico_ni_la_api(self):
        """El histórico global (US12) sigue siendo de solo lectura: el carrito es local."""
        llamadas = []
        original = self.cliente.solicitar
        self.cliente.solicitar = lambda m, r, **k: (llamadas.append((m, r)), original(m, r, **k))[1]
        self.entrar("johnd")
        self.agregar(1)
        self.assertNotIn("POST", [m for m, r in llamadas if r != "/auth/login"])
        self.assertFalse([r for m, r in llamadas if r.startswith("/carts")])


if __name__ == "__main__":
    unittest.main()
