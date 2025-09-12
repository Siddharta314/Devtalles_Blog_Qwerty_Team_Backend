# Backend Blogpost DevTalles 

## Stack
* FastAPI
* SQLAlchemy
* PostgreSQL 
* uv



## Installation and run with uv 
uv run uvicorn app.main:app --reload


## Routes: 
### Auth
* POST `/api/auth/register` -> registro: valida email único, crea usuario con password hasheado.
* POST `/api/auth/login`    -> login: verifica credenciales y retorna datos del usuario.
### Posts
* POST `/api/posts/` -> Crear un nuevo post. 🔒 Requiere autenticación (token).
* GET `/api/posts/` -> Listar posts con paginación (`skip`, `limit`) y filtro opcional por autor. 🔒 Solo accesible por admin.
* GET `/api/posts/{id}` -> Obtener un post específico por su ID. ✅ Público.
* PUT `/api/posts/{id}` -> Actualizar un post existente. 🔒 Requiere autenticación y ser el autor o admin.
* DELETE `/api/posts/{id}` -> Eliminar (soft delete) un post. 🔒 Requiere autenticación y ser el autor o admin.
* GET `/api/posts/author/{id}` -> Listar todos los posts de un autor específico. ✅ Público.
* GET `/api/posts/me/posts` -> Listar todos los posts del usuario autenticado. 🔒 Requiere autenticación (token).
### Comments
* POST `/api/comments/` -> Crear un comentario en un post. 🔒 Requiere autenticación (token).
* GET `/api/comments/{id}` -> Obtener un comentario específico por ID. ✅ Público.
* GET `/api/comments/post/{post_id}` -> Listar comentarios de un post con paginación. ✅ Público.
* PUT `/api/comments/{id}` -> Actualizar un comentario. 🔒 Solo autor o admin.
* DELETE `/api/comments/{id}` -> Eliminar un comentario (soft delete). 🔒 Solo autor o admin.
* GET `/api/comments/me/comments` -> Listar todos los comentarios del usuario autenticado. 🔒 Requiere autenticación (token).
### Likes
* POST `/api/likes/` -> Dar like a un post. 🔒 Requiere autenticación (token).
* DELETE `/api/likes/post/{id}` -> Quitar like de un post. 🔒 Requiere autenticación (token).
* POST `/api/likes/toggle` -> Toggle like/unlike en un post. 🔒 Requiere autenticación (token).
* GET `/api/likes/post/{id}/stats` -> Obtener estadísticas de likes de un post + estado del usuario. 🔒 Requiere autenticación (token).
* GET `/api/likes/post/{id}` -> Listar todos los likes de un post específico. ✅ Público.
* GET `/api/likes/me/posts` -> Listar todos los posts que me gustan. 🔒 Requiere autenticación (token).
* GET `/api/likes/check/{id}` -> Verificar si me gusta un post específico. 🔒 Requiere autenticación (token).
### Categories
* POST `/api/categories/` -> Crear una nueva categoría. 🔒 Solo admin.
* GET `/api/categories/` -> Listar todas las categorías con paginación. ✅ Público.
* GET `/api/categories/stats` -> Obtener categorías con estadísticas de posts. 🔒 Solo admin.
* GET `/api/categories/{id}` -> Obtener una categoría específica por ID. 🔒 Solo admin.
* PUT `/api/categories/{id}` -> Actualizar una categoría existente. 🔒 Solo admin.
* DELETE `/api/categories/{id}` -> Eliminar una categoría (posts quedan sin categoría). 🔒 Solo admin.

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
Dependencias de seguridad (`get_current_user`, `get_current_admin_user`)
- ✅ CRUD de `Post` (crear, listar, ver detalle, actualizar, borrar)
- ✅ Implementar `Comment` (modelo + endpoints)
- ✅ Implementar `Like` (modelo + endpoints con PK compuesta)
- ✅ Implementar `Category` (modelo + endpoints solo admin + relación opcional con Post)

### 🚧 En progreso / Próximos pasos
- 🚧 Implementar `Tag` con relaciones many-to-many con Post
- 🚧 Añadir filtros y búsqueda de posts (categoría, tag, texto)
- 🚧 Subida y gestión de imágenes en posts
- 🚧 Roles de usuario (`admin`, `user`) con autorización en rutas protegidas
- 🚧 Crear archivo `requests.http` para probar todos los endpoints desde VSCode REST Client
- 🚧 Migración a PostgreSQL (modo producción)
- 🚧 Dockerfile + docker-compose (FastAPI + PostgreSQL)
- 🚧 Tests automáticos con Pytest
- 🚧 Despliegue en servicio cloud

---
