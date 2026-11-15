from datetime import date, timedelta
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.libro import Libro
    from models.socio import Socio


class PrestamoBase(SQLModel):
    socio_id: int = Field(foreign_key="socio.id", index=True)
    libro_id: int = Field(foreign_key="libro.id", index=True)
    fecha_prestamo: date = Field(default_factory=date.today)
    fecha_vencimiento: date = Field(
        default_factory=lambda: date.today() + timedelta(days=14)
    )
    fecha_devolucion: date | None = Field(default=None, nullable=True)
    multa: float = Field(default=0.0, ge=0)


class Prestamo(PrestamoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    socio: "Socio" = Relationship(back_populates="prestamos")
    libro: "Libro" = Relationship(back_populates="prestamos")


class PrestamoCreate(SQLModel):
    socio_id: int
    libro_id: int
    fecha_prestamo: date | None = None


class DevolucionRequest(SQLModel):
    fecha_devolucion: date | None = None


class PrestamoRead(PrestamoBase):
    id: int
