# Backend mínimo + DPIA

Hands-on de privacidad: un backend básico que recolecta datos personales
(nombres, apellidos, correo, teléfono) y su **DPIA** (Evaluación de Impacto
en Protección de Datos).

> El backend es deliberadamente simple. Tener problemas de privacidad es la
> idea: son el objeto de la DPIA. Las restricciones de diseño **se escriben,
> no se implementan**.

## Descripción del proyecto

Este proyecto simula una aplicación que recoge información personal sin
medidas de minimización, seguridad ni control de acceso. El objetivo es que
el análisis de la DPIA muestre los riesgos reales de tratamiento de datos
personales en un sistema poco seguro y con poca protección para el usuario.

La aplicación incluye:
- Un formulario frontend para registrar personas.
- Un backend Flask con endpoints para guardar y listar registros.
- Una base de datos SQLite que almacena los datos personales.
- Una evaluación de impacto en protección de datos documentada en `backend/DPIA.md`.

## Estructura del repositorio

| Archivo o carpeta | Descripción |
|---|---|
| `backend/app.py` | Backend Flask con `GET /` y `POST /registro`, además de `GET /usuarios` |
| `backend/schema.sql` | Definición de la tabla `usuarios` |
| `backend/requirements.txt` | Dependencias del proyecto |
| `backend/DPIA.md` | Documento de evaluación de impacto en protección de datos |
| `frontend/index.html` | Formulario web para registrar usuarios |
| `README.md` | Documentación del proyecto |

## Cómo correrlo

Desde la carpeta `backend`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

La aplicación queda disponible en:

- http://127.0.0.1:5000/

Si el puerto 5000 está ocupado, se puede ejecutar con:

```bash
PORT=5001 python app.py
```

## Probar la API

### Registrar un usuario

```bash
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"nombres":"Ana","apellidos":"Pérez","correo":"ana@example.com","telefono":"999111222"}'
```

### Listar usuarios

```bash
curl http://localhost:5000/usuarios
```

## Observaciones de privacidad

Este proyecto no implementa buenas prácticas de protección de datos como:
- minimización de datos
- cifrado de información sensible
- control de acceso
- eliminación segura de registros
- auditoría o trazabilidad
- consentimiento explícito y revocación

Es un caso intencionalmente débil para fines de análisis de DPIA.

## Integrantes

- María Fernanda Lazón Meza
- Christopher Renato Pérez Torres
- 