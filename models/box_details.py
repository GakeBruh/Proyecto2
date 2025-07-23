from pydantic import BaseModel, Field, field_validator
from typing import Optional

class BoxDetail(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="MongoDB ID - Se genera automáticamente desde el _id de MongoDB, no es necesario enviarlo en POST"
    )

    id_box: str = Field(
        description="ID del box (equivalente a id_product cuando el tipo es box)",
        examples=["507f1f77bcf86cd799439011"]
    )

    id_producto: str = Field(
        description="ID del producto que forma parte del box",
        examples=["507f1f77bcf86cd799439012"]
    )

    quantity: int = Field(
        description="Cantidad del producto en el box",
        gt=0,
        examples=[1, 2, 5]
    )

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, value: int):
        if value <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return value


# Modelo para la respuesta del box completo con productos
class BoxWithProducts(BaseModel):
    id: str = Field(description="ID del box")
    id_catalog_type: str = Field(description="ID del tipo de catálogo")
    name: str = Field(description="Nombre del box")
    description: str = Field(description="Descripción del box")
    cost: float = Field(description="Costo del box")
    discount: int = Field(description="Descuento del box")
    active: bool = Field(description="Estado activo del box")
    products: list[dict] = Field(description="Lista de productos en el box")


# Modelo para agregar producto al box
class AddProductToBox(BaseModel):
    id_producto: str = Field(
        description="ID del producto a agregar al box",
        examples=["507f1f77bcf86cd799439012"]
    )

    quantity: int = Field(
        description="Cantidad del producto a agregar",
        gt=0,
        examples=[1, 2, 5]
    )

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, value: int):
        if value <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return value
