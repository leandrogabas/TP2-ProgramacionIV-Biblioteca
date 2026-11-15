from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.prestamo import Prestamo


class SocioBase(SQLModel):
    nombre: str = Field(index=True, min_length=1)
    email: EmailStr = Field(unique=True, index=True)
    activo: bool = Field(default=True)


class Socio(SocioBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prestamos: list["Prestamo"] = Relationship(back_populates="socio")


class SocioCreate(SocioBase):
    pass


class SocioUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    activo: bool | None = None


class SocioRead(SocioBase):
    id: int
