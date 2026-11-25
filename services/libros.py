from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException

from models.libro import Libro, LibroCreate, LibroUpdate
from repositories.autor_repository import AutorRepositoryDep
from repositories.libro_repository import LibroRepositoryDep


class LibroService:
    def __init__(
        self, repo: LibroRepositoryDep, autor_repo: AutorRepositoryDep
    ):
        self.repo = repo
        self.autor_repo = autor_repo

    def create(self, data: LibroCreate) -> Libro:
        if self.repo.get_by_isbn(data.isbn):
            raise HTTPException(
                status_code=409, detail="Ya existe un libro con ese ISBN"
            )
        libro = Libro.model_validate(data)
        return self.repo.create(libro)

    def list_all(
        self,
        disponibles: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Libro]:
        return self.repo.list_all(
            disponibles=disponibles, offset=offset, limit=limit
        )

    def get_by_id(self, libro_id: int) -> Libro:
        libro = self.repo.get_by_id(libro_id)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        return libro

    def update(self, libro_id: int, data: LibroUpdate) -> Libro:
        libro = self.get_by_id(libro_id)
        update_data = data.model_dump(exclude_unset=True)
        if "isbn" in update_data and update_data["isbn"] != libro.isbn:
            if self.repo.get_by_isbn(update_data["isbn"]):
                raise HTTPException(
                    status_code=409, detail="Ya existe un libro con ese ISBN"
                )
        for key, value in update_data.items():
            setattr(libro, key, value)
        return self.repo.update(libro)

    def delete(self, libro_id: int) -> None:
        libro = self.get_by_id(libro_id)
        self.repo.delete(libro)

    def asociar_autor(self, libro_id: int, autor_id: int) -> Libro:
        libro = self.get_by_id(libro_id)
        autor = self.autor_repo.get_by_id(autor_id)
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")

        if self.repo.get_libro_autor_link(libro_id, autor_id):
            raise HTTPException(
                status_code=409, detail="El autor ya está asociado a este libro"
            )

        return self.repo.add_autor(libro, autor)


LibroServiceDep = Annotated[LibroService, Depends(LibroService)]
