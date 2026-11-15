from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.libro import Libro


class LibroAutor(SQLModel, table=True):
    libro_id: int | None = Field(
        default=None, foreign_key="libro.id", primary_key=True
    )
    autor_id: int | None = Field(
        default=None, foreign_key="autor.id", primary_key=True
    )


class AutorBase(SQLModel):
    nombre: str = Field(index=True, min_length=1)
    nacionalidad: str = Field(min_length=1)


class Autor(AutorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    libros: list["Libro"] = Relationship(
        back_populates="autores", link_model=LibroAutor
    )


class AutorCreate(AutorBase):
    pass


class AutorUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    nacionalidad: str | None = Field(default=None, min_length=1)


class AutorRead(AutorBase):
    id: int
