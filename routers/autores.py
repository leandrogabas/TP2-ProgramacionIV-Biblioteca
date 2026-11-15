from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query

from models.autor import Autor, AutorCreate, AutorRead, AutorUpdate
from services.autores import AutorServiceDep

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("", response_model=AutorRead, status_code=201)
def create_autor(data: AutorCreate, service: AutorServiceDep) -> Autor:
    return service.create(data)


@router.get("", response_model=Sequence[AutorRead])
def list_autores(
    service: AutorServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Autor]:
    return service.list_all(offset=offset, limit=limit)


@router.get("/{id}", response_model=AutorRead)
def get_autor(id: int, service: AutorServiceDep) -> Autor:
    return service.get_by_id(id)


@router.put("/{id}", response_model=AutorRead)
def replace_autor(
    id: int, data: AutorCreate, service: AutorServiceDep
) -> Autor:
    update_payload = AutorUpdate(
        nombre=data.nombre, nacionalidad=data.nacionalidad
    )
    return service.update(id, update_payload)


@router.patch("/{id}", response_model=AutorRead)
def update_autor(id: int, data: AutorUpdate, service: AutorServiceDep) -> Autor:
    return service.update(id, data)


@router.delete("/{id}")
def delete_autor(id: int, service: AutorServiceDep) -> dict[str, bool]:
    service.delete(id)
    return {"ok": True}
