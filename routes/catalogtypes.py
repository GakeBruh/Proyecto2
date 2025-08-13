from fastapi import APIRouter, Depends
from models.catalogtypes import CatalogType
from controllers.catalogtypes import (
    create_catalog_type,
    get_catalog_types,
    get_catalog_type_by_id,
    update_catalog_type,
    deactivate_catalog_type
)
from utils.security import validate_token  # <- autenticar cualquier usuario

router = APIRouter()

@router.post("/catalogtypes", response_model=CatalogType, tags=["📂 Catalog Types"])
async def create_catalog_type_endpoint(
    catalog_type: CatalogType,
    user: dict = Depends(validate_token)
) -> CatalogType:
    return await create_catalog_type(catalog_type)

@router.get("/catalogtypes", response_model=list, tags=["📂 Catalog Types"])
async def get_catalog_types_endpoint(
    user: dict = Depends(validate_token)
) -> list:
    return await get_catalog_types()

@router.get("/catalogtypes/{catalog_type_id}", response_model=CatalogType, tags=["📂 Catalog Types"])
async def get_catalog_type_by_id_endpoint(
    catalog_type_id: str,
    user: dict = Depends(validate_token)
) -> CatalogType:
    return await get_catalog_type_by_id(catalog_type_id)

@router.put("/catalogtypes/{catalog_type_id}", response_model=CatalogType, tags=["📂 Catalog Types"])
async def update_catalog_type_endpoint(
    catalog_type_id: str,
    catalog_type: CatalogType,
    user: dict = Depends(validate_token)
) -> CatalogType:
    return await update_catalog_type(catalog_type_id, catalog_type)

@router.delete("/catalogtypes/{catalog_type_id}", response_model=dict, tags=["📂 Catalog Types"])
async def deactivate_catalog_type_endpoint(
    catalog_type_id: str,
    user: dict = Depends(validate_token)
) -> dict:
    return await deactivate_catalog_type(catalog_type_id)
