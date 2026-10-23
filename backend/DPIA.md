# DPIA — Backend de registro de usuarios

**Fecha:** 2026-10-23  
**Sistema evaluado:** `app.py` + `schema.sql` (Flask + SQLite)

---

## 1. Inventario de datos

| Dato | Tabla.columna | Tipo | Identifica directamente | Quién accede hoy | Dónde se almacena |
|---|---|---|---|---|---|
| Nombres | `usuarios.nombres` | Dato personal | Sí (junto con apellidos) | Cualquiera con acceso al API/DB | SQLite, texto plano |
| Apellidos | `usuarios.apellidos` | Dato personal | Sí (junto con nombres) | Cualquiera con acceso al API/DB | SQLite, texto plano |
| Correo | `usuarios.correo` | Dato personal | Sí | Cualquiera con acceso al API/DB | SQLite, texto plano |
| Teléfono | `usuarios.telefono` | Dato personal | Sí | Cualquiera con acceso al API/DB | SQLite, texto plano |

**Flujo:** el cliente envía los datos por `POST /registro` → se insertan en `usuarios` → `GET /usuarios` devuelve todos los registros sin autenticación.

**Hechos observables del backend actual:**
- No hay captura de consentimiento ni de finalidad.
- No hay autenticación ni autorización en ningún endpoint.
- `GET /usuarios` expone todos los datos de todos los usuarios.
- Los datos se guardan en texto plano; no hay cifrado, retención ni borrado.
- No hay endpoints para consultar, corregir ni eliminar datos propios.
- No hay validación de formato de correo o teléfono.
- El servidor corre con `debug=True` y sin HTTPS.

---

## 2. Necesidad y proporcionalidad

| Dato | Finalidad plausible | ¿Estrictamente necesario? | Comentario |
|---|---|---|---|
| Nombres / apellidos | Identificar a la persona registrada | Sí | Mínimo para identificar |
| Correo | Contacto y/o login | Sí | Mantener; es el identificador natural |
| Teléfono | Contacto alternativo | **Dudoso** | Solo si existe una finalidad concreta; si no, eliminarlo (minimización) |

**Conclusión:** el tratamiento es proporcional solo si se declara una finalidad explícita. El teléfono debería ser opcional o no recolectarse si no tiene un uso definido.

---

## 3. Riesgos identificados

Escala: Probabilidad (P) y Severidad (S) en Baja / Media / Alta.

| # | Riesgo | Causa en el backend | P | S | Nivel |
|---|---|---|---|---|---|
| R1 | Acceso no autorizado a todos los datos personales | `GET /usuarios` sin autenticación | Alta | Alta | **Crítico** |
| R2 | Recolección sin base legal ni consentimiento | `POST /registro` no pide ni registra consentimiento | Alta | Alta | **Crítico** |
| R3 | Filtración de datos si se roba la DB | Texto plano, sin cifrado | Media | Alta | **Alto** |
| R4 | Usuario no puede ejercer sus derechos (acceso, rectificación, eliminación) | No existen endpoints | Alta | Media | **Alto** |
| R5 | Uso de datos para fines no informados | No hay finalidad declarada ni política | Media | Alta | **Alto** |
| R6 | Retención indefinida de datos | No hay política ni mecanismo de borrado | Alta | Media | **Alto** |
| R7 | Interceptación en tránsito | Sin HTTPS / `debug=True` expone el debugger | Media | Alta | **Alto** |
| R8 | Datos innecesarios o inválidos | Teléfono obligatorio sin justificación; sin validación | Media | Baja | Medio |
| R9 | Respuesta tardía o nula ante una brecha | No hay protocolo | Media | Alta | **Alto** |
| R10 | Equipo sin criterios de privacidad | Sin formación ni revisiones | Media | Media | Medio |

---

## 4. Restricciones de diseño

> Estas restricciones **se escriben, no se implementan**. Son requisitos que un rediseño del backend tendría que cumplir. Cada una está vinculada al riesgo que mitiga y al ítem del checklist.

### 4.1 Consentimiento y recopilación de datos

| ID | Restricción | Mitiga |
|---|---|---|
| RD-01 | El registro debe exigir un campo `consentimiento: true` explícito, no pre-marcado. Se guarda `consentimiento_fecha` y `version_politica` en la DB. Sin consentimiento, el endpoint responde 400 y no inserta nada. | R2 |
| RD-02 | El formulario de registro debe mostrar, junto a cada campo, para qué se usará (ej.: "Correo: para iniciar sesión y avisarte cambios en la política"). La finalidad también se versiona. | R2, R5 |
| RD-03 | Solo se recolectan datos estrictamente necesarios. El teléfono pasa a ser opcional y se elimina si no hay finalidad definida. Se rechazan campos extra en el payload. | R8 |

### 4.2 Acceso y control sobre los datos personales

| ID | Restricción | Mitiga |
|---|---|---|
| RD-04 | `GET /me` devuelve únicamente los datos del usuario autenticado. `GET /usuarios` (listado completo) se elimina o se restringe a un rol administrador con 2FA. | R1, R4 |
| RD-05 | `PATCH /me` permite al usuario corregir nombres, apellidos, correo y teléfono, con validación de formato. Cada cambio queda auditado (quién, cuándo, qué campo, sin guardar el valor antiguo en logs). | R4 |
| RD-06 | `DELETE /me` elimina la cuenta y todos los datos asociados (tabla principal, copias, logs con datos personales) en un plazo máximo definido (ej.: 30 días) y confirma la eliminación al usuario. | R4, R6 |
| RD-07 | `POST /me/restricciones` permite al usuario restringir el uso de **como máximo 2 datos** (ej.: teléfono y apellidos). Un dato restringido se conserva pero no se usa para ninguna finalidad ni se muestra en listados, salvo obligación legal. Se guarda en una columna `restringidos` (lista de máximo 2 campos); el backend rechaza más de 2. | R4, R5 |

