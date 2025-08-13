from fastapi import APIRouter, HTTPException, Request, Depends
from models.catalogs import Catalog
from controllers.catalogs import (
    create_catalog,
    get_catalogs,
    get_catalog_by_id,
    update_catalog,
    deactivate_catalog
)
from utils.security import validate_admin  

router = APIRouter()

@router.post("/catalogs", response_model=Catalog, tags=["Catalogs"])
async def create_catalog_endpoint(
    catalog: Catalog,
    user: dict = Depends(validate_admin)  
) -> Catalog:
    return await create_catalog(catalog)

@router.get("/catalogs", response_model=dict, tags=["Catalogs"])
async def get_catalogs_endpoint() -> dict:
    return await get_catalogs()

@router.get("/catalogs/{catalog_id}", response_model=Catalog, tags=["Catalogs"])
async def get_catalog_by_id_endpoint(catalog_id: str) -> Catalog:
    return await get_catalog_by_id(catalog_id)

@router.get("/catalogs/type/{catalog_type_description}", response_model=dict, tags=["Catalogs"])
async def get_catalogs_by_type_endpoint(
    catalog_type_description: str,
    skip: int = 0,
    limit: int = 10,
    user: dict | None = Depends(validate_admin)  #
) -> dict:
    is_admin = bool(user and user.get("role") == "admin")
    return await get_catalogs_by_type(catalog_type_description, skip, limit, is_admin)

@router.put("/catalogs/{catalog_id}", response_model=Catalog, tags=["Catalogs"])
async def update_catalog_endpoint(
    catalog_id: str,
    catalog: Catalog,
    user: dict = Depends(validate_admin)  
) -> Catalog:
    return await update_catalog(catalog_id, catalog)

@router.delete("/catalogs/{catalog_id}", response_model=Catalog, tags=["Catalogs"])
async def deactivate_catalog_endpoint(
    catalog_id: str,
    user: dict = Depends(validate_admin)  
) -> Catalog:
    return await deactivate_catalog(catalog_id)
