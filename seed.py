#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de ejemplo para desarrollo.
Uso: python seed.py
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db import SessionLocal, engine, Base
from app.models.user import User, UserRole, UserPosition
from app.models.category import Category
from app.models.tag import Tag
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.models.auth_provider import AuthProvider, ProviderType


def clear_database():
    """Limpia todas las tablas de la base de datos."""
    print("🗑️  Limpiando base de datos...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos limpiada y recreada")


def create_users(db: Session) -> dict[str, User]:
    """Crea usuarios de ejemplo."""
    print("👥 Creando usuarios...")

    users = {}

    # Usuario admin
    admin = User.create_local(
        name="Admin",
        lastname="Sistema",
        email="admin@devtalles.com",
        password="admin123",
    )
    admin.role = UserRole.ADMIN
    admin.description = "Administrador del sistema y desarrollador fullstack con más de 10 años de experiencia"
    admin.position = UserPosition.FULLSTACK
    admin.stack = "Python, JavaScript, React, Node.js, PostgreSQL, Docker"
    db.add(admin)
    users["admin"] = admin

    # Usuarios normales
    user_data = [
        (
            "Carlos",
            "Azaustre",
            "carlos@devtalles.com",
            "carlos123",
            "Desarrollador frontend especializado en React y Vue.js",
            UserPosition.FRONTEND,
            "React, Vue.js, TypeScript, CSS, HTML",
        ),
        (
            "Fernando",
            "Herrera",
            "fernando@devtalles.com",
            "fernando123",
            "Backend developer con experiencia en Python y Node.js",
            UserPosition.BACKEND,
            "Python, FastAPI, Node.js, Express, MongoDB",
        ),
        (
            "Miguel",
            "Angel",
            "miguel@devtalles.com",
            "miguel123",
            "DevOps engineer y desarrollador fullstack",
            UserPosition.DEVOPS,
            "Docker, Kubernetes, AWS, Terraform, Python, Go",
        ),
        (
            "Ana",
            "García",
            "ana@devtalles.com",
            "ana123",
            "Desarrolladora móvil con React Native y Flutter",
            UserPosition.MOBILE,
            "React Native, Flutter, JavaScript, Dart, Firebase",
        ),
        (
            "Luis",
            "Martín",
            "luis@devtalles.com",
            "luis123",
            "Data scientist y desarrollador Python",
            UserPosition.DATA,
            "Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL",
        ),
    ]

    for name, lastname, email, password, description, position, stack in user_data:
        user = User.create_local(
            name=name, lastname=lastname, email=email, password=password
        )
        user.description = description
        user.position = position
        user.stack = stack
        db.add(user)
        users[name.lower()] = user

    # Usuario Discord de ejemplo
    discord_user = User.create_social(
        name="Discord",
        lastname="User",
        email="discord@example.com",
        image="https://cdn.discordapp.com/avatars/123456789/avatar.png",
    )
    discord_user.description = "Desarrollador que se unió a través de Discord OAuth"
    discord_user.position = UserPosition.FULLSTACK
    discord_user.stack = "JavaScript, TypeScript, React, Node.js"
    db.add(discord_user)
    users["discord"] = discord_user

    db.flush()  # Para obtener IDs

    # Crear auth_provider para el usuario Discord
    auth_provider = AuthProvider(
        user_id=discord_user.id,
        provider=ProviderType.DISCORD,
        provider_id="123456789",
        access_token="discord_access_token_example",
        refresh_token="discord_refresh_token_example",
    )
    db.add(auth_provider)

    db.commit()
    print(f"✅ Creados {len(users)} usuarios")
    return users


def create_categories(db: Session) -> dict[str, Category]:
    """Crea categorías de ejemplo."""
    print("📂 Creando categorías...")

    categories_data = [
        ("JavaScript", "Todo sobre JavaScript y sus frameworks"),
        ("Python", "Desarrollo con Python y sus librerías"),
        ("React", "Desarrollo frontend con React"),
        ("Node.js", "Backend development with Node.js"),
        ("Database", "Bases de datos y SQL"),
        ("DevOps", "Docker, CI/CD y despliegues"),
        ("Mobile", "Desarrollo móvil React Native y Flutter"),
        ("AI & ML", "Inteligencia Artificial y Machine Learning"),
    ]

    categories = {}
    for name, description in categories_data:
        category = Category(name=name, description=description)
        db.add(category)
        categories[name.lower().replace(" ", "_")] = category

    db.commit()
    print(f"✅ Creadas {len(categories)} categorías")
    return categories


