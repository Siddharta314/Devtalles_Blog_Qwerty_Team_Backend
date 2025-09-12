from fastapi import FastAPI
from app.db import init_db
from app.routers.auth import auth_router

app = FastAPI()
init_db()


@app.get("/")
async def root():
    return {"message": "Server is running"}


app.include_router(auth_router, prefix="/api/auth")