### 4.3 Seguridad de datos y protección

| ID | Restricción | Mitiga |
|---|---|---|
| RD-08 | Cifrado en reposo: la base de datos debe estar cifrada (SQLCipher o cifrado de disco/gestionado en un motor tipo PostgreSQL). Las columnas `correo` y `telefono` se cifran a nivel de aplicación; para buscar por correo se usa un hash determinístico (HMAC) separado. Las claves viven fuera del repo (variables de entorno / gestor de secretos). | R3 |
| RD-09 | Si se añaden contraseñas: hash con Argon2id (o bcrypt con cost ≥ 12), con salt único por usuario. Nunca se guardan ni se registran en texto plano. | R3 |
| RD-10 | 2FA (TOTP) obligatoria para cuentas administrativas y para cualquier cuenta con acceso a datos de otros usuarios. | R1 |
| RD-11 | HTTPS obligatorio (TLS 1.2+), `debug=False` en producción, WAF/firewall delante del backend, rate limiting en `/registro` y login, y alertas por intentos repetidos o accesos anómalos. | R1, R7 |

### 4.4 Transparencia y políticas de privacidad

| ID | Restricción | Mitiga |
|---|---|---|
| RD-12 | El front debe tener un enlace "Política de privacidad" visible en el pie de todas las páginas y en el formulario de registro (máximo 1 clic). | R2, R5 |
| RD-13 | La política debe estar en lenguaje sencillo (sin jerga legal innecesaria), con resumen corto al inicio: qué datos, para qué, cuánto tiempo, con quién se comparten, cómo ejercer derechos. | R5 |
| RD-14 | Todo cambio en la política se versiona, se notifica por correo a los usuarios con anticipación razonable (ej.: 15 días) y, si el cambio amplía finalidades, se pide nuevo consentimiento. | R2, R5 |

### 4.5 Integración de privacidad en el diseño

| ID | Restricción | Mitiga |
|---|---|---|
| RD-15 | Privacidad desde el diseño: el modelo de datos y el front se definen con la DPIA, antes de implementar. Todo campo nuevo requiere justificar finalidad y base legal. | R2, R8 |
| RD-16 | Toda decisión de diseño o funcionalidad nueva pasa por una lista de verificación de privacidad (¿qué dato nuevo?, ¿para qué?, ¿cuánto se retiene?, ¿quién accede?) en el pull request. | R5, R10 |
| RD-17 | Revisión periódica de privacidad (ej.: cada 6 meses y ante cambios mayores): actualizar esta DPIA, revisar accesos y verificar que se cumplen las restricciones. | R10 |
| RD-18 | Retención limitada: los datos se eliminan automáticamente tras un plazo definido (ej.: cuentas inactivas por 24 meses, previo aviso). Un job programado purga registros vencidos, incluidas copias de seguridad según su ciclo de rotación. | R6 |

### 4.6 Extras

| ID | Restricción | Mitiga |
|---|---|---|
| RD-19 | `GET /me/export` permite descargar todos los datos del usuario en formato legible y portable (JSON o CSV), previa reautenticación. | R4 |
| RD-20 | Protocolo de brechas: responsable designado, canal de reporte interno, evaluación en menos de 24 h, notificación a las personas afectadas y a la autoridad de protección de datos en el plazo legal (en Perú, la Autoridad Nacional de Protección de Datos Personales), y registro del incidente con lecciones aprendidas. | R9 |
| RD-21 | Formación del equipo en privacidad y seguridad: inducción para nuevos integrantes y refresco periódico (ej.: anual), con registro de asistencia. | R10 |

---

## 5. Cobertura del checklist

| Ítem del checklist | Restricción |
|---|---|
| Mecanismo claro de consentimiento antes de recopilar | RD-01 |
| Formularios que especifiquen para qué se usan los datos | RD-02 |
| Evitar recopilar datos innecesarios | RD-03 |
| Interfaz para acceder a los datos almacenados | RD-04 |
| Opciones para editar o corregir datos | RD-05 |
| Eliminar cuenta y todos los datos asociados | RD-06 |
| Restringir el uso de datos (máximo 2) | RD-07 |
| Cifrado en la base de datos | RD-08 |
| Hashing seguro de contraseñas | RD-09 |
| Autenticación de dos factores para cuentas sensibles/administrativas | RD-10 |
| Firewalls o protección contra intrusos | RD-11 |
| Política de privacidad accesible en el front | RD-12 |
| Política clara y fácil de entender | RD-13 |
| Informar cambios en la política | RD-14 |
| Privacidad desde la fase inicial de BD y front | RD-15 |
| Privacidad en todas las decisiones de diseño | RD-16 |
| Revisiones periódicas de privacidad | RD-17 |
| Eliminar datos antiguos o innecesarios | RD-18 |
| Descarga de todos los datos en formato legible | RD-19 |
| Protocolos ante brechas de seguridad | RD-20 |
| Formación continua del equipo | RD-21 |

---

## 6. Riesgo residual y decisión

Si se cumplen RD-01 a RD-21, los riesgos críticos (R1, R2) bajan a **Bajo/Medio** y los altos (R3–R7, R9) a **Medio/Bajo**.

**Decisión:** el backend actual **no debe usarse en producción ni con datos reales**. Solo es válido como prototipo de aprendizaje. Para pasar a producción hay que implementar, como mínimo, RD-01, RD-04, RD-08, RD-11 y RD-12, y volver a evaluar esta DPIA.

| Rol | Nombre | Fecha |
|---|---|---|
| Elaborado por | Mafer Lazón | 2026-10-23 |
