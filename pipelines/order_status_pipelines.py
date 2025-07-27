from bson import ObjectId

def validate_order_status_exists_pipeline(order_status_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(order_status_id)}},
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]



def check_duplicate_order_status_description_pipeline(description: str) -> list:
    return [
        {
            "$match": {
                "description": description.strip().lower()
            }
        },
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]


def check_duplicate_order_status_on_update_pipeline(order_status_id: str, description: str) -> list:
    return [
        {
            "$match": {
                "description": description.strip().lower(),
                "_id": {"$ne": ObjectId(order_status_id)}
            }
        },
        {"$project": {"_id": 1}},
        {"$limit": 1}
    ]



def get_all_order_statuses_pipeline() -> list:
    return [
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "description": 1,
                "_id": 0
            }
        }
    ]



def get_order_status_by_id_pipeline(order_status_id: str) -> list:
    return [
        {"$match": {"_id": ObjectId(order_status_id)}},
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "description": 1,
                "_id": 0
            }
        }
    ]
