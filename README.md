# Backend Blogpost DevTalles 

## Stack
* FastAPI
* SQLAlchemy
* PostgreSQL 
* uv



## Installation and run with uv 
uv run uvicorn app.main:app --reload


## Routes: 
* POST `/api/auth/register` -> registro: valida email único, crea usuario con password hasheado.
* POST `/api/auth/login`    -> login: verifica credenciales y retorna datos del usuario.


## Database Schema

[Ver diagrama de base de datos](https://www.mermaidchart.com/app/projects/2f622023-c812-43fd-a487-03dc1dcecf6a/diagrams/69f18f4e-f733-4ac3-8b90-45796ab74f9d/version/v0.1/edit)

![Database Schema](./docs/database_schema.png)


## 📝 Roadmap

### ✅ Hecho
- ✅ Inicializar proyecto con `uv`
- ✅ Crear modelos `User` y `Post`
- ✅ Crear base de datos con SQLite (modo desarrollo)
- ✅ Configurar SQLAlchemy
- ✅ Auth: crear `schemas` y `router` con endpoints `register` y `login`
- ✅ Generar y devolver JWT en el login (`create_access_token`)
- ✅ Dependencias de seguridad (`get_current_user`, `get_current_admin_user`)

### 🚧 En progreso / Próximos pasos
- 🚧 CRUD de `Post` (crear, listar, ver detalle, actualizar, borrar)
- 🚧 Relación `Post` ↔ `User` (author)
- 🚧 Implementar `Comment` (modelo + endpoints)
- 🚧 Implementar `Like` (modelo + endpoints)
- 🚧 Implementar `Category` y `Tag` con relaciones
- 🚧 Añadir filtros y búsqueda de posts (categoría, tag, texto)
- 🚧 Subida y gestión de imágenes en posts
- 🚧 Roles de usuario (`admin`, `user`) con autorización en rutas protegidas
- 🚧 Migración a PostgreSQL (modo producción)
- 🚧 Dockerfile + docker-compose (FastAPI + PostgreSQL)
- 🚧 Tests automáticos con Pytest
- 🚧 Despliegue en servicio cloud

---
