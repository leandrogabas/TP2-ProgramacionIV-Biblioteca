from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from database import SessionDep
from models.autor import Autor, AutorCreate, AutorUpdate


class AutorService:
    def __init__(self, session: SessionDep):
        self.session = session

    def create(self, data: AutorCreate) -> Autor:
        autor = Autor.model_validate(data)
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def list_all(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        statement = select(Autor).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_by_id(self, autor_id: int) -> Autor:
        autor = self.session.get(Autor, autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")
        return autor

    def update(self, autor_id: int, data: AutorUpdate) -> Autor:
        autor = self.get_by_id(autor_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(autor, key, value)
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def delete(self, autor_id: int) -> None:
        autor = self.get_by_id(autor_id)
        self.session.delete(autor)
        self.session.commit()


AutorServiceDep = Annotated[AutorService, Depends(AutorService)]
