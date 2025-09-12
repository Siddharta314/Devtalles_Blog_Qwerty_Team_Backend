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
