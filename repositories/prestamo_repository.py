from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import col, select

from database import SessionDep
from models.prestamo import Prestamo


class PrestamoRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_id(self, prestamo_id: int) -> Prestamo | None:
        return self.session.get(Prestamo, prestamo_id)

    def list_by_socio(
        self, socio_id: int, activos: bool | None = None
    ) -> Sequence[Prestamo]:
        statement = select(Prestamo).where(col(Prestamo.socio_id) == socio_id)
        if activos is True:
            statement = statement.where(col(Prestamo.fecha_devolucion).is_(None))
        elif activos is False:
            statement = statement.where(
                col(Prestamo.fecha_devolucion).is_not(None)
            )
        return self.session.exec(statement).all()

    def count_activos_by_socio(self, socio_id: int) -> int:
        return len(self.list_by_socio(socio_id=socio_id, activos=True))

    def create(self, prestamo: Prestamo, commit: bool = True) -> Prestamo:
        self.session.add(prestamo)
        if commit:
            self.session.commit()
            self.session.refresh(prestamo)
        else:
            self.session.flush()
        return prestamo

    def update(self, prestamo: Prestamo, commit: bool = True) -> Prestamo:
        self.session.add(prestamo)
        if commit:
            self.session.commit()
            self.session.refresh(prestamo)
        else:
            self.session.flush()
        return prestamo

    def commit_and_refresh(self, prestamo: Prestamo) -> Prestamo:
        try:
            self.session.commit()
            self.session.refresh(prestamo)
            return prestamo
        except Exception:
            self.session.rollback()
            raise


PrestamoRepositoryDep = Annotated[
    PrestamoRepository, Depends(PrestamoRepository)
]
