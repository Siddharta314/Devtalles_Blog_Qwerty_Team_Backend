from fastapi import FastAPI
from app.routers import api_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Server is running"}


app.include_router(api_router)
