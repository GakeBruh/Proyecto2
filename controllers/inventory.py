from models.inventory import Inventory
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime, date
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

        # Convierte date a string para MongoDB
        if isinstance(inventory_dict.get("entry_date"), date):
            inventory_dict["entry_date"] = inventory_dict["entry_date"].isoformat()

        result = coll.insert_one(inventory_dict)
        inventory.id = str(result.inserted_id)
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating inventory: {str(e)}")

    
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
        raise HTTPException(status_code=500, detail=f"Error fetching inventories: {str(e)}")

async def get_inventory_by_id(inventory_id: str) -> dict:
    try:
        pipeline = get_inventory_by_id_pipeline(inventory_id)
        results =  coll.aggregate(pipeline).to_list(length=None)

        if not results:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")

        return results[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el inventario: {str(e)}")

async def update_inventory_quantity(inventory_id: str, quantity: int, batch_name: str) -> Inventory:
    try:
        result = await coll.update_one(
            {"_id": ObjectId(inventory_id)},
            {"$set": {
                "quantity": quantity,
                "batch_name": batch_name
            }}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Inventario no encontrado")
        
        if result.modified_count == 0:
           raise HTTPException(status_code=400, detail="No hubo cambios en el inventario")

        updated_pipeline = get_inventory_by_id_pipeline(inventory_id)
        updated_list = await coll.aggregate(updated_pipeline).to_list(length=None)

        if not updated_list:
            raise HTTPException(status_code=404, detail="Inventario no encontrado tras actualizar")

        updated = updated_list[0]

        return Inventory(**{
            "id": updated.get("id") or str(updated.get("_id")),
            "catalog_id": updated["catalog_id"],
            "quantity": updated["quantity"],
            "batch_name": updated["batch_name"],
            "entry_date": updated["entry_date"]
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el inventario: {str(e)}")

async def get_total_stock_by_catalog(catalog_id: str) -> dict:
    try:
        pipeline = get_total_stock_pipeline(catalog_id)
        stock_result = list(coll.aggregate(pipeline))

        if not stock_result:
            return {"catalog_id": catalog_id, "total_stock": 0}

        return stock_result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating total stock: {str(e)}")

async def descontar_inventario(product_id: str, quantity: int):
    if quantity <= 0:
        raise HTTPException(400, "Cantidad a descontar debe ser mayor que cero")

    inventory = await coll.find_one({"catalog_id": product_id})
    if not inventory:
        raise HTTPException(404, f"Inventario no encontrado para producto {product_id}")

    new_quantity = inventory.get("quantity", 0) - quantity
    if new_quantity < 0:
        raise HTTPException(400, f"No hay suficiente inventario para el producto {product_id}")

    result = await coll.update_one({"_id": inventory["_id"]}, {"$set": {"quantity": new_quantity}})
    if result.modified_count == 0:
        raise HTTPException(500, "Error actualizando el inventario")
