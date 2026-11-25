from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import col, select

from database import SessionDep
from models.socio import Socio


class SocioRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_id(self, socio_id: int) -> Socio | None:
        return self.session.get(Socio, socio_id)

    def get_by_email(self, email: str) -> Socio | None:
        statement = select(Socio).where(col(Socio.email) == email)
        return self.session.exec(statement).first()

    def list_all(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        statement = select(Socio).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create(self, socio: Socio) -> Socio:
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def update(self, socio: Socio) -> Socio:
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def delete(self, socio: Socio) -> None:
        self.session.delete(socio)
        self.session.commit()


SocioRepositoryDep = Annotated[SocioRepository, Depends(SocioRepository)]
