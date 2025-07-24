from  pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class CatalogType(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID "
    )

    description: str = Field(
        description="Descripción del tipo de catálogo",
        pattern=r"^[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["Product","Special Box"]
    )

    active: bool = Field(
        default=True,
        description="Estado activo del tipo de catálogo"
    )