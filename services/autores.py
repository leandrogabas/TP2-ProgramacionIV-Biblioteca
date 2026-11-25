from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException

from models.autor import Autor, AutorCreate, AutorUpdate
from repositories.autor_repository import AutorRepositoryDep


class AutorService:
    def __init__(self, repo: AutorRepositoryDep):
        self.repo = repo

    def create(self, data: AutorCreate) -> Autor:
        autor = Autor.model_validate(data)
        return self.repo.create(autor)

    def list_all(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        return self.repo.list_all(offset=offset, limit=limit)

    def get_by_id(self, autor_id: int) -> Autor:
        autor = self.repo.get_by_id(autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        return autor

    def update(self, autor_id: int, data: AutorUpdate) -> Autor:
        autor = self.get_by_id(autor_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(autor, key, value)
        return self.repo.update(autor)

    def delete(self, autor_id: int) -> None:
        autor = self.get_by_id(autor_id)
        self.repo.delete(autor)


AutorServiceDep = Annotated[AutorService, Depends(AutorService)]
