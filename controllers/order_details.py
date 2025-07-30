from utils.mongodb import get_collection
from bson import ObjectId
from datetime import datetime
from models.order_details import OrderDetail, CreateOrderDetail, UpdateOrderDetail
from pipelines.order_detail_pipelines import (
    get_order_details_pipeline,
    get_order_detail_by_id_pipeline
)


order_details_collection = get_collection("order_details")
orders_collection = get_collection("orders")
catalogs_collection = get_collection("catalogs")
inventories_collection = get_collection("inventories")


async def recalculate_order_totals(order_id: str) -> dict:
    try:
        print(f"DEBUG: Recalculando totales para orden: {order_id}")

        # Obtener todos los detalles activos de la orden con información del producto
        pipeline = [
            {"$match": {"id_order": order_id, "active": True}},
            {
                "$lookup": {
                    "from": "catalogs",
                    "let": {"product_id": {"$toObjectId": "$id_producto"}},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$_id", "$$product_id"]}}}
                    ],
                    "as": "product_info"
                }
            },
            {
                "$addFields": {
                    "product": {"$arrayElemAt": ["$product_info", 0]},
                    "product_price": {"$arrayElemAt": ["$product_info.cost", 0]},
                    "line_subtotal": {
                        "$cond": {
                            "if": {"$gt": [{"$size": "$product_info"}, 0]},
                            "then": {
                                "$multiply": [
                                    "$quantity",
                                    {"$arrayElemAt": ["$product_info.cost", 0]}
                                ]
                            },
                            "else": 0
                        }
                    }
                }
            }
        ]

        debug_result = list(order_details_collection.aggregate(pipeline))
        print(f"DEBUG: Detalles encontrados: {len(debug_result)}")
        for detail in debug_result:
            print(f"DEBUG: Detalle - quantity: {detail.get('quantity')}, product_info: {detail.get('product_info')}, line_subtotal: {detail.get('line_subtotal')}")

        pipeline.append({
            "$group": {
                "_id": None,
                "subtotal": {"$sum": "$line_subtotal"},
                "total_items": {"$sum": "$quantity"}
            }
        })

        result = list(order_details_collection.aggregate(pipeline))
        print(f"DEBUG: Resultado del pipeline: {result}")

        if result and result[0]["subtotal"] > 0:
            subtotal = result[0]["subtotal"]
            tax_rate = 0.15
            taxes = subtotal * tax_rate
            discount = 0.0
            total = subtotal + taxes - discount

            print(f"DEBUG: Calculando - subtotal: {subtotal}, taxes: {taxes}, total: {total}")

            update_result = orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "subtotal": round(subtotal, 2),
                        "taxes": round(taxes, 2),
                        "discount": discount,
                        "total": round(total, 2),
                        "date_updated": datetime.utcnow()
                    }
                }
            )

            print(f"DEBUG: Update result - modified_count: {update_result.modified_count}")

            if update_result.modified_count > 0:
                return {
                    "success": True,
                    "subtotal": round(subtotal, 2),
                    "taxes": round(taxes, 2),
                    "discount": discount,
                    "total": round(total, 2)
                }
        else:
            print("DEBUG: No hay productos o subtotal es 0, reseteando a cero")
            # La orden no tiene productos, resetear a cero
            orders_collection.update_one(
                {"_id": ObjectId(order_id)},
                {
                    "$set": {
                        "subtotal": 0.0,
                        "taxes": 0.0,
                        "discount": 0.0,
                        "total": 0.0,
                        "date_updated": datetime.utcnow()
                    }
                }
            )
            return {
                "success": True,
                "subtotal": 0.0,
                "taxes": 0.0,
                "discount": 0.0,
                "total": 0.0
            }

        return {"success": False, "message": "Error al actualizar totales"}

    except Exception as e:
        print(f"DEBUG: Error en recalculate_order_totals: {str(e)}")
        return {"success": False, "message": f"Error al recalcular totales: {str(e)}"}



async def create_order_detail(order_id: str, detail_data: CreateOrderDetail, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    try:
        if not ObjectId.is_valid(order_id):
            return {"success": False, "message": "ID de orden inválido", "data": None}

        order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order_info:
            return {"success": False, "message": "Orden no encontrada", "data": None}

        if not is_admin and requesting_user_id:
            if order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para modificar esta orden", "data": None}

        product_exists = catalogs_collection.find_one({"_id": ObjectId(detail_data.id_producto)})
        if not product_exists:
            return {"success": False, "message": "Producto no encontrado", "data": None}

        existing_detail = order_details_collection.find_one({
            "id_order": order_id,  # Usar string directamente
            "id_producto": detail_data.id_producto,  # Usar string directamente
            "active": True
        })

        if existing_detail:
            return {"success": False, "message": "Este producto ya está en la orden", "data": None}
        
        inventarios = list(inventories_collection.find({"catalog_id": detail_data.id_producto}))
        total_disponible = sum(i["quantity"] for i in inventarios)

        detalles_orden = list(order_details_collection.find({
            "id_order": order_id,
            "id_producto": detail_data.id_producto,
            "active": True
        }))
        total_pedido_actual = sum(d["quantity"] for d in detalles_orden)

        if (total_pedido_actual + detail_data.quantity) > total_disponible:
            return {
                "success": False,
                "message": f"Stock insuficiente para el producto pedido. Disponible: {total_disponible}, solicitado: {total_pedido_actual + detail_data.quantity}",
                "data": None
            }


        detail_dict = detail_data.model_dump()
        detail_dict["id_order"] = order_id  
        detail_dict["id_producto"] = detail_data.id_producto  
        detail_dict["date_created"] = datetime.utcnow()
        detail_dict["date_updated"] = datetime.utcnow()
        detail_dict["active"] = True

        result = order_details_collection.insert_one(detail_dict)
        
        if result.inserted_id:
            # Recalcular totales de la orden después de agregar el producto
            totals_result = await recalculate_order_totals(order_id)
            
            response_data = {"id": str(result.inserted_id)}
            if totals_result["success"]:
                response_data["order_totals"] = {
                    "subtotal": totals_result["subtotal"],
                    "taxes": totals_result["taxes"],
                    "discount": totals_result["discount"],
                    "total": totals_result["total"]
                }
            
            return {
                "success": True,
                "message": "Producto agregado a la orden exitosamente",
                "data": response_data
            }
        
        return {"success": False, "message": "Error al agregar el producto a la orden", "data": None}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "data": None}




