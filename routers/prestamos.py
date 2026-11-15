from collections.abc import Sequence

from fastapi import APIRouter, Body

from models.prestamo import DevolucionRequest, Prestamo, PrestamoCreate, PrestamoRead
from services.prestamos import PrestamoServiceDep

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.post("", response_model=PrestamoRead, status_code=201)
def create_prestamo(
    data: PrestamoCreate, service: PrestamoServiceDep
) -> Prestamo:
    return service.registrar_prestamo(data)


@router.post("/{id}/devolucion", response_model=PrestamoRead)
def devolver_prestamo(
    id: int,
    service: PrestamoServiceDep,
    req: DevolucionRequest | None = Body(default=None),
) -> Prestamo:
    return service.registrar_devolucion(prestamo_id=id, req=req)


@router.get("/{id}", response_model=PrestamoRead)
def get_prestamo(id: int, service: PrestamoServiceDep) -> Prestamo:
    return service.get_by_id(id)
