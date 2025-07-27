from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
import re

class Inventory(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="ID MongoDB"
    )

    catalog_id: str = Field(
        description="ID del producto del catálogo al que pertenece este lote",
        examples=["507f1f77bcf86cd799439011"]
    )

    quantity: int = Field(
        description="Cantidad de unidades en este lote",
        gt=0,
        examples=[45, 100]
    )

    batch_name: str = Field(
        description="Nombre identificador del lote",
        min_length=1,
        max_length=100,
        examples=["Lote Julio 2025", "Figuras MGR"]
    )

    entry_date: date = Field(
        description="Fecha de ingreso al inventario",
        examples=["2025-07-15"]
    )

    @field_validator('batch_name')
    @classmethod
    def validate_batch_name(cls, v):
        if not re.match(r"^[a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑ.,\-()]+$", v):
            raise ValueError("El nombre del lote contiene caracteres no permitidos")
        return v
