from fastapi import FastAPI
from database import initialize_db
from auth import router as auth_router
from shanyrak import router as shanyrak_router
from comments import router as comments_router

initialize_db()
app = FastAPI()

app.include_router(auth_router)
app.include_router(shanyrak_router)
app.include_router(comments_router)


@app.get("/")
def home():
    return {"message": "Shanyraq API is running"}