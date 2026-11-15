from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query

from models.libro import Libro, LibroCreate, LibroRead, LibroUpdate
from services.libros import LibroServiceDep

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("", response_model=LibroRead, status_code=201)
def create_libro(data: LibroCreate, service: LibroServiceDep) -> Libro:
    return service.create(data)


@router.get("", response_model=Sequence[LibroRead])
def list_libros(
    service: LibroServiceDep,
    disponibles: bool | None = Query(default=None),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Libro]:
    return service.list_all(
        disponibles=disponibles, offset=offset, limit=limit
    )


@router.get("/{id}", response_model=LibroRead)
def get_libro(id: int, service: LibroServiceDep) -> Libro:
    return service.get_by_id(id)


@router.put("/{id}", response_model=LibroRead)
def replace_libro(
    id: int, data: LibroCreate, service: LibroServiceDep
) -> Libro:
    update_payload = LibroUpdate(
        titulo=data.titulo,
        isbn=data.isbn,
        stock=data.stock,
        anio=data.anio,
    )
    return service.update(id, update_payload)


@router.patch("/{id}", response_model=LibroRead)
def update_libro(id: int, data: LibroUpdate, service: LibroServiceDep) -> Libro:
    return service.update(id, data)


@router.delete("/{id}")
def delete_libro(id: int, service: LibroServiceDep) -> dict[str, bool]:
    service.delete(id)
    return {"ok": True}


@router.post("/{id}/autores/{autor_id}", response_model=LibroRead)
def asociar_autor_a_libro(
    id: int, autor_id: int, service: LibroServiceDep
) -> Libro:
    return service.asociar_autor(libro_id=id, autor_id=autor_id)