async def get_order_details(order_id: str, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(order_id):
            return {"success": False, "message": "ID de orden inválido", "data": None}

        order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order_info:
            return {"success": False, "message": "Orden no encontrada", "data": None}

        if not is_admin and requesting_user_id:
            if order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para ver esta orden", "data": None}

        pipeline = get_order_details_pipeline(order_id)
        details = list(order_details_collection.aggregate(pipeline))

        return {
            "success": True,
            "message": "Detalles de orden obtenidos exitosamente",
            "data": {
                "order_id": order_id,
                "details": details,
                "total_items": len(details)
            }
        }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "data": None}




async def update_order_detail(order_id: str, detail_id: str, update_data: UpdateOrderDetail, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    try:
        print(f"DEBUG: Iniciando update_order_detail - order_id: {order_id}, detail_id: {detail_id}")
        
        if not ObjectId.is_valid(detail_id):
            return {"success": False, "message": "ID de detalle inválido", "data": None}

        if not ObjectId.is_valid(order_id):
            return {"success": False, "message": "ID de orden inválido", "data": None}

        detail_info = order_details_collection.find_one({
            "_id": ObjectId(detail_id), 
            "id_order": order_id,  # VALIDACIÓN CRÍTICA: el detalle debe pertenecer a esta orden
            "active": True
        })

        if not detail_info:
            return {"success": False, "message": "Detalle no encontrado o no pertenece a esta orden", "data": None}

        if not is_admin and requesting_user_id:
            # Obtener la orden asociada al detalle para verificar permisos
            order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
            if not order_info or order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para modificar este detalle", "data": None}

        update_dict = update_data.model_dump()
        update_dict["date_updated"] = datetime.utcnow()

        result = order_details_collection.update_one(
            {"_id": ObjectId(detail_id)},
            {"$set": update_dict}
        )

        if result.modified_count > 0:
            print(f"DEBUG: Detalle actualizado exitosamente, iniciando recálculo de totales")
            totals_result = await recalculate_order_totals(order_id)
            print(f"DEBUG: Resultado del recálculo: {totals_result}")
            
            response_data = {"modified_count": result.modified_count}
            if totals_result["success"]:
                response_data["order_totals"] = {
                    "subtotal": totals_result["subtotal"],
                    "taxes": totals_result["taxes"],
                    "discount": totals_result["discount"],
                    "total": totals_result["total"]
                }
            
            return {
                "success": True,
                "message": "Detalle de orden actualizado exitosamente",
                "data": response_data
            }

        return {"success": False, "message": "No se pudo actualizar el detalle", "data": None}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "data": None}



async def delete_order_detail(order_id: str, detail_id: str, requesting_user_id: str = None, is_admin: bool = False) -> dict:
    try:
        if not ObjectId.is_valid(detail_id):
            return {"success": False, "message": "ID de detalle inválido", "data": None}

        if not ObjectId.is_valid(order_id):
            return {"success": False, "message": "ID de orden inválido", "data": None}

        detail_info = order_details_collection.find_one({
            "_id": ObjectId(detail_id), 
            "id_order": order_id,  # VALIDACIÓN CRÍTICA: el detalle debe pertenecer a esta orden
            "active": True
        })

        if not detail_info:
            return {"success": False, "message": "Detalle no encontrado o no pertenece a esta orden", "data": None}

        if not is_admin and requesting_user_id:
            # Obtener la orden asociada al detalle para verificar permisos
            order_info = orders_collection.find_one({"_id": ObjectId(order_id)})
            if not order_info or order_info["id_user"] != requesting_user_id:
                return {"success": False, "message": "No tienes permiso para modificar este detalle", "data": None}

        result = order_details_collection.update_one(
            {"_id": ObjectId(detail_id)},
            {"$set": {"active": False, "date_updated": datetime.utcnow()}}
        )

        if result.modified_count > 0:
            totals_result = await recalculate_order_totals(order_id)
            
            response_data = {"modified_count": result.modified_count}
            if totals_result["success"]:
                response_data["order_totals"] = {
                    "subtotal": totals_result["subtotal"],
                    "taxes": totals_result["taxes"],
                    "discount": totals_result["discount"],
                    "total": totals_result["total"]
                }
            
            return {
                "success": True,
                "message": "Producto eliminado de la orden exitosamente",
                "data": response_data
            }

        return {"success": False, "message": "No se pudo eliminar el producto", "data": None}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}", "data": None}
