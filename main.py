from contextlib import asynccontextmanager

from fastapi import FastAPI

import models  # noqa: F401 - Registra todos los modelos en SQLModel.metadata
from database import create_db_and_tables
from routers import autores, libros, prestamos, socios


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Sistema de Biblioteca API",
    description="API REST para gestión de catálogo de biblioteca, socios y préstamos (TP2 - Programación IV)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)
app.include_router(prestamos.router)
