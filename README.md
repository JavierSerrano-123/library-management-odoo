# 📚 Library Management — Odoo 19 Module

Módulo desarrollado para la gestión integral de bibliotecas sobre **Odoo 19 Community Edition**.  
Cubre socios, catálogo de libros, préstamos, automatizaciones, seguridad por roles, portal web, integración con POS y API REST.

---

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Levantar el entorno](#levantar-el-entorno)
- [Instalación del módulo](#instalación-del-módulo)
- [Funcionalidades implementadas](#funcionalidades-implementadas)
- [Usuarios de prueba](#usuarios-de-prueba)
- [API REST](#api-rest)
- [Casos de prueba](#casos-de-prueba)
- [Capturas](#capturas)
- [Decisiones técnicas](#decisiones-técnicas)
- [Limitaciones conocidas](#limitaciones-conocidas)
- [Estructura del módulo](#estructura-del-módulo)

---

## Requisitos

- Python 3.12+
- PostgreSQL 15+
- Git

---

## Levantar el entorno

```bash
# 1. Clonar Odoo 19
git clone https://github.com/odoo/odoo.git --branch 19.0 --depth 1

# 2. Clonar el módulo dentro de addons
cd odoo/addons
git clone https://github.com/JavierSerrano-123/library-management-odoo.git library_management

# 3. Crear entorno virtual e instalar dependencias
cd ../..
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r odoo/requirements.txt

# 4. Crear base de datos
createdb odoo19

# 5. Lanzar Odoo
python odoo/odoo-bin ^
  --addons-path=odoo/addons ^
  --db_host=localhost ^
  --db_user=TU_USUARIO_POSTGRES ^
  --db_password=TU_PASSWORD_POSTGRES ^
  -d odoo19 ^
  --without-demo=all
```

Odoo quedará disponible en `http://localhost:8069`.

---

## Instalación del módulo

1. Acceder a `http://localhost:8069` e iniciar sesión como administrador.
2. Ir a **Settings → Activate developer mode**.
3. Ir a **Apps → Update Apps List**.
4. Buscar **"Library Management"** e instalar.

Para actualizar el módulo tras cambios en el código:

```bash
python odoo/odoo-bin -d odoo19 -u library_management --stop-after-init ^
  --db_host=localhost ^
  --db_user=TU_USUARIO_POSTGRES ^
  --db_password=TU_PASSWORD_POSTGRES
```

---

## Funcionalidades implementadas

### 1. Módulo principal
Aplicación instalable registrada como `library_management`, visible en el menú principal de Odoo con ícono propio.

### 2. Gestión de socios (`library.member`)
- Extensión del modelo `res.partner` para identificar socios de biblioteca mediante el campo `is_library_member`.
- Código de socio único generado automáticamente mediante una secuencia Odoo (`library.member.code`) al crear o al activar el campo en un contacto existente.
- El código es inmutable y se muestra en la ficha del contacto.

### 3. Catálogo de libros (`library.book`)
- Campos: título, autor, ISBN, fecha de publicación, disponibilidad, producto POS vinculado.
- Campo calculado **"Años desde publicación"** computado automáticamente desde `publication_date`.
- Filtros en listado: Disponibles, No disponibles.
- Búsqueda por autor e ISBN.

### 4. Préstamo y devolución (`library.loan`)
- Proceso creado desde **Biblioteca → Préstamos → Nuevo**.
- Validaciones en backend (no omisibles):
  - El libro debe estar en estado **"Disponible"**.
  - El socio no puede tener más de **5 préstamos activos** simultáneos.
- Registro manual de devolución mediante botón **"Marcar Devuelto"**: libera el cupo del socio y cambia el estado del libro a "Disponible".
- Reporte PDF individual accesible desde el botón **"Imprimir Reporte"** en la vista del préstamo.

### 5. Avisos automáticos de préstamos vencidos
- Acción programada (`ir.cron`) que se ejecuta diariamente.
- Detecta préstamos con más de **30 días** desde la fecha de préstamo.
- Marca automáticamente el registro como **"Atrasado"**.
- Genera un mensaje de correo al socio notificando el vencimiento (requiere configuración de servidor SMTP en producción).

### 6. Portal del socio
- Menú **"Mis Préstamos"** accesible desde el portal web en `/my`.
- Tabla con libro, fecha de préstamo y estado.
- Botón de **Renovar** disponible únicamente para préstamos en estado "En curso" (no vencidos).
- La renovación actualiza la fecha de préstamo a la fecha actual.

### 7. Seguridad y permisos
Dos grupos configurados:

| Grupo | Acceso |
|---|---|
| **Bibliotecario** | CRUD completo sobre libros, socios y préstamos. Acceso a POS asignado desde Ajustes → Usuarios. |
| **Usuario Público** | Solo lectura de libros con estado "Disponible" (regla de registro aplicada). |

### 8. Integración con Punto de Venta (POS)
- Cada libro tiene un producto POS vinculado mediante el campo `product_id`.
- Al confirmar el pago de una orden POS con un cliente seleccionado:
  - Se registra automáticamente el préstamo (socio, libro, fecha).
  - El estado del libro cambia a "No disponible".
- Validaciones activas desde el POS:
  - Muestra error si el libro no está disponible.
  - Muestra error si el socio ya tiene 5 préstamos activos.

### 9. API REST
Endpoint público para consultar disponibilidad de libros por ISBN (ver sección [API REST](#api-rest)).

---

## Usuarios de prueba

Los usuarios deben crearse manualmente desde **Settings → Users** y asignarse a los grupos correspondientes.

| Usuario | Rol | Notas |
|---|---|---|
| `bibliotecario@test.com` | Bibliotecario | Acceso total. Asignar permiso POS desde Ajustes → Usuarios. |
| `publico@test.com` | Usuario Público | Solo ve libros disponibles. |
| `socio@test.com` | Portal | Accede a "Mis Préstamos" en `/my`. Debe tener `is_library_member` activado en su contacto. |

---

## API REST

### Consultar disponibilidad por ISBN

```
GET /api/book?isbn=<ISBN>
```

**Respuesta exitosa — HTTP 200 OK**
```json
{
  "title": "Learning SQL",
  "author": "Alan Beaulieu",
  "isbn": "9780596520830",
  "available": true
}
```

**ISBN no encontrado — HTTP 404 Not Found**
```json
{
  "error": "Libro no encontrado"
}
```

**Ejemplo:**
```bash
curl "http://localhost:8069/api/book?isbn=9780596520830"
```

---

## Casos de prueba

### CP-01 — Préstamo exitoso
**Precondición:** Libro disponible, socio con menos de 5 préstamos activos.  
**Pasos:** Biblioteca → Préstamos → Nuevo → seleccionar socio y libro → guardar.  
**Resultado:** Préstamo creado, libro pasa a "No disponible".

### CP-02 — Bloqueo por libro no disponible
**Precondición:** Libro con estado "No disponible".  
**Pasos:** Intentar crear préstamo con ese libro desde Biblioteca → Préstamos → Nuevo.  
**Resultado:** Error: _"El libro no está disponible para préstamo."_  

### CP-03 — Límite de 5 préstamos por socio
**Precondición:** Socio con 5 préstamos activos.  
**Pasos:** Intentar crear un sexto préstamo para ese socio.  
**Resultado:** Error: _"El socio ya tiene 5 préstamos activos."_  

### CP-04 — Vencimiento automático (cron)
**Precondición:** Préstamo activo con fecha anterior a 30 días.  
**Pasos:** Settings → Technical → Scheduled Actions → "Verificar préstamos vencidos" → Run Manually.  
**Resultado:** El préstamo cambia a estado "Atrasado" y se genera mensaje de notificación al socio.

### CP-05 — Renovación desde portal
**Precondición:** Socio autenticado en el portal con préstamo activo no vencido.  
**Pasos:** Ir a `/my` → "Mis Préstamos" → clic en "Renovar".  
**Resultado:** La fecha de préstamo se actualiza a la fecha actual.

### CP-06 — Acceso por roles
**Pasos:** Iniciar sesión como Usuario Público → ir al catálogo de libros.  
**Resultado:** Solo se listan libros disponibles. No aparecen opciones de crear o editar.

### CP-07 — API REST ISBN existente
```bash
curl "http://localhost:8069/api/book?isbn=9780596520830"
```
**Resultado:** HTTP 200 OK + JSON con disponibilidad y datos del libro.

### CP-08 — API REST ISBN inexistente
```bash
curl "http://localhost:8069/api/book?isbn=0000000000000"
```
**Resultado:** HTTP 404 Not Found + JSON con mensaje de error.

### CP-09 — Préstamo desde POS con libro no disponible
**Pasos:** Abrir POS → seleccionar cliente socio → agregar libro no disponible → confirmar pago.  
**Resultado:** Error emergente: _"El libro no está disponible para préstamo."_  

### CP-10 — Devolución manual
**Pasos:** Biblioteca → Préstamos → abrir préstamo activo → clic en "Marcar Devuelto".  
**Resultado:** Estado cambia a "Devuelto", libro vuelve a "Disponible".

---

## Capturas

### Dashboard principal
![Dashboard](screenshots/dashboard.png)

### Gestión de socios
![Members](screenshots/members.png)

### Catálogo de libros
![Books](screenshots/books.png)

### Gestión de préstamos
![Loans](screenshots/loans.png)

### Portal del socio
![Portal](screenshots/portal.png)

### Punto de Venta (POS)
![POS](screenshots/pos.png)

### API REST en funcionamiento
![API](screenshots/api.png)

---

## Decisiones técnicas

**¿Por qué extender `res.partner` para los socios?**  
Odoo gestiona contactos, emails y el portal web sobre `res.partner`. Extenderlo evita duplicar datos y permite que el socio use el portal sin crear un modelo paralelo de usuarios.

**¿Por qué validar en el backend con `ValidationError` y no solo en la vista?**  
Las restricciones implementadas en `create` garantizan que no puedan omitirse desde la API RPC, imports masivos o integraciones externas como el POS.

**¿Por qué usar una secuencia Odoo para el código de socio?**  
`ir.sequence` es el mecanismo estándar de Odoo para identificadores únicos e incrementales. Garantiza unicidad incluso con accesos concurrentes.

**¿Por qué el cron marca vencidos en lugar de solo enviar correos?**  
Cambiar el estado a "Atrasado" permite filtrar, reportar y bloquear renovaciones desde el portal basándose en el campo `state`, independientemente de si el correo llegó o no.

**¿Por qué heredar `mail.thread` en `library.loan`?**  
Para poder usar `message_post` y enviar notificaciones de correo desde el modelo de préstamo al detectar vencimientos.

---

## Limitaciones conocidas

- El envío de correos requiere configuración SMTP externa.
- El endpoint REST no implementa autenticación.
- La integración POS asume que cada libro posee un producto asociado.
- Las pruebas fueron realizadas sobre Odoo 19 Community Edition.

---

## Estructura del módulo

```
library_management/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── library_api.py          # Endpoint REST /api/book + rutas portal
├── data/
│   ├── library_sequence.xml    # Secuencia código de socio
│   └── library_cron.xml        # Acción programada diaria
├── models/
│   ├── __init__.py
│   ├── library_member.py       # Extensión res.partner
│   ├── library_book.py         # Catálogo de libros
│   ├── library_loan.py         # Préstamos y devoluciones
│   └── pos_order.py            # Integración POS
├── reports/
│   ├── report_library_loans.xml
│   └── report_library_loans_template.xml
├── security/
│   ├── library_category.xml    # Categoría del módulo
│   ├── library_groups.xml      # Grupos: Bibliotecario / Usuario Público
│   ├── library_rules.xml       # Regla: Usuario Público solo ve disponibles
│   └── ir.model.access.csv     # Permisos CRUD por modelo y grupo
├── static/
│   └── description/
│       └── icon.png
└── views/
    ├── library_member_views.xml
    ├── library_book_views.xml
    ├── library_loan_views.xml
    └── portal_loan_templates.xml
```

---

## Autor

**Javier** — Prueba técnica Odoo Developer Intern