def create_tags(db: Session) -> dict[str, Tag]:
    """Crea tags de ejemplo."""
    print("🏷️  Creando tags...")

    tags_data = [
        "frontend",
        "backend",
        "fullstack",
        "tutorial",
        "beginner",
        "intermediate",
        "advanced",
        "tips",
        "best-practices",
        "frameworks",
        "libraries",
        "tools",
        "deployment",
        "testing",
        "security",
        "performance",
        "api",
        "database",
        "authentication",
        "cors",
    ]

    tags = {}
    for tag_name in tags_data:
        tag = Tag(name=tag_name)
        db.add(tag)
        tags[tag_name] = tag

    db.commit()
    print(f"✅ Creados {len(tags)} tags")
    return tags


def create_posts(db: Session, users: dict, categories: dict, tags: dict) -> list[Post]:
    """Crea posts de ejemplo."""
    print("📝 Creando posts...")

    posts_data = [
        {
            "title": "Introducción a React Hooks",
            "description": "Los React Hooks llegaron para cambiar la forma en que escribimos componentes en React. Aprende todo lo que necesitas saber sobre useState, useEffect y más.",
            "content": """
# React Hooks: La revolución en React

Los React Hooks llegaron para cambiar la forma en que escribimos componentes en React. En este post te explico todo lo que necesitas saber.

## ¿Qué son los Hooks?

Los Hooks son funciones que permiten "engancharse" al estado y ciclo de vida de React desde componentes funcionales.

### useState

```javascript
const [count, setCount] = useState(0);
```

### useEffect

```javascript
useEffect(() => {
  document.title = `Count: ${count}`;
}, [count]);
```

## Ventajas

- Componentes más simples
- Reutilización de lógica
- Mejor performance
- Código más limpio

¡Empieza a usar Hooks hoy mismo!
            """,
            "author": "carlos",
            "category": "react",
            "tags": ["frontend", "react", "tutorial", "beginner"],
            "days_ago": 1,
        },
        {
            "title": "FastAPI vs Flask: ¿Cuál elegir?",
            "description": "Comparación completa entre FastAPI y Flask. Descubre cuál framework de Python es mejor para tu próximo proyecto web.",
            "content": """
# FastAPI vs Flask: Comparación completa

Ambos son frameworks excelentes para Python, pero cada uno tiene sus fortalezas.

## FastAPI

### Ventajas
- Performance superior
- Documentación automática con Swagger
- Type hints nativo
- Async/await support

### Ejemplo
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Flask

### Ventajas
- Simplicidad y flexibilidad
- Ecosistema maduro
- Gran comunidad
- Fácil de aprender

### Ejemplo
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
```

## Conclusión

Para APIs modernas y performance: **FastAPI**
Para simplicidad y proyectos pequeños: **Flask**
            """,
            "author": "fernando",
            "category": "python",
            "tags": ["backend", "python", "api", "tutorial"],
            "days_ago": 3,
        },
        {
            "title": "Docker para Desarrolladores: Guía Práctica",
            "description": "Aprende Docker desde cero con esta guía práctica. Contenedores, imágenes, Dockerfile y Docker Compose explicados paso a paso.",
            "content": """
# Docker: Contenedores para Desarrolladores

Docker ha revolucionado el desarrollo y despliegue de aplicaciones.

## ¿Qué es Docker?

Docker es una plataforma que permite crear, desplegar y ejecutar aplicaciones en contenedores.

## Conceptos Básicos

### Imagen
Una plantilla inmutable para crear contenedores.

### Contenedor
Una instancia ejecutable de una imagen.

### Dockerfile
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

## Comandos Esenciales

```bash
# Construir imagen
docker build -t mi-app .

# Ejecutar contenedor
docker run -p 8000:8000 mi-app

# Ver contenedores
docker ps

# Detener contenedor
docker stop <container-id>
```

## Docker Compose

Para aplicaciones multi-servicio:

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: password
```

¡Docker simplifica todo el proceso de desarrollo!
            """,
            "author": "miguel",
            "category": "devops",
            "tags": ["devops", "docker", "deployment", "tutorial"],
            "days_ago": 5,
        },
        {
            "title": "Autenticación JWT en Node.js",
            "description": "Implementa autenticación segura con JWT en Node.js. Aprende sobre tokens, middleware y mejores prácticas de seguridad.",
            "content": """
# Implementando JWT en Node.js

La autenticación es crucial en cualquier aplicación. Te enseño cómo implementar JWT.

## ¿Qué es JWT?

JSON Web Token es un estándar para transmitir información de forma segura.

## Estructura

Un JWT tiene 3 partes:
- **Header**: Tipo y algoritmo
- **Payload**: Claims/datos
- **Signature**: Verificación

## Implementación

```javascript
const jwt = require('jsonwebtoken');

// Generar token
const token = jwt.sign(
  { userId: user.id, email: user.email },
  process.env.JWT_SECRET,
  { expiresIn: '24h' }
);

// Verificar token
const decoded = jwt.verify(token, process.env.JWT_SECRET);
```

## Middleware de Autenticación

```javascript
const authMiddleware = (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'Token required' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};
```

## Mejores Prácticas

1. Usa HTTPS siempre
2. Tokens de corta duración
3. Implementa refresh tokens
4. Valida en el servidor
5. Logout seguro

¡La seguridad es fundamental!
            """,
            "author": "ana",
            "category": "node.js",
            "tags": ["backend", "authentication", "security", "tutorial"],
            "days_ago": 7,
        },
        {
            "title": "SQL vs NoSQL: ¿Cuándo usar cada uno?",
            "description": "Guía completa para elegir entre bases de datos SQL y NoSQL. Ventajas, desventajas y casos de uso para cada tipo.",
            "content": """
# SQL vs NoSQL: La eterna pregunta

Elegir la base de datos correcta es crucial para el éxito de tu proyecto.

## Bases de Datos SQL

### Características
- Estructura tabular
- ACID compliance
- Relaciones bien definidas
- Consultas complejas con JOINs

### Cuándo usar SQL
- Datos estructurados
- Transacciones complejas
- Consistencia crítica
- Reportes y analytics

### Ejemplos
- PostgreSQL
- MySQL
- SQL Server
- Oracle

## Bases de Datos NoSQL

### Tipos

#### Document Stores
```json
{
  "id": "123",
  "name": "John Doe",
  "posts": [
    {
      "title": "Mi primer post",
      "content": "Contenido..."
    }
  ]
}
```

#### Key-Value
```
user:123 -> {"name": "John", "email": "john@example.com"}
```

#### Column Family
```
Row Key: user123
Columns: name, email, created_at
```

#### Graph
```
(User)-[FOLLOWS]->(User)
(User)-[LIKES]->(Post)
```

### Cuándo usar NoSQL
- Datos no estructurados
- Escalabilidad horizontal
- Desarrollo ágil
- Grandes volúmenes

## Conclusión

No hay una respuesta única. Depende de:
- Tipo de datos
- Escalabilidad requerida
- Consistencia vs Disponibilidad
- Experiencia del equipo

¡A veces incluso puedes usar ambos!
            """,
            "author": "luis",
            "category": "database",
            "tags": ["database", "sql", "nosql", "architecture"],
            "days_ago": 10,
        },
    ]

    posts = []
    for post_data in posts_data:
        # Calcular fecha
        created_at = datetime.now() - timedelta(days=post_data["days_ago"])

        # Calcular tiempo de lectura estimado (palabras / 200 palabras por minuto)
        word_count = len(post_data["content"].split())
        reading_time = max(1, word_count // 200)  # Mínimo 1 minuto

        post = Post(
            title=post_data["title"],
            description=post_data["description"],
            content=post_data["content"],
            reading_time=reading_time,
            author_id=users[post_data["author"]].id,
            category_id=categories[post_data["category"]].id,
            created_at=created_at,
        )
        db.add(post)
        db.flush()  # Para obtener el ID

        # Agregar tags al post
        for tag_name in post_data["tags"]:
            if tag_name in tags:
                post.tags.append(tags[tag_name])

        posts.append(post)

    db.commit()
    print(f"✅ Creados {len(posts)} posts")
    return posts


def create_comments(db: Session, users: dict, posts: list) -> list[Comment]:
    """Crea comentarios de ejemplo."""
    print("💬 Creando comentarios...")

    comments_data = [
        {
            "content": "¡Excelente explicación! Los hooks realmente cambiaron mi forma de programar en React.",
            "author": "fernando",
            "post_index": 0,
            "hours_ago": 2,
        },
        {
            "content": "Me ayudó mucho este tutorial. ¿Podrías hacer uno sobre useContext?",
            "author": "miguel",
            "post_index": 0,
            "hours_ago": 5,
        },
        {
            "content": "FastAPI es increíble. Lo estoy usando en producción y el performance es excelente.",
            "author": "carlos",
            "post_index": 1,
            "hours_ago": 8,
        },
        {
            "content": "¿Tienes algún benchmark comparando ambos frameworks?",
            "author": "ana",
            "post_index": 1,
            "hours_ago": 12,
        },
        {
            "content": "Docker me salvó la vida en mi último proyecto. Ya no más 'en mi máquina funciona' 😄",
            "author": "luis",
            "post_index": 2,
            "hours_ago": 3,
        },
        {
            "content": "¿Podrías explicar más sobre Docker volumes?",
            "author": "discord",
            "post_index": 2,
            "hours_ago": 6,
        },
        {
            "content": "JWT es fundamental. ¿Qué opinas sobre usar refresh tokens?",
            "author": "carlos",
            "post_index": 3,
            "hours_ago": 4,
        },
        {
            "content": "Muy buena explicación del tema. Lo implementaré en mi próximo proyecto.",
            "author": "fernando",
            "post_index": 4,
            "hours_ago": 7,
        },
    ]

    comments = []
    for comment_data in comments_data:
        created_at = datetime.now() - timedelta(hours=comment_data["hours_ago"])

        comment = Comment(
            content=comment_data["content"],
            author_id=users[comment_data["author"]].id,
            post_id=posts[comment_data["post_index"]].id,
            created_at=created_at,
        )
        db.add(comment)
        comments.append(comment)

    db.commit()
    print(f"✅ Creados {len(comments)} comentarios")
    return comments


def create_likes(db: Session, users: dict, posts: list) -> list[Like]:
    """Crea likes de ejemplo."""
    print("❤️  Creando likes...")

    # Configurar likes por post
    likes_config = [
        {"post_index": 0, "users": ["fernando", "miguel", "ana", "luis", "discord"]},
        {"post_index": 1, "users": ["carlos", "ana", "miguel"]},
        {"post_index": 2, "users": ["luis", "ana", "fernando", "discord"]},
        {"post_index": 3, "users": ["carlos", "fernando", "miguel"]},
        {"post_index": 4, "users": ["ana", "carlos", "discord"]},
    ]

    likes = []
    for config in likes_config:
        post = posts[config["post_index"]]
        for user_name in config["users"]:
            # Evitar que el autor se dé like a sí mismo
            if users[user_name].id != post.author_id:
                like = Like(
                    user_id=users[user_name].id,
                    post_id=post.id,
                )
                db.add(like)
                likes.append(like)

    db.commit()
    print(f"✅ Creados {len(likes)} likes")
    return likes


def print_summary(
    users: dict, categories: dict, tags: dict, posts: list, comments: list, likes: list
):
    """Imprime un resumen de los datos creados."""
    print("\n" + "=" * 50)
    print("🎉 SEED COMPLETADO EXITOSAMENTE")
    print("=" * 50)
    print(f"👥 Usuarios: {len(users)}")
    print(f"📂 Categorías: {len(categories)}")
    print(f"🏷️  Tags: {len(tags)}")
    print(f"📝 Posts: {len(posts)}")
    print(f"💬 Comentarios: {len(comments)}")
    print(f"❤️  Likes: {len(likes)}")
    print("\n📧 Credenciales de acceso:")
    print("   Admin: admin@devtalles.com / admin123")
    print("   Carlos: carlos@devtalles.com / carlos123")
    print("   Fernando: fernando@devtalles.com / fernando123")
    print("   Miguel: miguel@devtalles.com / miguel123")
    print("   Ana: ana@devtalles.com / ana123")
    print("   Luis: luis@devtalles.com / luis123")
    print("\n🚀 ¡Base de datos lista para desarrollo!")
    print("=" * 50)


def main():
    """Función principal del seed."""
    print("🌱 INICIANDO SEED DE BASE DE DATOS")
    print("=" * 40)

    # Limpiar base de datos
    clear_database()

    # Crear sesión
    db = SessionLocal()

    try:
        # Crear datos en orden
        users = create_users(db)
        categories = create_categories(db)
        tags = create_tags(db)
        posts = create_posts(db, users, categories, tags)
        comments = create_comments(db, users, posts)
        likes = create_likes(db, users, posts)

        # Mostrar resumen
        print_summary(users, categories, tags, posts, comments, likes)

    except Exception as e:
        print(f"❌ Error durante el seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
