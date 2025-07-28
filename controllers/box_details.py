from models.box_details import BoxDetail, BoxWithProducts, AddProductToBox
from models.catalogs import Catalog
from utils.mongodb import get_collection
from fastapi import HTTPException
from bson import ObjectId
from pipelines import (
    get_box_with_catalog_type_pipeline,
    get_box_products_pipeline,
    get_box_validation_pipeline,
    get_product_validation_pipeline,
    get_box_detail_with_product_pipeline,
    check_existing_product_in_box_pipeline
)

box_details_coll = get_collection("box_details")
catalogs_coll = get_collection("catalogs")
catalog_types_coll = get_collection("catalogtypes")
inventories_coll = get_collection("inventories")


async def get_box_with_products(box_id: str) -> BoxWithProducts:
    """Obtener información completa del box con todos sus productos"""
    try:
        # Verificar que el box existe y es de tipo "box" usando pipeline
        pipeline = get_box_with_catalog_type_pipeline(box_id)
        box_result = list(catalogs_coll.aggregate(pipeline))

        if not box_result:
            raise HTTPException(status_code=404, detail="Box no encontrado o no es de tipo box")

        box = box_result[0]

        # Obtener los productos del box usando pipeline optimizada
        products_pipeline = get_box_products_pipeline(box_id)
        products = list(box_details_coll.aggregate(products_pipeline))

        # Crear respuesta completa
        box_response = BoxWithProducts(
            id=str(box["_id"]),
            id_catalog_type=str(box["id_catalog_type"]),
            name=box["name"],
            description=box["description"],
            cost=box["cost"],
            discount=box.get("discount", 0),
            active=box.get("active", True),
            products=products
        )

        return box_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el box con productos: {str(e)}")

async def add_product_to_box(box_id: str, product_data: AddProductToBox) -> dict:
    """Agregar un producto al box"""
    try:
        # Verificar que no se esté agregando el mismo box como producto (evitar recursión)
        if product_data.id_producto == box_id:
            raise HTTPException(status_code=400, detail="No se puede agregar otra box a sí misma")

        # Validar box (existe, activo y es de tipo box) en una sola pipeline
        box_pipeline = get_box_validation_pipeline(box_id)
        box_result = list(catalogs_coll.aggregate(box_pipeline))

        if not box_result:
            raise HTTPException(status_code=404, detail="Box no encontrado, inactivo o no es de tipo box")

        box = box_result[0]

        # Validar producto (existe, activo y es de tipo producto) en una sola pipeline
        product_pipeline = get_product_validation_pipeline(product_data.id_producto)
        product_result = list(catalogs_coll.aggregate(product_pipeline))

        if not product_result:
            raise HTTPException(status_code=404, detail="Producto no encontrado, inactivo o no es de tipo producto")

        product = product_result[0]

        # Obtener inventario disponible para ese producto
        inventarios = list(inventories_coll.find({"catalog_id": product_data.id_producto}))
        total_disponible = sum(i["quantity"] for i in inventarios)

        # Verificar si el producto ya existe en el box usando pipeline
        existing_pipeline = check_existing_product_in_box_pipeline(box_id, product_data.id_producto)
        existing_result = list(box_details_coll.aggregate(existing_pipeline))

        cantidad_existente_en_box = existing_result[0]["quantity"] if existing_result else 0
        cantidad_final = cantidad_existente_en_box + product_data.quantity

        # Validar que no se exceda el inventario disponible
        if cantidad_final > total_disponible:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Stock insuficiente para el producto '{product_data.id_producto}'. "
                    f"Disponible: {total_disponible}, solicitado en total: {cantidad_final}"
                )
            )

        if existing_result:
            # Actualizar cantidad si ya existe en el box
            existing_detail = existing_result[0]
            new_quantity = existing_detail["quantity"] + product_data.quantity
            box_details_coll.update_one(
                {"_id": ObjectId(existing_detail["box_detail_id"])},
                {"$set": {"quantity": new_quantity}}
            )
            detail_id = existing_detail["box_detail_id"]
            final_quantity = new_quantity
        else:
            # Crear nuevo detalle del box
            box_detail = BoxDetail(
                id_box=box_id,
                id_producto=product_data.id_producto,
                quantity=product_data.quantity
            )
            box_detail_dict = box_detail.model_dump(exclude={"id"})
            inserted = box_details_coll.insert_one(box_detail_dict)
            detail_id = str(inserted.inserted_id)
            final_quantity = product_data.quantity

        # Retornar información del producto agregado
        return {
            "message": "Product added to box successfully",
            "box_detail_id": detail_id,
            "box_id": box_id,
            "product_id": product_data.id_producto,
            "product_name": product["name"],
            "quantity": final_quantity,
            "product_cost": product["cost"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al añadir este producto a la box: {str(e)}")

async def remove_product_from_box(box_id: str, box_detail_id: str) -> dict:
    """Remover un producto del box"""
    try:
        # Validar box y obtener detalle del box con información del producto en una sola pipeline
        box_detail_pipeline = get_box_detail_with_product_pipeline(box_id, box_detail_id)
        box_detail_result = list(box_details_coll.aggregate(box_detail_pipeline))
        
        if not box_detail_result:
            raise HTTPException(status_code=404, detail="Prudcto no encontrado en la box")

        box_detail = box_detail_result[0]

        # Eliminar el detalle del box
        result = box_details_coll.delete_one({"_id": ObjectId(box_detail_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Prudcto no encontrado en la box")

        return {
            "message": "Producto removido de la box exitosamente",
            "box_id": box_detail["id_box"],
            "product_id": box_detail["id_producto"],
            "product_name": box_detail["product_name"],
            "removed_quantity": box_detail["quantity"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al remover productos de la box: {str(e)}")
