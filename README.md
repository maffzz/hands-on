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
| `backend/app.py` | Backend Flask con `GET /`, `POST /registro`, y endpoints de listado `GET /registros` / `GET /usuarios` |
| `backend/schema.sql` | Definición de la tabla `usuarios` |
| `backend/requirements.txt` | Dependencias del proyecto |
| `backend/DPIA.md` | Documento de evaluación de impacto en protección de datos (DPIA) |
| `frontend/index.html` | Formulario web para registrar usuarios |
| `README.md` | Documentación del proyecto |

## Cómo correrlo

Desde la raíz o desde la carpeta `backend`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py
```

La aplicación queda disponible en:

- http://127.0.0.1:5000/

Si el puerto 5000 está ocupado, se puede ejecutar con:

```bash
PORT=5001 python backend/app.py
```

## Probar la API

### Registrar un usuario (POST /registro)

Ejemplo con teléfono:
```bash
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"nombres":"Ana","apellidos":"Pérez","correo":"ana@example.com","telefono":"999111222"}'
```

Ejemplo con teléfono opcional (ejemplo de la diapositiva):
```bash
curl -X POST http://localhost:5000/registro \
  -H "Content-Type: application/json" \
  -d '{"nombres":"Ana","apellidos":"Quispe","correo":"ana@correo.pe"}'
```

### Listar registros (GET /registros o GET /usuarios)

```bash
curl http://localhost:5000/registros
```

## Datos de prueba y hallazgos iniciales (Paso 1)

Antes de redactar la DPIA, se insertaron 4 personas inventadas (`Ana Quispe`, `Carlos Mendoza`, `Lucía Vargas`, `Luis García`) y se consultó `GET /registros`. Lo que resultó problemático/incómodo:
1. **Acceso público y sin barreras:** Cualquier persona puede ver todos los registros sin requerir login ni roles.
2. **Exposición de datos de contacto:** Celulares y correos personales quedan al descubierto.
3. **Sin trazabilidad de consentimiento:** No se sabe para qué se recogió la información ni si el titular aceptó una política.
4. **Almacenamiento plano:** La base de datos guarda todo sin cifrado ni minimización.

## Observaciones de privacidad y DPIA

Este proyecto no implementa deliberadamente buenas prácticas de protección de datos:
- minimización de datos
- cifrado de información sensible
- control de acceso
- eliminación segura de registros
- auditoría o trazabilidad
- consentimiento explícito y revocación

Todo el análisis de riesgos y las restricciones de diseño para subsanarlo se detallan en [backend/DPIA.md](backend/DPIA.md).

## Paso 3 y 4: Revisión Cruzada

| Sección | Detalle |
|---|---|
| **Grupo revisado** | Grupo X (completar al realizar la revisión) |
| **Revisión recibida de** | Grupo Y (pegar comentarios recibidos del otro grupo aquí) |
| **Estado de entrega** | Repositorio + DPIA + Revisión lista para entrega |

## Integrantes

- María Fernanda Lazón Meza
- Christopher Renato Pérez Torres 