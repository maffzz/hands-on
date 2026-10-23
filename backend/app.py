"""Backend mínimo de recolección de datos personales.

Intencionalmente simple: la idea es que tenga problemas de privacidad,
que se analizan en DPIA.md. Las restricciones de diseño se ESCRIBEN
en la DPIA, no se implementan aquí.
"""
import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DB_PATH = BASE_DIR / "backend" / "usuarios.db"
PORT = int(os.environ.get("PORT", "5000"))

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with open("schema.sql", encoding="utf-8") as f:
        conn = get_db()
        conn.executescript(f.read())
        conn.commit()
        conn.close()


@app.post("/registro")
def registro():
    data = request.get_json(silent=True) or {}
    campos = ["nombres", "apellidos", "correo", "telefono"]
    faltan = [c for c in campos if not data.get(c)]
    if faltan:
        return jsonify({"error": f"Faltan campos: {', '.join(faltan)}"}), 400

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO usuarios (nombres, apellidos, correo, telefono) VALUES (?, ?, ?, ?)",
        (data["nombres"], data["apellidos"], data["correo"], data["telefono"]),
    )
    conn.commit()
    nuevo_id = cur.lastrowid
    conn.close()
    return jsonify({"id": nuevo_id, "mensaje": "Registrado"}), 201


@app.get("/usuarios")
def listado():
    conn = get_db()
    filas = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return jsonify([dict(f) for f in filas])


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=PORT, debug=True)
