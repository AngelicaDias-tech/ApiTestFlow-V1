import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SQLite é usado para acelerar o desenvolvimento local. Trocar para Postgres em produção
# exige apenas alterar a variável de ambiente DATABASE_URL (ex.: postgresql+psycopg://...),
# sem nenhuma mudança no restante da aplicação.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'apitestflow.db'}")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:4200,http://localhost:4300").split(",")
    if origin.strip()
]
