from repositories.autor_repository import AutorRepository, AutorRepositoryDep
from repositories.libro_repository import LibroRepository, LibroRepositoryDep
from repositories.prestamo_repository import (
    PrestamoRepository,
    PrestamoRepositoryDep,
)
from repositories.socio_repository import SocioRepository, SocioRepositoryDep

__all__ = [
    "AutorRepository",
    "AutorRepositoryDep",
    "LibroRepository",
    "LibroRepositoryDep",
    "SocioRepository",
    "SocioRepositoryDep",
    "PrestamoRepository",
    "PrestamoRepositoryDep",
]
