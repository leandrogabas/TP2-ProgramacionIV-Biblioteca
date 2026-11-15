from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from database import SessionDep
from models.socio import Socio, SocioCreate, SocioUpdate


class SocioService:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_email(self, email: str) -> Socio | None:
        statement = select(Socio).where(col(Socio.email) == email)
        return self.session.exec(statement).first()

    def create(self, data: SocioCreate) -> Socio:
        if self.get_by_email(data.email):
            raise HTTPException(
                status_code=409, detail="Ya existe un socio con ese email"
            )
        socio = Socio.model_validate(data)
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def list_all(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        statement = select(Socio).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_by_id(self, socio_id: int) -> Socio:
        socio = self.session.get(Socio, socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return socio

    def update(self, socio_id: int, data: SocioUpdate) -> Socio:
        socio = self.get_by_id(socio_id)
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != socio.email:
            if self.get_by_email(update_data["email"]):
                raise HTTPException(
                    status_code=409, detail="Ya existe un socio con ese email"
                )
        for key, value in update_data.items():
            setattr(socio, key, value)
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def delete(self, socio_id: int) -> None:
        socio = self.get_by_id(socio_id)
        self.session.delete(socio)
        self.session.commit()


SocioServiceDep = Annotated[SocioService, Depends(SocioService)]
