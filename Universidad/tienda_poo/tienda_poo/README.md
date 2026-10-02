# Tienda POO (Python 3.14.2 + Flask + Fake Store API)

Aplicación web hecha con Programación Orientada a Objetos. Cubre US01–US05.

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

## Mapa de historias de usuario

| US | Dónde |
|----|-------|
| US01 Login + perfil local | `servicio_autenticacion.py`, `auth_controller.py`, `login.html` |
| US02 Cerrar sesión | `AuthController.logout` (limpia toda la sesión) + cabecera `no-store` |
| US03 Catálogo (imagen, título, precio, loading, error + Reintentar) | `catalogo.js`, `catalogo.html`, `ServicioProductos.listar` |
| US04 Filtro por categoría (chips, Ver todos, limpia grilla, spinner) | `catalogo.js`, `ServicioProductos.categorias/por_categoria` |
| US05 Detalle por rol | `detalle.html` (botones solo se generan si es Administrador), `CatalogoController.detalle/editar/eliminar` |

## Estructura POO
```
app/
  models/     Rol, Producto, SesionUsuario
  services/   FakeStoreClient (HTTP), ServicioAutenticacion, ServicioProductos, excepciones
  web/        AuthController, CatalogoController, Seguridad (sesión, roles, CSRF)
```

## Notas
- Fake Store API **simula** editar/eliminar: responde OK pero no guarda cambios.
- Cambia `SECRET_KEY` con una variable de entorno si lo publicas.
