from bson import ObjectId

def get_inventory_by_id_pipeline(inventory_id: str) -> list:
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
            "_id": 0,
            "id": {"$toString": "$_id"},
            "catalog_id": {"$toString": "$catalog_id"},
            "catalog_name": "$catalog.name",
            "quantity": "$quantity",
            "batch_name": "$batch_name",
            "entry_date": {
                "$cond": [
                    {"$eq": [{"$type": "$entry_date"}, "string"]},
                    "$entry_date",
                    {"$dateToString": {"format": "%Y-%m-%d", "date": "$entry_date"}}
                ]
            }
        }}
    ]


def get_all_inventory_pipeline(skip: int = 0, limit: int = 10) -> list:

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
            "_id": 0,
            "id": {"$toString": "$_id"},
            "catalog_id": {"$toString": "$catalog_id"},
            "catalog_name": "$catalog.name",
            "quantity": "$quantity",
            "batch_name": "$batch_name",
            "entry_date": {
                "$cond": [
                    {"$eq": [{"$type": "$entry_date"}, "string"]},
                    "$entry_date",
                    {"$dateToString": {"format": "%Y-%m-%d", "date": "$entry_date"}}
                ]
            }
        }},
        {"$skip": skip},
        {"$limit": limit}
    ]


def validate_catalog_pipeline(catalog_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(catalog_id), "active": True}},
        {"$project": {
            "id": {"$toString": "$_id"},
            "name": "$name"
        }}
    ]

def get_total_stock_pipeline(catalog_id: str) -> list:
    return [
        {"$match": {"catalog_id": catalog_id}},
        {"$group": {
            "_id": "$catalog_id",
            "total_stock": {"$sum": "$quantity"}
        }},
        {"$addFields": {
            "catalog_obj_id": {"$toObjectId": "$_id"}
        }},
        {"$lookup": {
            "from": "catalogs",
            "localField": "catalog_obj_id",
            "foreignField": "_id",
            "as": "catalog"
        }},
        {"$unwind": "$catalog"},
        {"$project": {
            "catalog_id": "$_id",
            "catalog_name": "$catalog.name",
            "total_stock": 1,
            "_id": 0
        }}
    ]
