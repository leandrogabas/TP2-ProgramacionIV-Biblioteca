from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import col, select

from database import SessionDep
from models.autor import Autor, LibroAutor
from models.libro import Libro


class LibroRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_id(self, libro_id: int) -> Libro | None:
        return self.session.get(Libro, libro_id)

    def get_by_isbn(self, isbn: str) -> Libro | None:
        statement = select(Libro).where(col(Libro.isbn) == isbn)
        return self.session.exec(statement).first()

    def list_all(
        self,
        disponibles: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Libro]:
        statement = select(Libro)
        if disponibles is True:
            statement = statement.where(col(Libro.stock) > 0)
        elif disponibles is False:
            statement = statement.where(col(Libro.stock) == 0)
        statement = statement.offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def create(self, libro: Libro) -> Libro:
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def update(self, libro: Libro, commit: bool = True) -> Libro:
        self.session.add(libro)
        if commit:
            self.session.commit()
            self.session.refresh(libro)
        else:
            self.session.flush()
        return libro

    def delete(self, libro: Libro) -> None:
        self.session.delete(libro)
        self.session.commit()

    def get_libro_autor_link(
        self, libro_id: int, autor_id: int
    ) -> LibroAutor | None:
        return self.session.get(LibroAutor, (libro_id, autor_id))

    def add_autor(self, libro: Libro, autor: Autor) -> Libro:
        libro.autores.append(autor)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro


LibroRepositoryDep = Annotated[LibroRepository, Depends(LibroRepository)]
