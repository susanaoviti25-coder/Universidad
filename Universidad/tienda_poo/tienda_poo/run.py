"""Punto de entrada: python run.py  ->  http://127.0.0.1:8000"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "8000")),
        debug=True,
        use_reloader=False,  # evita doble proceso al depurar en VS Code
    )
