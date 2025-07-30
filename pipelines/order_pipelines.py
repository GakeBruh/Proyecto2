from bson import ObjectId

def get_all_orders_pipeline(skip: int = 0, limit: int = 50) -> list:
    return [
        {
            "$lookup": {
                "from": "users",
                "let": {"user_id": {"$toObjectId": "$id_user"}},  # Convertir string a ObjectId para lookup
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$user_id"]}}}
                ],
                "as": "user_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_user": "$id_user",  # Ya es string
                "user_name": {"$arrayElemAt": ["$user_info.name", 0]},
                "date": 1,
                "subtotal": 1,
                "taxes": 1,
                "discount": 1,
                "total": 1,
                "_id": 0
            }
        },
        {"$sort": {"date": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]


def get_orders_by_user_pipeline(user_id: str, skip: int = 0, limit: int = 50) -> list:
    return [
        {"$match": {"id_user": user_id}},  # Ahora id_user es string
        {
            "$lookup": {
                "from": "users",
                "let": {"user_id": {"$toObjectId": "$id_user"}},  # Convertir string a ObjectId para lookup
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$user_id"]}}}
                ],
                "as": "user_info"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_user": "$id_user",  # Ya es string
                "user_name": {"$arrayElemAt": ["$user_info.name", 0]},
                "date": 1,
                "subtotal": 1,
                "taxes": 1,
                "discount": 1,
                "total": 1,
                "_id": 0
            }
        },
        {"$sort": {"date": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]


def get_order_by_id_pipeline(order_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(order_id)}},
        {
            "$lookup": {
                "from": "users",
                "let": {"user_id": {"$toObjectId": "$id_user"}},  # Convertir string a ObjectId para lookup
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$user_id"]}}}
                ],
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "order_details",
                "let": {"order_id": {"$toString": "$_id"}},  # Convertir ObjectId a string para lookup
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$id_order", "$$order_id"]}}}
                ],
                "as": "details"
            }
        },
        {
            "$lookup": {
                "from": "order_status_record",
                "let": {"order_id": {"$toString": "$_id"}},  # Convertir ObjectId a string para lookup
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$id_order", "$$order_id"]}}}
                ],
                "as": "status_history"
            }
        },
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "id_user": "$id_user",  # Ya es string
                "user_info": {"$arrayElemAt": ["$user_info", 0]},
                "date": 1,
                "subtotal": 1,
                "taxes": 1,
                "discount": 1,
                "total": 1,
                "details": {
                    "$map": {
                        "input": "$details",
                        "as": "detail",
                        "in": {
                            "id": {"$toString": "$$detail._id"},
                            "id_producto": "$$detail.id_producto",  # Ya es string
                            "quantity": "$$detail.quantity",
                            "active": "$$detail.active",
                            "date_created": "$$detail.date_created",
                            "date_updated": "$$detail.date_updated"
                        }
                    }
                },
                "status_history": {
                    "$map": {
                        "input": "$status_history",
                        "as": "status",
                        "in": {
                            "id": {"$toString": "$$status._id"},
                            "id_status": "$$status.id_status",  # Ya es string
                            "date": "$$status.date"
                        }
                    }
                },
                "_id": 0
            }
        }
    ]


def validate_user_exists_pipeline(user_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(user_id)}},
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]


def get_order_owner_pipeline(order_id: str):
    return [
        {"$match": {"_id": ObjectId(order_id)}},
        {"$project": {"id_user": "$id_user"}},  # Ya es string, no necesita conversión
        {"$limit": 1}
    ]


def get_existing_inprogress_order_pipeline(user_id: str):
    return [
        {"$match": {"id_user": user_id}},

        {"$lookup": {
            "from": "order_status_record",
            "let": {"order_id": {"$toString": "$_id"}},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$id_order", "$$order_id"]}}},
                {"$sort": {"date": -1}},
                {"$limit": 1}
            ],
            "as": "latest_status_array"
        }},

        {"$addFields": {
            "latest_status": {"$arrayElemAt": ["$latest_status_array", 0]}
        }},

        {"$match": {"latest_status": {"$exists": True}}},

        {"$lookup": {
            "from": "order_statuses",
            "let": {"status_id": {"$toObjectId": "$latest_status.id_status"}},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$_id", "$$status_id"]}}}
            ],
            "as": "status_info"
        }},

        {"$match": {"status_info.description": "inprogress"}},

        {"$project": {
            "_id": {"$toString": "$_id"},
            "id_user": "$id_user",  # Ya es string
            "date": 1,
            "subtotal": {"$ifNull": ["$subtotal", 0.0]},
            "taxes": {"$ifNull": ["$taxes", 0.0]},
            "discount": {"$ifNull": ["$discount", 0.0]},
            "total": {"$ifNull": ["$total", 0.0]},
            "status": {"$arrayElemAt": ["$status_info.description", 0]}
        }},

        {"$limit": 1}
    ]
