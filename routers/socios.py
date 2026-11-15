from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query

from models.prestamo import Prestamo, PrestamoRead
from models.socio import Socio, SocioCreate, SocioRead, SocioUpdate
from services.prestamos import PrestamoServiceDep
from services.socios import SocioServiceDep

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.post("", response_model=SocioRead, status_code=201)
def create_socio(data: SocioCreate, service: SocioServiceDep) -> Socio:
    return service.create(data)


@router.get("", response_model=Sequence[SocioRead])
def list_socios(
    service: SocioServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Socio]:
    return service.list_all(offset=offset, limit=limit)


@router.get("/{id}", response_model=SocioRead)
def get_socio(id: int, service: SocioServiceDep) -> Socio:
    return service.get_by_id(id)


@router.put("/{id}", response_model=SocioRead)
def replace_socio(
    id: int, data: SocioCreate, service: SocioServiceDep
) -> Socio:
    update_payload = SocioUpdate(
        nombre=data.nombre,
        email=data.email,
        activo=data.activo,
    )
    return service.update(id, update_payload)


@router.patch("/{id}", response_model=SocioRead)
def update_socio(id: int, data: SocioUpdate, service: SocioServiceDep) -> Socio:
    return service.update(id, data)


@router.delete("/{id}")
def delete_socio(id: int, service: SocioServiceDep) -> dict[str, bool]:
    service.delete(id)
    return {"ok": True}


@router.get("/{id}/prestamos", response_model=Sequence[PrestamoRead])
def list_prestamos_socio(
    id: int,
    service: PrestamoServiceDep,
    activos: bool | None = Query(default=None),
) -> Sequence[Prestamo]:
    return service.get_prestamos_socio(socio_id=id, activos=activos)
