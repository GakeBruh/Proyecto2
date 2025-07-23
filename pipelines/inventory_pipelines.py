"""
Pipelines de MongoDB para operaciones con inventario
"""
from bson import ObjectId

def get_inventory_by_id_pipeline(inventory_id: str) -> list:
    """
    Pipeline para obtener un lote de inventario con información del catálogo
    """
    return [
        {"$match": {"_id": ObjectId(inventory_id)}},
        {"$addFields": {
            "catalog_obj_id": {"$toObjectId": "$catalog_id"}
        }},
        {"$lookup": {
            "from": "catalogs",
            "localField": "catalog_obj_id",
            "foreignField": "_id",
            "as": "catalog"
        }},
        {"$unwind": "$catalog"},
        {"$project": {
            "id": {"$toString": "$_id"},
            "catalog_id": {"$toString": "$catalog_id"},
            "catalog_name": "$catalog.name",
            "quantity": "$quantity",
            "batch_name": "$batch_name",
            "date": "$date"
        }}
    ]

def get_all_inventory_pipeline() -> list:
    """
    Pipeline para obtener todos los lotes de inventario con información del catálogo
    """
    return [
        {"$addFields": {
            "catalog_obj_id": {"$toObjectId": "$catalog_id"}
        }},
        {"$lookup": {
            "from": "catalogs",
            "localField": "catalog_obj_id",
            "foreignField": "_id",
            "as": "catalog"
        }},
        {"$unwind": "$catalog"},
        {"$project": {
            "id": {"$toString": "$_id"},
            "catalog_id": {"$toString": "$catalog_id"},
            "catalog_name": "$catalog.name",
            "quantity": "$quantity",
            "batch_name": "$batch_name",
            "date": "$date"
        }}
    ]

def validate_catalog_pipeline(catalog_id: str) -> list:
    """
    Pipeline para validar que un catálogo existe y está activo
    """
    return [
        {"$match": {
            "_id": ObjectId(catalog_id),
            "active": True
        }},
        {"$project": {
            "id": {"$toString": "$_id"},
            "name": "$name"
        }}
    ]

def get_total_stock_pipeline(catalog_id: str) -> list:
    """
    Pipeline para obtener el stock total (sumatoria de quantity) de un catálogo
    """
    return [
        {"$match": {"catalog_id": catalog_id}},
        {"$group": {
            "_id": "$catalog_id",
            "total_stock": {"$sum": "$quantity"}
        }},
        {"$project": {
            "catalog_id": "$_id",
            "total_stock": 1,
            "_id": 0
        }}
    ]
