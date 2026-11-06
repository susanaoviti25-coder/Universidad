# Tienda POO (Python 3.14.2 + Flask + Fake Store API)

Aplicación web hecha con Programación Orientada a Objetos. Cubre US01–US05, **US11 y US12** y el **carrito de compra**.

## Cómo ejecutarla en Visual Studio Code

1. Descomprime el zip y abre la carpeta `tienda_poo` en VS Code (**Archivo > Abrir carpeta**).
2. Abre una terminal (**Ctrl+ñ**) y crea el entorno virtual con Python 3.14.2:

   **Windows (PowerShell)**
   ```powershell
   py -3.14 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   **macOS / Linux**
   ```bash
   python3.14 -m venv .venv
   source .venv/bin/activate
   ```
3. Instala dependencias y ejecuta:
   ```bash
   pip install -r requirements.txt
   python run.py
   ```
4. Abre http://127.0.0.1:8000
   (o pulsa **F5** con la configuración "Tienda POO (Flask)").

Si VS Code pregunta por el intérprete: `Ctrl+Shift+P` > *Python: Select Interpreter* > `.venv`.

## Usuarios de prueba (Fake Store API) y perfil local

| Usuario     | Contraseña  | Perfil asignado localmente |
|-------------|-------------|----------------------------|
| `mor_2314`  | `83r5^_`    | Administrador              |
| `johnd`     | `m38rmF$`   | Cliente                    |
| `kevinryan` | `kev02937@` | Auditor                    |

La asignación vive en `app/config.py` (`PERFILES_LOCALES`).

## Pruebas (no necesitan internet)
```bash
python -m unittest discover -s tests -v
```
(47 pruebas: US01–US05, US11/US12 en `tests/test_auditoria.py` y el carrito en `tests/test_compra.py`.)

## Mapa de historias de usuario

| US | Dónde |
|----|-------|
| US01 Login + perfil local | `servicio_autenticacion.py`, `auth_controller.py`, `login.html` |
| US02 Cerrar sesión | `AuthController.logout` (limpia toda la sesión) + cabecera `no-store` |
| US03 Catálogo (imagen, título, precio, loading, error + Reintentar) | `catalogo.js`, `catalogo.html`, `ServicioProductos.listar` |
| US04 Filtro por categoría (chips, Ver todos, limpia grilla, spinner) | `catalogo.js`, `ServicioProductos.categorias/por_categoria` |
| US05 Detalle por rol | `detalle.html` (botones solo se generan si es Administrador), `CatalogoController.detalle/editar/eliminar` |
| US11 Listar usuarios (solo Administrador/Auditor) | `servicio_usuarios.py`, `usuarios_controller.py`, `usuarios.html`, `usuarios.js`, `models/usuario.py` |
| US12 Histórico global de carritos (solo Administrador/Auditor) | `servicio_carritos.py`, `carritos_controller.py`, `carritos.html`, `carritos.js`, `models/carrito.py` |

## Estructura POO
```
app/
  models/     Rol, Producto, SesionUsuario, Usuario (+Direccion, Geolocalizacion), Carrito (+ItemCarrito)
  services/   FakeStoreClient (HTTP), ServicioAutenticacion, ServicioProductos,
              ServicioUsuarios (US11), ServicioCarritos (US12), excepciones
  web/        AuthController, CatalogoController, UsuariosController, CarritosController,
              Seguridad (sesión, roles, CSRF, ROLES_AUDITORIA)
```

## US11 y US12 (auditoría)

| Ruta | Qué hace | Quién entra |
|------|----------|-------------|
| `/usuarios` y `/api/usuarios` | Directorio: nombre completo, correo, teléfono y usuario; clic en la fila para ver dirección y coordenadas | Administrador, Auditor |
| `/carritos` y `/api/carritos` | Carritos con ID, fecha y usuario; clic para ver artículos (ID, título real y cantidad) | Administrador, Auditor |

- **Cliente:** el menú *Usuarios / Carritos* no se genera en el HTML, y entrar por URL directa o por la API devuelve **403** (sin consultar la Fake Store API).
- **Solo lectura:** solo existen rutas `GET`; cualquier otro método devuelve 405 y no hay botones de editar/eliminar.
- **Reto lógico (US12):** `ServicioCarritos` cruza cada `productId` con `GET /products` para mostrar el título. Si el catálogo falla se muestran los IDs con un aviso.
- **Anidados sin caídas (US11):** `Usuario → Direccion → Geolocalizacion` toleran `null`, campos ausentes o tipos inesperados. El campo `password` de la API **no se guarda ni se muestra**.
- **Carga y error:** indicador de carga, panel de error con **Reintentar** y búsqueda en vivo en usuarios.
- Con los usuarios de prueba: `kevinryan` (Auditor) y `mor_2314` (Administrador) ven las dos secciones; `johnd` (Cliente) no.

## Carrito de compra (solo Cliente)

| Ruta | Qué hace |
|------|----------|
| Botón **Agregar al carrito** en `/producto/<id>` | Agrega N unidades (1–99). Valida que el producto exista antes de agregarlo |
| `/mi-carrito` | Lista productos, precio, cantidad, subtotal y **total**; cambiar cantidad, quitar y vaciar |

- **Quién:** solo el rol **Cliente** (`ROLES_COMPRA` en `seguridad.py`). Para Administrador/Auditor el botón y el menú ni se generan en el HTML, y las rutas devuelven 403.
- **Dónde se guarda:** en la sesión local (cookie firmada, solo `id → cantidad`). Los precios se leen del catálogo al mostrar el carrito. Al cerrar sesión el carrito se borra.
- **Fake Store API no guarda carritos**, por eso no se envía nada a `/carts`. El histórico global de la US12 sigue siendo de solo lectura y no incluye estos carritos.
- Archivos: `models/carrito_compra.py`, `services/servicio_compra.py`, `web/compra_controller.py`, `templates/mi_carrito.html`.
- No incluye "pagar / finalizar compra" (no está en las historias).

## Notas
- Fake Store API **simula** editar/eliminar: responde OK pero no guarda cambios.
- Cambia `SECRET_KEY` con una variable de entorno si lo publicas.
