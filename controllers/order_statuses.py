from models.order_statuses import OrderStatus
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime

orders_collection = get_collection("orders")
order_details_collection = get_collection("order_details")
inventories_collection = get_collection("inventories")
catalogs_collection = get_collection("catalogs")
catalog_types_coll = get_collection("catalogtypes")
box_details_coll = get_collection("box_details")
from pipelines.box_pipelines import get_box_products_pipeline
from controllers.inventory import descontar_inventario
coll = get_collection("order_statuses")


async def create_order_status(order_status: OrderStatus) -> dict:
    """Crear un nuevo order status"""
    try:
        # Normalizar descripción
        order_status.description = order_status.description.strip().lower()

        # Verificar si ya existe un order status con la misma descripción
        existing = coll.find_one({"description": order_status.description})

        if existing:
            raise HTTPException(status_code=400, detail="Order status with this description already exists")

        # Crear el order status
        order_status_dict = order_status.model_dump(exclude={"id"})
        inserted = coll.insert_one(order_status_dict)

        # Retornar el order status creado con su ID
        order_status_dict["id"] = str(inserted.inserted_id)
        return order_status_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order status: {str(e)}")

async def get_order_statuses() -> dict:
    """Obtener todos los order statuses"""
    try:
        # Obtener todos los order statuses directamente
        order_statuses_cursor = coll.find({})
        order_statuses = []
        
        for status in order_statuses_cursor:
            status["id"] = str(status["_id"])
            del status["_id"]
            order_statuses.append(status)
        
        return {
            "order_statuses": order_statuses,
            "total": len(order_statuses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order statuses: {str(e)}")

async def get_order_status_by_id(order_status_id: str) -> dict:
    """Obtener un order status por ID"""
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(order_status_id):
            raise HTTPException(status_code=400, detail="Invalid order status ID")
        
        # Buscar el order status directamente
        order_status = coll.find_one({"_id": ObjectId(order_status_id)})
        
        if not order_status:
            raise HTTPException(status_code=404, detail="Order status not found")
        
        # Convertir ObjectId a string para la respuesta
        order_status["id"] = str(order_status["_id"])
        del order_status["_id"]
        
        return order_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order status: {str(e)}")


async def update_order_status_and_manage_inventory(order_id: str, new_status: str, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    if not ObjectId.is_valid(order_id):
        raise HTTPException(400, "ID de orden inválido")

    order = orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(404, "Orden no encontrada")

    if not is_admin and requesting_user_id:
        if order.get("id_user") != requesting_user_id:
            raise HTTPException(403, "No tienes permiso para modificar esta orden")

    update_result = orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": new_status.lower(), "date_updated": datetime.utcnow()}}
    )
    if update_result.matched_count == 0:
        raise HTTPException(404, "Orden no encontrada o no pudo actualizarse")

    if new_status.lower() in ["paid", "ordered", "confirmed", "delivered"]:
        details = list(order_details_collection.find({"id_order": order_id, "active": True}))
        for detail in details:
            catalog_id = detail["id_producto"]
            cantidad_ordenada = detail["quantity"]

            # Consultar si el producto es una box
            catalog = catalogs_collection.find_one({"_id": ObjectId(catalog_id)})
            if not catalog:
                continue

            tipo_catalogo = catalog.get("id_catalog_type")
            catalog_type = catalog_types_coll.find_one({"_id": ObjectId(tipo_catalogo)})
            if not catalog_type:
                continue

            if catalog_type.get("description", "").lower() == "box":
                # Obtener productos dentro de la box
                box_products_pipeline = get_box_products_pipeline(catalog_id)
                box_products = list(box_details_coll.aggregate(box_products_pipeline))

                for producto in box_products:
                    id_producto = producto["id_producto"]
                    cantidad_en_box = producto["quantity"]
                    cantidad_total = cantidad_en_box * cantidad_ordenada

                    await descontar_inventario(id_producto, cantidad_total)

                    # Verificar si ese producto debe desactivarse
                    inventarios_actualizados = list(inventories_collection.find({"catalog_id": id_producto}))
                    total_restante = sum(i["quantity"] for i in inventarios_actualizados)
                    if total_restante == 0:
                        catalogs_collection.update_one(
                            {"_id": ObjectId(id_producto)},
                            {"$set": {"active": False}}
                        )
            else:
                # Producto individual
                await descontar_inventario(catalog_id, cantidad_ordenada)

                inventarios_actualizados = list(inventories_collection.find({"catalog_id": catalog_id}))
                total_restante = sum(i["quantity"] for i in inventarios_actualizados)
                if total_restante == 0:
                    catalogs_collection.update_one(
                        {"_id": ObjectId(catalog_id)},
                        {"$set": {"active": False}}
                    )

    return {
        "success": True,
        "message": f"Estado de la orden actualizado a '{new_status}' exitosamente"
    }


async def delete_order_status(order_status_id: str) -> dict:
    """Eliminar un order status"""
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(order_status_id):
            raise HTTPException(status_code=400, detail="Invalid order status ID")

        # Obtener el order status antes de eliminarlo
        order_status = coll.find_one({"_id": ObjectId(order_status_id)})

        if not order_status:
            raise HTTPException(status_code=404, detail="Order status not found")

        # Eliminar el order status
        result = coll.delete_one({"_id": ObjectId(order_status_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Order status not found")

        # Convertir ObjectId a string para la respuesta
        order_status["id"] = str(order_status["_id"])
        del order_status["_id"]

        return {
            "message": "Order status deleted successfully",
            "deleted_order_status": order_status
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting order status: {str(e)}")
