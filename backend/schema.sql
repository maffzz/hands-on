CREATE TABLE IF NOT EXISTS usuarios (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres   TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    correo    TEXT NOT NULL,
    telefono  TEXT,
    creado_en TEXT DEFAULT CURRENT_TIMESTAMP
);
