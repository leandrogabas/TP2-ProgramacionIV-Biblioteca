from collections.abc import Sequence
from datetime import date, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException

from models.prestamo import DevolucionRequest, Prestamo, PrestamoCreate
from repositories.libro_repository import LibroRepositoryDep
from repositories.prestamo_repository import PrestamoRepositoryDep
from repositories.socio_repository import SocioRepositoryDep

MAX_PRESTAMOS_ACTIVOS = 3
DIAS_PLAZO_PRESTAMO = 14
MULTA_POR_DIA_ATRASO = 100.0


class PrestamoService:
    def __init__(
        self,
        repo: PrestamoRepositoryDep,
        socio_repo: SocioRepositoryDep,
        libro_repo: LibroRepositoryDep,
    ):
        self.repo = repo
        self.socio_repo = socio_repo
        self.libro_repo = libro_repo

    def get_by_id(self, prestamo_id: int) -> Prestamo:
        prestamo = self.repo.get_by_id(prestamo_id)
        if not prestamo:
            raise HTTPException(
                status_code=404, detail="Préstamo no encontrado"
            )
        return prestamo

    def get_prestamos_socio(
        self, socio_id: int, activos: bool | None = None
    ) -> Sequence[Prestamo]:
        socio = self.socio_repo.get_by_id(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")

        return self.repo.list_by_socio(socio_id=socio_id, activos=activos)

    def registrar_prestamo(self, data: PrestamoCreate) -> Prestamo:
        socio = self.socio_repo.get_by_id(data.socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")

        libro = self.libro_repo.get_by_id(data.libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")

        if not socio.activo:
            raise HTTPException(
                status_code=403,
                detail="El socio se encuentra inactivo y no puede solicitar préstamos",
            )

        if (
            self.repo.count_activos_by_socio(data.socio_id)
            >= MAX_PRESTAMOS_ACTIVOS
        ):
            raise HTTPException(
                status_code=409,
                detail=f"El socio ya alcanzó el límite de {MAX_PRESTAMOS_ACTIVOS} préstamos activos",
            )

        if libro.stock <= 0:
            raise HTTPException(
                status_code=409,
                detail="No hay stock disponible para el libro solicitado",
            )

        fecha_prestamo = data.fecha_prestamo or date.today()
        fecha_vencimiento = fecha_prestamo + timedelta(days=DIAS_PLAZO_PRESTAMO)

        libro.stock -= 1
        prestamo = Prestamo(
            socio_id=data.socio_id,
            libro_id=data.libro_id,
            fecha_prestamo=fecha_prestamo,
            fecha_vencimiento=fecha_vencimiento,
            fecha_devolucion=None,
            multa=0.0,
        )

        # Se preparan ambos cambios en la sesión compartida (flush) y se confirman atómicamente
        self.libro_repo.update(libro, commit=False)
        self.repo.create(prestamo, commit=False)
        return self.repo.commit_and_refresh(prestamo)

    def registrar_devolucion(
        self, prestamo_id: int, req: DevolucionRequest | None = None
    ) -> Prestamo:
        prestamo = self.get_by_id(prestamo_id)

        if prestamo.fecha_devolucion is not None:
            raise HTTPException(
                status_code=409, detail="El préstamo ya fue devuelto"
            )

        libro = self.libro_repo.get_by_id(prestamo.libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")

        fecha_devolucion = (
            req.fecha_devolucion
            if req and req.fecha_devolucion is not None
            else date.today()
        )

        dias_atraso = (fecha_devolucion - prestamo.fecha_vencimiento).days
        multa = (
            float(dias_atraso * MULTA_POR_DIA_ATRASO) if dias_atraso > 0 else 0.0
        )

        prestamo.fecha_devolucion = fecha_devolucion
        prestamo.multa = multa
        libro.stock += 1

        # Se preparan ambos cambios en la sesión compartida (flush) y se confirman atómicamente
        self.libro_repo.update(libro, commit=False)
        self.repo.update(prestamo, commit=False)
        return self.repo.commit_and_refresh(prestamo)


PrestamoServiceDep = Annotated[PrestamoService, Depends(PrestamoService)]
