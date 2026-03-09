from fastapi import FastAPI
from app.db import Base, engine
from app.routers import auth, links
from app.tasks import start_scheduler


Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener Service")

app.include_router(auth.router)
app.include_router(links.router)


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.get("/")
def root():
    return {"message": "URL Shortener API is running"}