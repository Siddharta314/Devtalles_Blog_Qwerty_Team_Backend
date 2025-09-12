from fastapi import FastAPI
from app.db import init_db
from app.routers import api_router
from app.core.config import settings

print(settings.SECRET_KEY)
app = FastAPI()
init_db()


@app.get("/")
async def root():
    return {"message": "Server is running"}


app.include_router(api_router)
