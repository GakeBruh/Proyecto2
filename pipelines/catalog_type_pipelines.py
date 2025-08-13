from bson import ObjectId

def get_catalog_type_pipeline() -> list:
    """
    Pipeline para obtener todos los tipos de catálogo con conteo de productos asociados.
    """
    return [
        # Convertir _id a string para usar en el lookup
        {"$addFields": {"id": {"$toString": "$_id"}}},

        # Hacer lookup en la colección 'catalogs' para traer los productos asociados
        {
            "$lookup": {
                "from": "catalogs",
                "localField": "id",
                "foreignField": "id_catalog_type",
                "as": "products"
            }
        },

        # Contar el número de productos
        {"$addFields": {"number_of_products": {"$size": "$products"}}},

        # Seleccionar solo los campos que necesitamos
        {"$project": {"_id": 0, "id": 1, "description": 1, "active": 1, "number_of_products": 1}}
    ]


def validate_type_is_assigned_pipeline(id: str) -> list:
    """
    Pipeline para validar si un tipo de catálogo tiene productos asignados,
    y obtener el conteo de productos asociados.
    """
    return [
        # Filtrar por el id específico
        {"$match": {"_id": ObjectId(id)}},

        # Convertir _id a string para el lookup
        {"$addFields": {"id": {"$toString": "$_id"}}},

        # Traer productos asociados
        {
            "$lookup": {
                "from": "catalogs",
                "localField": "id",
                "foreignField": "id_catalog_type",
                "as": "products"
            }
        },

        # Contar productos
        {"$addFields": {"number_of_products": {"$size": "$products"}}},

        # Proyección final
        {"$project": {"_id": 0, "id": 1, "description": 1, "active": 1, "number_of_products": 1}}
    ]
