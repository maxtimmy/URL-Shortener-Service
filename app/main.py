import time
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db import Base, engine
from app.routers import auth, links
from app.tasks import start_scheduler


def wait_for_db():
    for _ in range(30):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("Database is not ready")


wait_for_db()
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