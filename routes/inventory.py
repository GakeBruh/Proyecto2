from fastapi import APIRouter, Depends
from models.inventory import Inventory
from controllers.inventory import (
    create_inventory,
    get_inventories,
    get_inventory_by_id,
    update_inventory_quantity,
    get_total_stock_by_catalog
)
from utils.security import validate_admin  # ← versión con Depends

router = APIRouter()

@router.post("/inventories", response_model=Inventory, tags=["Inventories"])
async def create_inventory_endpoint(
    inventory: Inventory,
    user: dict = Depends(validate_admin)  # ← validación
) -> Inventory:
    return await create_inventory(inventory)

@router.get("/inventories", response_model=dict, tags=["Inventories"])
async def get_inventories_endpoint(
    user: dict = Depends(validate_admin)
):
    return await get_inventories()

@router.get("/inventories/{inventory_id}", response_model=dict, tags=["Inventories"])
async def get_inventory_by_id_endpoint(
    inventory_id: str,
    user: dict = Depends(validate_admin)
):
    return await get_inventory_by_id(inventory_id)

@router.put("/inventories/{inventory_id}", response_model=Inventory, tags=["Inventories"])
async def update_inventory_quantity_endpoint(
    inventory_id: str,
    inventory: Inventory,
    user: dict = Depends(validate_admin)
) -> Inventory:
    return await update_inventory_quantity(inventory_id, inventory.quantity, inventory.batch_name)

@router.get("/inventories/stock/{catalog_id}", response_model=dict, tags=["Inventories"])
async def get_total_stock_by_catalog_endpoint(
    catalog_id: str,
    user: dict = Depends(validate_admin)
) -> dict:
    return await get_total_stock_by_catalog(catalog_id)
