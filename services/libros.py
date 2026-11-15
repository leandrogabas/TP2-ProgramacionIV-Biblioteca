from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import col, select

from database import SessionDep
from models.autor import Autor, LibroAutor
from models.libro import Libro, LibroCreate, LibroUpdate


class LibroService:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_by_isbn(self, isbn: str) -> Libro | None:
        statement = select(Libro).where(col(Libro.isbn) == isbn)
        return self.session.exec(statement).first()

    def create(self, data: LibroCreate) -> Libro:
        if self.get_by_isbn(data.isbn):
            raise HTTPException(
                status_code=409, detail="Ya existe un libro con ese ISBN"
            )
        libro = Libro.model_validate(data)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

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

    def get_by_id(self, libro_id: int) -> Libro:
        libro = self.session.get(Libro, libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return libro

    def update(self, libro_id: int, data: LibroUpdate) -> Libro:
        libro = self.get_by_id(libro_id)
        update_data = data.model_dump(exclude_unset=True)
        if "isbn" in update_data and update_data["isbn"] != libro.isbn:
            if self.get_by_isbn(update_data["isbn"]):
                raise HTTPException(
                    status_code=409, detail="Ya existe un libro con ese ISBN"
                )
        for key, value in update_data.items():
            setattr(libro, key, value)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def delete(self, libro_id: int) -> None:
        libro = self.get_by_id(libro_id)
        self.session.delete(libro)
        self.session.commit()

    def asociar_autor(self, libro_id: int, autor_id: int) -> Libro:
        libro = self.get_by_id(libro_id)
        autor = self.session.get(Autor, autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")

        existing_link = self.session.get(LibroAutor, (libro_id, autor_id))
        if existing_link:
            raise HTTPException(
                status_code=409, detail="El autor ya está asociado a este libro"
            )

        libro.autores.append(autor)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro


LibroServiceDep = Annotated[LibroService, Depends(LibroService)]
