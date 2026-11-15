from collections.abc import Sequence
from datetime import date, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from database import SessionDep
from models.libro import Libro
from models.prestamo import DevolucionRequest, Prestamo, PrestamoCreate
from models.socio import Socio

MAX_PRESTAMOS_ACTIVOS = 3
DIAS_PLAZO_PRESTAMO = 14
MULTA_POR_DIA_ATRASO = 100.0


class PrestamoService:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_id(self, prestamo_id: int) -> Prestamo:
        prestamo = self.session.get(Prestamo, prestamo_id)
        if not prestamo:
            raise HTTPException(
                status_code=404, detail="Préstamo no encontrado"
            )
        return prestamo

    def get_prestamos_socio(
        self, socio_id: int, activos: bool | None = None
    ) -> Sequence[Prestamo]:
        socio = self.session.get(Socio, socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")

        statement = select(Prestamo).where(col(Prestamo.socio_id) == socio_id)
        if activos is True:
            statement = statement.where(col(Prestamo.fecha_devolucion).is_(None))
        elif activos is False:
            statement = statement.where(
                col(Prestamo.fecha_devolucion).is_not(None)
            )
        return self.session.exec(statement).all()

    def registrar_prestamo(self, data: PrestamoCreate) -> Prestamo:
        socio = self.session.get(Socio, data.socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")

        libro = self.session.get(Libro, data.libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")

        if not socio.activo:
            raise HTTPException(
                status_code=403,
                detail="El socio se encuentra inactivo y no puede solicitar préstamos",
            )

        prestamos_activos = self.get_prestamos_socio(socio.id, activos=True)  # type: ignore[arg-type]
        if len(prestamos_activos) >= MAX_PRESTAMOS_ACTIVOS:
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

        self.session.add(libro)
        self.session.add(prestamo)
        self.session.commit()
        self.session.refresh(prestamo)
        return prestamo

    def registrar_devolucion(
        self, prestamo_id: int, req: DevolucionRequest | None = None
    ) -> Prestamo:
        prestamo = self.get_by_id(prestamo_id)

        if prestamo.fecha_devolucion is not None:
            raise HTTPException(
                status_code=409, detail="El préstamo ya fue devuelto"
            )

        libro = self.session.get(Libro, prestamo.libro_id)
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

        self.session.add(prestamo)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(prestamo)
        return prestamo


PrestamoServiceDep = Annotated[PrestamoService, Depends(PrestamoService)]
