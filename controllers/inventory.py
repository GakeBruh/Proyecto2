from models.inventory import Inventory
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId
from pipelines.inventory_pipelines import (
    get_all_inventory_pipeline,
    get_inventory_by_id_pipeline,
    get_total_stock_pipeline,
    validate_catalog_pipeline
)

coll = get_collection("inventories")
catalogs_coll = get_collection("catalogs")

async def create_inventory(inventory: Inventory) -> Inventory:
    try:
        validation_pipeline = validate_catalog_pipeline(inventory.catalog_id)
        catalog_result = list(catalogs_coll.aggregate(validation_pipeline))

        if not catalog_result:
            raise HTTPException(status_code=400, detail="Catalogo no encontrado o inactivo")

        inventory_dict = inventory.model_dump(exclude={"id"})
        result = coll.insert_one(inventory_dict)
        inventory.id = str(result.inserted_id)
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando el inventario: {str(e)}")

async def get_inventories() -> dict:
    try:
        pipeline = get_all_inventory_pipeline()
        results = list(coll.aggregate(pipeline))
        total = coll.count_documents({})
        return {
            "inventories": results,
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el inventario: {str(e)}")

async def get_inventory_by_id(inventory_id: str) -> dict:
    try:
        pipeline = get_inventory_by_id_pipeline(inventory_id)
        results = list(coll.aggregate(pipeline))

        if not results:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")

        return results[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el inventario: {str(e)}")

async def update_inventory_quantity(inventory_id: str, quantity: int) -> Inventory:
    try:
        result = coll.update_one(
            {"_id": ObjectId(inventory_id)},
            {"$set": {"quantity": quantity}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Inventario no encontrado o no modificado")

        updated_pipeline = get_inventory_by_id_pipeline(inventory_id)
        updated = list(coll.aggregate(updated_pipeline))[0]

        return Inventory(**{
            "id": updated["id"],
            "catalog_id": updated["catalog_id"],
            "quantity": updated["quantity"],
            "batch_name": updated["batch_name"],
            "date": updated["date"]
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el inventario: {str(e)}")

async def delete_inventory(inventory_id: str):
    try:
        result = coll.delete_one({"_id": ObjectId(inventory_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")

        return {"message": "Inventario eliminado"}
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando el inventario: {str(e)}")

async def get_total_stock_by_catalog(catalog_id: str) -> dict:
    try:
        pipeline = get_total_stock_pipeline(catalog_id)
        stock_result = list(coll.aggregate(pipeline))

        if not stock_result:
            return {"catalog_id": catalog_id, "total_stock": 0}

        return stock_result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando el total del stock: {str(e)}")
