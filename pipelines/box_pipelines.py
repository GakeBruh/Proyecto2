"""
Pipelines de MongoDB para operaciones con boxes
"""
from bson import ObjectId

def get_box_validation_pipeline(box_id: str) -> list:
    """
    Pipeline para validar que un box existe, está activo y es de tipo 'box'
    """
    return [
        {"$match": {"_id": ObjectId(box_id)}},
        {"$addFields": {
            "id_catalog_type_obj": {"$toObjectId": "$id_catalog_type"}
        }},
        {"$lookup": {
            "from": "catalogtypes",
            "localField": "id_catalog_type_obj",
            "foreignField": "_id",
            "as": "catalog_type"
        }},
        {"$match": {
            "catalog_type.description": {"$regex": "^box$", "$options": "i"},
            "active": True
        }}
    ]

def get_box_with_catalog_type_pipeline(box_id: str) -> list:
    """
    Pipeline para obtener un box con información del catalog type
    (sin filtro de activo para casos de solo lectura)
    """
    return [
        {"$match": {"_id": ObjectId(box_id)}},
        {"$addFields": {
            "id_catalog_type_obj": {"$toObjectId": "$id_catalog_type"}
        }},
        {"$lookup": {
            "from": "catalogtypes",
            "localField": "id_catalog_type_obj",
            "foreignField": "_id",
            "as": "catalog_type"
        }},
        {"$match": {
            "catalog_type.description": {"$regex": "^box$", "$options": "i"}
        }}
    ]

def get_box_products_pipeline(box_id: str) -> list:
    """
    Pipeline para obtener todos los productos de un box con información completa
    """
    return [
        {"$match": {"id_box": box_id}},
        {"$addFields": {
            "id_producto_obj": {"$toObjectId": "$id_producto"}
        }},
        {"$lookup": {
            "from": "catalogs",
            "localField": "id_producto_obj",
            "foreignField": "_id",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"},
        {"$project": {
            "_id": 0,
            "box_detail_id": {"$toString": "$_id"},
            "id_producto": {"$toString": "$id_producto"},
            "quantity": "$quantity",
            "product_name": "$product_info.name",
            "product_description": "$product_info.description",
            "product_cost": "$product_info.cost",
            "product_active": "$product_info.active"
        }}
    ]

def get_product_validation_pipeline(product_id: str) -> list:
    """
    Pipeline para validar que un producto existe y está activo
    """
    return [
        {"$match": {
            "_id": ObjectId(product_id),
            "active": True
        }},
        {"$addFields": {
            "id_catalog_type_obj": {"$toObjectId": "$id_catalog_type"}
        }},
        {"$lookup": {
            "from": "catalogtypes",
            "localField": "id_catalog_type_obj",
            "foreignField": "_id",
            "as": "catalog_type"
        }},
        {"$match": {
            "catalog_type.description": {"$regex": "^products?$", "$options": "i"}
        }}
    ]


def get_box_detail_with_product_pipeline(box_id: str, box_detail_id: str) -> list:
    """
    Pipeline para obtener un box detail específico con información del producto
    """
    return [
        {"$match": {
            "_id": ObjectId(box_detail_id),
            "id_box": box_id
        }},
        {"$addFields": {
            "id_producto_obj": {"$toObjectId": "$id_producto"}
        }},
        {"$lookup": {
            "from": "catalogs",
            "localField": "id_producto_obj",
            "foreignField": "_id",
            "as": "product_info"
        }},
        {"$unwind": "$product_info"},
        {"$project": {
            "box_detail_id": {"$toString": "$_id"},
            "id_box": "$id_box",
            "id_producto": {"$toString": "$id_producto"},
            "quantity": "$quantity",
            "product_name": "$product_info.name",
            "product_cost": "$product_info.cost"
        }}
    ]

def check_existing_product_in_box_pipeline(box_id: str, product_id: str) -> list:
    """
    Pipeline para verificar si un producto ya existe en un box
    """
    return [
        {"$match": {
            "id_box": box_id,
            "id_producto": product_id
        }},
        {"$project": {
            "box_detail_id": {"$toString": "$_id"},
            "quantity": "$quantity"
        }}
    ]
