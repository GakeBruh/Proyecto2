from fastapi import APIRouter, HTTPException, Request
from models.box_details import BoxWithProducts, AddProductToBox
from controllers.box_details import (
    get_box_with_products,
    add_product_to_box,
    remove_product_from_box
)
from utils.security import validateadmin

router = APIRouter()

@router.get("/box/{box_id}", response_model=BoxWithProducts, tags=["📦 Box Details"])
async def get_box_with_products_endpoint(box_id: str) -> BoxWithProducts:
    """Obtener información completa del box con todos sus productos"""
    return await get_box_with_products(box_id)

@router.post("/boxes/{box_id}/product", tags=["📦 Box Details"])
@validateadmin
async def add_product_to_box_endpoint(
    box_id: str, 
    product_data: AddProductToBox,
    request: Request
) -> dict:
    """Agregar un producto al box (requiere permisos de admin)"""
    return await add_product_to_box(box_id, product_data)

@router.delete("/boxes/{box_id}/product/{box_detail_id}", tags=["Box Details"])
@validateadmin
async def remove_product_from_box_endpoint(
    box_id: str, 
    box_detail_id: str,
    request: Request
) -> dict:
    """Remover un producto del box (requiere permisos de admin)"""
    return await remove_product_from_box(box_id, box_detail_id)
