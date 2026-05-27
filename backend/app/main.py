from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import Base, engine
from app.monitoring import record_metrics
from app.routers import auth, health, metrics, tasks

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(record_metrics)

app.include_router(health.router, tags=["system"])
app.include_router(metrics.router, tags=["system"])
app.include_router(auth.router, tags=["auth"])
app.include_router(tasks.router)
