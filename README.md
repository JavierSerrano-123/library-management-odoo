# Library Management - Odoo Module

## Descripción

Módulo desarrollado en Odoo para la gestión de bibliotecas.

Permite administrar:

- Socios
- Libros
- Préstamos
- Disponibilidad de libros
- Control de usuarios y permisos

---

# Funcionalidades

## Gestión de Socios

- Registro de socios
- Código automático de socio
- Relación con préstamos

## Gestión de Libros

- Catálogo de libros
- Autor
- ISBN
- Fecha de publicación
- Disponibilidad
- Años desde publicación

## Gestión de Préstamos

- Crear préstamos
- Validar disponibilidad
- Limitar máximo 5 préstamos activos por socio
- Marcar préstamos como devueltos
- Marcar préstamos atrasados

## Seguridad

### Bibliotecario

- Control total del sistema

### Usuario Público

- Solo puede visualizar libros disponibles

## Automatización

- Cron automático para detectar préstamos atrasados

## Reportes

- Reporte PDF de préstamos

---

# Tecnologías Utilizadas

- Odoo 19
- Python
- PostgreSQL
- XML

---

# Instalación

## Requisitos

- Python 3.12+
- PostgreSQL
- Odoo 19

## Pasos

1. Clonar el proyecto

2. Copiar el módulo en:

```txt
odoo/addons/
```

3. Actualizar aplicaciones

4. Instalar módulo "Library Management"

---

# Usuarios de prueba

## Bibliotecario

Permisos completos.

## Usuario Público

Solo lectura de libros disponibles.

---

# Casos de prueba realizados

1. Crear préstamo exitosamente
2. Evitar préstamo de libro no disponible
3. Limitar máximo 5 préstamos activos
4. Marcar préstamo como devuelto
5. Detectar préstamos atrasados automáticamente

---

# Autor

Javier