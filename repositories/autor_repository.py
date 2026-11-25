from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from database import SessionDep
from models.autor import Autor


class AutorRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_id(self, autor_id: int) -> Autor | None:
        return self.session.get(Autor, autor_id)

    def list_all(self, offset: int = 0, limit: int = 100) -> Sequence[Autor]:
        statement = select(Autor).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create(self, autor: Autor) -> Autor:
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def update(self, autor: Autor) -> Autor:
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def delete(self, autor: Autor) -> None:
        self.session.delete(autor)
        self.session.commit()


AutorRepositoryDep = Annotated[AutorRepository, Depends(AutorRepository)]
