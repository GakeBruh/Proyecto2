from fastapi import APIRouter, HTTPException, Request
from models.inventory import Inventory
from controllers.inventory import (
    create_inventory,
    get_inventories,
    get_inventory_by_id,
    update_inventory_quantity,
    delete_inventory,
    get_total_stock_by_catalog
)
from utils.security import validateadmin

router = APIRouter()

@router.post("/inventories", response_model=Inventory, tags=["Inventories"])
@validateadmin
async def create_inventory_endpoint(request: Request, inventory: Inventory) -> Inventory:
    """Crear un nuevo lote de inventario"""
    return await create_inventory(inventory)

@router.get("/inventories", response_model=dict, tags=["Inventories"])
@validateadmin
async def get_inventories_endpoint() -> dict:
    """Obtener todos los lotes del inventario"""
    return await get_inventories()

@router.get("/inventories/{inventory_id}", response_model=Inventory, tags=["Inventories"])
@validateadmin
async def get_inventory_by_id_endpoint(inventory_id: str) -> Inventory:
    """Obtener el detalle de un lote por ID"""
    return await get_inventory_by_id(inventory_id)

@router.put("/inventories/{inventory_id}", response_model=Inventory, tags=["Inventories"])
@validateadmin
async def update_inventory_quantity_endpoint(request: Request, inventory_id: str, inventory: Inventory) -> Inventory:
    """Actualizar la cantidad de un lote de inventario"""
    return await update_inventory_quantity(inventory_id, inventory.quantity)

@router.delete("/inventories/{inventory_id}", tags=["📦 Inventories"])
@validateadmin
async def delete_inventory_endpoint(request: Request, inventory_id: str):
    """Eliminar un lote de inventario"""
    return await delete_inventory(inventory_id)

@router.get("/inventories/stock/{catalog_id}", response_model=dict, tags=["Inventories"])
@validateadmin
async def get_total_stock_by_catalog_endpoint(catalog_id: str) -> dict:
    """Obtener el stock total de un producto del catálogo (sumando sus lotes)"""
    return await get_total_stock_by_catalog(catalog_id)
