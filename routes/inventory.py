from fastapi import APIRouter, Request
from models.inventory import Inventory
from controllers.inventory import (
    create_inventory,
    get_inventories,
    get_inventory_by_id,
    update_inventory_quantity,
    get_total_stock_by_catalog
)
from utils.security import validateadmin

router = APIRouter()

@router.post("/inventories", response_model=Inventory, tags=["Inventories"])
@validateadmin
async def create_inventory_endpoint(request: Request, inventory: Inventory) -> Inventory:
    return await create_inventory(inventory)

@router.get("/inventories", response_model=dict, tags=["Inventories"])
@validateadmin
async def get_inventories_endpoint(request: Request):
    return await get_inventories()

@router.get("/inventories/{inventory_id}", response_model=dict, tags=["Inventories"])
@validateadmin
async def get_inventory_by_id_endpoint(request: Request, inventory_id: str):
    return await get_inventory_by_id(inventory_id)


@router.put("/inventories/{inventory_id}", response_model=Inventory, tags=["Inventories"])
@validateadmin
async def update_inventory_quantity_endpoint(request: Request, inventory_id: str, inventory: Inventory) -> Inventory:
    return await update_inventory_quantity(inventory_id, inventory.quantity, inventory.batch_name)

@router.get("/inventories/stock/{catalog_id}", response_model=dict, tags=["Inventories"])
@validateadmin
async def get_total_stock_by_catalog_endpoint(request: Request, catalog_id: str) -> dict:
    return await get_total_stock_by_catalog(catalog_id)
