# Backend Blogpost DevTalles 

## Stack
* FastAPI
* SQLAlchemy
* PostgreSQL 
* uv



## Installation and run with uv 
uv run uvicorn app.main:app --reload


## Routes: 
* POST `/api/auth`       -> registro: valida email único, crea usuario con password hasheado.
* POST `/api/auth/login` -> login: verifica credenciales y retorna datos del usuario.