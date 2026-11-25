from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException

from models.socio import Socio, SocioCreate, SocioUpdate
from repositories.socio_repository import SocioRepositoryDep


class SocioService:
    def __init__(self, repo: SocioRepositoryDep):
        self.repo = repo

    def create(self, data: SocioCreate) -> Socio:
        if self.repo.get_by_email(data.email):
            raise HTTPException(
                status_code=409, detail="Ya existe un socio con ese email"
            )
        socio = Socio.model_validate(data)
        return self.repo.create(socio)

    def list_all(self, offset: int = 0, limit: int = 100) -> Sequence[Socio]:
        return self.repo.list_all(offset=offset, limit=limit)

    def get_by_id(self, socio_id: int) -> Socio:
        socio = self.repo.get_by_id(socio_id)
        if not socio:
            raise HTTPException(status_code=404, detail="Socio no encontrado")
        return socio

    def update(self, socio_id: int, data: SocioUpdate) -> Socio:
        socio = self.get_by_id(socio_id)
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != socio.email:
            if self.repo.get_by_email(update_data["email"]):
                raise HTTPException(
                    status_code=409, detail="Ya existe un socio con ese email"
                )
        for key, value in update_data.items():
            setattr(socio, key, value)
        return self.repo.update(socio)

    def delete(self, socio_id: int) -> None:
        socio = self.get_by_id(socio_id)
        self.repo.delete(socio)


SocioServiceDep = Annotated[SocioService, Depends(SocioService)]
