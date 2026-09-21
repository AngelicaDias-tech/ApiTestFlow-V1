from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ORIGINS
from app.db.base import Base
from app.db.session import engine
from app.routers import clientes, projetos, testes

# Garante que todos os models estejam registrados no metadata antes do create_all.
from app import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="API TestFlow", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(clientes.router)
app.include_router(projetos.router)
app.include_router(testes.router)
