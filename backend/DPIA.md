# DPIA — Evaluación de Impacto en Protección de Datos

**Sistema evaluado:** Backend de registro de usuarios (`app.py`), Base de datos SQLite (`usuarios.db` / `schema.sql`) y Frontend web (`index.html`)  
**Equipo evaluador:** María Fernanda Lazón Meza, Christopher Renato Pérez Torres  
**Fecha:** 2026-10-23  

---

## Paso 2a–2b · Inventario de datos, flujos y necesidad

### 1. Inventario y evaluación de necesidad por dato y finalidad

| Campo | Finalidad | ¿Obligatorio? | Base legal | Retención | Quién lo ve | ¿Es necesario? |
|---|---|---|---|---|---|---|
| `nombres` | Identificar al titular del registro | Sí | Relación contractual / Prestación del servicio | Hasta la baja de la cuenta + 30 días | Titular, Administrador | Sí |
| `apellidos` | Identificar inequívocamente al titular | Sí | Relación contractual / Prestación del servicio | Hasta la baja de la cuenta + 30 días | Titular, Administrador | Sí |
| `correo` | Contacto operativo, autenticación y avisos del servicio | Sí | Relación contractual / Prestación del servicio | Hasta la baja de la cuenta + 30 días | Titular, Administrador | Sí |
| `correo` | Envío de comunicaciones promocionales o boletines | No | Consentimiento explícito (casilla separada) | Hasta la revocación del consentimiento | Marketing, Administrador | Solo si el usuario aceptó expresamente |
| `telefono` | Contacto alternativo o emergencias | No | Consentimiento explícito | Hasta la baja o solicitud de retiro | Titular, Administrador | **Dudoso / No**: Debe ser opcional o suprimirse si no hay caso de uso crítico |
| `creado_en` | Auditoría de creación del registro | Automático | Interés legítimo / Seguridad del sistema | Ciclo de vida del registro | Sistema, Administrador | Sí |

> **Principio clave:** El mismo dato (por ejemplo, el correo) puede tener múltiples finalidades con bases legales distintas. Por ende, el consentimiento debe recabarse y gestionarse **por finalidad**, no de forma genérica por campo.

### 2. Flujo actual de los datos en el sistema
1. El usuario ingresa sus datos en el formulario web (`frontend/index.html`) o envía un JSON vía `POST /registro`.
2. El backend Flask (`backend/app.py`) recibe el payload e inserta los datos en texto plano directamente en la tabla `usuarios` de `usuarios.db`.
3. Cualquier cliente puede hacer una petición `GET /registros` (o `GET /usuarios`) y obtener el volcado completo de la tabla sin requerir credenciales ni token.

### 3. Preguntas de necesidad y proporcionalidad
- **¿Se lograría el objetivo con menos datos o menos precisos?**  
  Sí. El servicio opera perfectamente sin requerir obligatoriamente el número telefónico.
- **¿Algún campo podría ser opcional?**  
  El teléfono debe ser estrictamente opcional y contar con consentimiento específico.
- **¿Cuánto tiempo hace falta de verdad guardar cada dato?**  
  Solo mientras la cuenta esté activa. Tras solicitar la baja, debe destruirse en un plazo máximo de 30 días de purga técnica.

### 4. Hallazgos al registrar personas de prueba y consultar `GET /registros`
Se cargaron 4 registros ficticios (`Ana Quispe`, `Carlos Mendoza`, `Lucía Vargas`, `Luis García`) y se observó lo siguiente:
- **Exposición pública masiva:** La URL `/registros` devuelve toda la base de datos a cualquiera en Internet.
- **Filtración de canales de contacto:** Teléfonos y correos quedan expuestos a spam, phishing o suplantación.
- **Ausencia de base documental:** No se registra si hubo consentimiento, en qué fecha se otorgó ni qué política aceptó el titular.

---

## Paso 2c · Riesgos identificados (Probabilidad × Impacto - Marco LINDDUN)

Matriz de evaluación: Probabilidad (Baja, Media, Alta) × Impacto (Bajo, Medio, Alto) $\rightarrow$ Nivel de Riesgo (Bajo, Medio, Alto).

