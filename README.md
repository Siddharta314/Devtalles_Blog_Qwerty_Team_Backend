# Backend Blogpost DevTalles 

## Stack
* FastAPI
* SQLAlchemy
* PostgreSQL 
* uv



## 🚀 Instalación y Configuración

### 🔧 Desarrollo Local

1. **Instalar dependencias con uv**
   ```bash
   uv sync
   ```
2. **Configurar variables de entorno**
   ```bash
   cp env.example .env
   # Editar .env con tus configuraciones
   ```
3. **Inicializar la base de datos con Alembic**
   ```bash
   # Iniciar PostgreSQL con Docker
   docker compose up -d db
   
   # Aplicar migraciones (desde el host)
   DATABASE_URL=postgresql://devtalles:devtalles@localhost:5432/devtalles_blog uv run alembic upgrade head
   ```
4. **Ejecutar el servidor**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

### 🐳 Con Docker

1. **Ejecutar con Docker Compose**
   ```bash
   docker compose up
   ```
2. **Aplicar migraciones (primera vez)**
   ```bash
   docker compose exec backend uv run alembic upgrade head
   ```

### 📋 Migraciones con Alembic

```bash
# Generar nueva migración
uv run alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
uv run alembic upgrade head

# Ver estado actual
uv run alembic current
```


## Routes: 
### Auth
* POST `/api/auth/register` -> registro: valida email único, crea usuario con password hasheado.
* POST `/api/auth/login`    -> login: verifica credenciales y retorna datos del usuario.
* GET `/api/auth/discord/login` -> redirige a Discord OAuth2 para autenticación social.
* GET `/api/auth/discord/callback` -> callback de Discord OAuth2, crea/actualiza usuario y retorna JWT.
* GET `/api/auth/provider/{user_id}` -> obtener el proveedor de autenticación de un usuario (local o social).
* POST `/api/auth/discord/custom-login` -> endpoint personalizado para NextAuth: recibe token y account directamente del frontend, crea/actualiza usuario Discord y retorna datos con auth_provider_id.
* GET `/api/auth/discord/custom-user/{user_id}` -> obtener datos del usuario con auth_provider_id para NextAuth.


### Posts
* POST `/api/posts/` -> Crear un nuevo post. 🔒 Requiere autenticación (token). Soporta `tags` (array de strings) que se crean automáticamente si no existen.
* GET `/api/posts/` -> Listar posts con paginación (`skip`, `limit`) y filtro opcional por autor. ✅ Público.
* GET `/api/posts/{id}` -> Obtener un post específico por su ID. ✅ Público. Incluye tags asociados.
* PUT `/api/posts/{id}` -> Actualizar un post existente. 🔒 Requiere autenticación y ser el autor o admin. Soporta `tags` (reemplaza lista completa).
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
### Tags
* POST `/api/tags/` -> Crear un nuevo tag. 🔒 Solo admin.
* GET `/api/tags/` -> Listar todos los tags con paginación. ✅ Público.
* GET `/api/tags/popular` -> Obtener tags más populares por número de posts. ✅ Público.
* GET `/api/tags/stats` -> Obtener tags con estadísticas de posts. 🔒 Solo admin.
* GET `/api/tags/{id}` -> Obtener un tag específico por ID. 🔒 Solo admin.
* PUT `/api/tags/{id}` -> Actualizar un tag existente. 🔒 Solo admin.
* DELETE `/api/tags/{id}` -> Eliminar un tag (posts pierden este tag). 🔒 Solo admin.

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
- ✅ CRUD de `Post` (crear, listar, ver detalle, actualizar, borrar)
- ✅ Implementar `Comment` (modelo + endpoints)
- ✅ Implementar `Like` (modelo + endpoints con PK compuesta)
- ✅ Implementar `Category` (modelo + endpoints solo admin + relación opcional con Post)
- ✅ Implementar `Tag` con relaciones many-to-many con Post
- ✅ Dockerfile + docker-compose (FastAPI + PostgreSQL)
- ✅ Migración a PostgreSQL (modo producción)
- ✅ Alembic
- ✅ Social Login (Discord)
- ✅ Endpoints personalizados para NextAuth Discord
- ✅ Crear archivo `requests.http` para probar todos los endpoints desde VSCode REST Client

### 🚧 En progreso
- 🚧 Añadir filtros y búsqueda de posts (categoría, tag, texto)
- 🚧 Subida y gestión de imágenes en posts
- 🚧 Roles de usuario (`admin`, `user`) con autorización en rutas protegidas
- 🚧 Tests automáticos con Pytest
- 🚧 Despliegue en servicio cloud

---