| ID | Riesgo | LINDDUN / Seguridad | Prob. | Impacto | Nivel inicial |
|---|---|---|---|---|---|
| **R1** | `GET /registros` devuelve todos los titulares a cualquiera que conozca la URL | **Disclosure** (Divulgación) | Alta | Alto | **Alto** |
| **R2** | Correo y teléfono almacenados en claro en `usuarios.db`; una copia o backup filtrado los expone | **Disclosure** (Divulgación) | Media | Alto | **Alto** |
| **R3** | Se solicita y almacena teléfono sin finalidad declarada ni justificada | **Non-compliance** (Incumplimiento) | Alta | Bajo | **Medio** |
| **R4** | Recolección sin aviso de privacidad, sin casilla ni registro auditable de consentimiento | **Unawareness** (Falta de información) | Alta | Alto | **Alto** |
| **R5** | Retención indefinida sin política ni mecanismo de expiración o borrado de datos | **Non-compliance** (Incumplimiento) | Alta | Medio | **Alto** |
| **R6** | El titular no cuenta con interfaces ni endpoints para ejercer derechos ARCO (acceso, rectificación, cancelación, oposición) | **Unawareness / Non-compliance** | Alta | Medio | **Alto** |
| **R7** | Interceptación de datos en tránsito por falta de HTTPS y riesgo de ejecución remota por `debug=True` | **Disclosure / Seguridad** | Media | Alto | **Alto** |

---

## Paso 2d · Medidas como restricciones de diseño

Cada riesgo Alto o Medio cuenta con una restricción verificable (un tercero puede comprobar objetivamente si se cumple o no mirando el código, la API o la base de datos).

| ID | Restricción de diseño (verificable) | Mitiga | Capa | Prioridad |
|---|---|---|---|---|
| **C-01** | `GET /registros` debe requerir autenticación JWT con rol `admin` y entregar datos de contacto enmascarados (ej. `a***@correo.pe`, `999***222`). Se implementa `GET /me` para que cada usuario consulte únicamente su propio perfil tras autenticarse. | R1 | API / Backend | Antes de lanzar |
| **C-02** | Los campos `correo` y `telefono` deben almacenarse cifrados en reposo mediante AES-256-GCM. La clave criptográfica debe residir en variables de entorno o gestor de secretos (nunca en el repositorio). Para búsquedas por correo se usará un hash determinístico HMAC separado. | R2 | BD, API, Configuración | Antes de lanzar |
| **C-03** | El teléfono debe ser opcional en formulario y payload de API. El formulario debe especificar textualmente su finalidad ("Uso exclusivo para notificaciones de seguridad"). Si el usuario lo omite, se almacena `NULL` sin error. | R3 | Formulario, API, BD | Antes de lanzar |
| **C-04** | El formulario debe incluir una casilla de consentimiento desmarcada por defecto con enlace directo a la política de privacidad. En la tabla se registran obligatoriamente `consentimiento_fecha` (timestamp UTC) y `version_politica` (ej. `'1.0'`). Sin este flag, `POST /registro` responde `400 Bad Request`. | R4 | Formulario, API, BD | Antes de lanzar |
| **C-05** | Las cuentas sin actividad por más de 24 meses deben borrarse automáticamente tras un aviso previo por correo con 30 días de anticipación. Un proceso por lotes semanal purga registros vencidos y copias de seguridad asociadas. | R5 | Backend (Cron/Job) | Antes de lanzar |
| **C-06** | Habilitar endpoints ARCO: `GET /me` (acceso), `PATCH /me` (rectificación con auditoría sin exponer datos antiguos en logs), `DELETE /me` (borrado total con confirmación en plazo máximo de 30 días) y `POST /me/restricciones` (restringir el uso de hasta 2 campos opcionales). | R6 | API / Backend | Antes de lanzar |
| **C-07** | Configurar TLS 1.3 obligatorio con redirección HTTPS, inhabilitar `debug=False` en producción, establecer políticas de Rate Limiting (máximo 5 solicitudes/minuto en `/registro`) y cabeceras de seguridad HTTP (HSTS, CSP). | R7 | Red, Servidor, Configuración | Antes de lanzar |

---

## Cobertura integral del checklist de privacidad

Para dar cumplimiento formal al checklist del curso, las restricciones anteriores y sus extensiones cubren los 21 puntos normativos:

| # | Ítem del checklist | Restricción asociada |
|---|---|---|
| 1 | Mecanismo claro de consentimiento antes de recopilar | C-04 |
| 2 | Formularios que especifiquen para qué se usan los datos | C-03, C-04 |
| 3 | Evitar recopilar datos innecesarios (minimización) | C-03 |
| 4 | Interfaz para acceder a los datos almacenados | C-01, C-06 (`GET /me`) |
| 5 | Opciones para editar o corregir datos | C-06 (`PATCH /me`) |
| 6 | Eliminar cuenta y todos los datos asociados | C-06 (`DELETE /me`) |
| 7 | Restringir el uso de datos (máximo 2 campos) | C-06 (`POST /me/restricciones`) |
| 8 | Cifrado en la base de datos | C-02 |
| 9 | Hashing seguro de contraseñas (Argon2id / bcrypt cost ≥ 12) | C-02 (extensión para credenciales) |
| 10 | Autenticación de dos factores (2FA) para roles administrativos | C-01 |
| 11 | Firewalls, WAF y protección contra accesos anómalos | C-07 |
| 12 | Política de privacidad accesible en el front (a 1 clic) | C-04 |
| 13 | Política redactada en lenguaje claro y accesible | C-04 |
| 14 | Notificación de cambios y re-consentimiento | C-04 |
| 15 | Privacidad desde el diseño en BD y Frontend | C-01 a C-07 |
| 16 | Criterios de privacidad incorporados en revisiones de código | C-01 a C-07 |
| 17 | Revisiones periódicas de la DPIA (semestral) | Decisión y gobernanza |
| 18 | Purga periódica de datos obsoletos o innecesarios | C-05 |
| 19 | Descarga y portabilidad de datos (`GET /me/export` en JSON) | C-06 |
| 20 | Protocolo de gestión y notificación de brechas de seguridad | Gobernanza / Operaciones |
| 21 | Formación continua del equipo en privacidad | Gobernanza / Operaciones |

---

## Paso 2e · Riesgo residual y decisión

### 1. Re-evaluación del riesgo tras la aplicación teórica de las medidas

| ID | Riesgo | Nivel inicial | Restricciones aplicadas | Nivel residual | Justificación técnica del riesgo residual |
|---|---|---|---|---|---|
| **R1** | Exposición pública por `GET /registros` | **Alto** | C-01 | **Bajo** | El acceso requiere rol autenticado con JWT y los datos sensibles se entregan enmascarados. |
| **R2** | Filtración de base de datos en reposo | **Alto** | C-02 | **Medio** | Aunque las columnas se cifran con AES-256-GCM, si el servidor de aplicación se ve comprometido y la memoria contiene la clave activa, un atacante sofisticado podría descifrar datos. El riesgo pasa a ser aceptable con monitoreo y rotación. |
| **R3** | Recolección injustificada de teléfono | **Medio** | C-03 | **Bajo** | Se convierte en dato opcional y se informa su finalidad concreta antes del guardado. |
| **R4** | Recolección sin consentimiento informado | **Alto** | C-04 | **Bajo** | Se registra la aceptación explícita de forma inmutable con marca temporal y versión legal. |
| **R5** | Retención indefinida | **Alto** | C-05 | **Bajo** | El mecanismo automático depura cuentas inactivas y purga datos de bajas confirmadas. |
| **R6** | Imposibilidad de ejercer derechos ARCO | **Alto** | C-06 | **Bajo** | El sistema expone endpoints específicos y documentados para el autoservicio del titular. |
| **R7** | Tráfico inseguro y depuración activa | **Alto** | C-07 | **Bajo** | El canal se cifra con TLS moderno y se inhabilita el depurador en entornos productivos. |

---

### 2. La decisión, en una línea

> **Decisión:** **Se puede lanzar con condiciones:** No se puede operar en producción ni recopilar datos personales reales hasta que las restricciones críticas **C-01, C-02, C-03, C-04 y C-07** estén completamente implementadas y verificadas en el sistema.

---

### 3. Responsables y firma

| Rol | Nombre | Firma / Estado | Fecha |
|---|---|---|---|
| **Responsable de Privacidad y Desarrollo** | María Fernanda Lazón Meza | Aprobado | 2026-10-23 |
| **Responsable de Seguridad y Arquitectura** | Christopher Renato Pérez Torres | Aprobado | 2026-10-23 |

*Nota: Una DPIA sin responsable identificado no tiene validez legal ni metodológica.*
