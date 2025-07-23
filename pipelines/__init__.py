"""
Módulo de pipelines de MongoDB optimizadas
"""

from .box_pipelines import (
    get_box_validation_pipeline,
    get_box_with_catalog_type_pipeline,
    get_box_products_pipeline,
    get_product_validation_pipeline, 
    get_box_detail_with_product_pipeline,
    check_existing_product_in_box_pipeline
)


from .catalog_pipelines import (
    get_catalog_with_type_pipeline,
    get_catalogs_by_type_pipeline,
    get_all_catalogs_with_types_pipeline,
    validate_catalog_type_pipeline,
    search_catalogs_pipeline
)

from .order_pipelines import (
    get_all_orders_pipeline,
    get_orders_by_user_pipeline,
    get_order_by_id_pipeline,
    get_order_owner_pipeline,
    get_existing_inprogress_order_pipeline
)

from .order_detail_pipelines import (
    get_order_details_pipeline,
    get_order_detail_by_id_pipeline
)

__all__ = [
    # Box pipelines
    "get_box_validation_pipeline",
    "get_box_with_catalog_type_pipeline", 
    "get_box_products_pipeline",
    "get_product_validation_pipeline",
    "get_box_detail_with_product_pipeline",
    "check_existing_product_in_box_pipeline",
    
    # Catalog pipelines
    "get_catalog_with_type_pipeline",
    "get_catalogs_by_type_pipeline",
    "get_all_catalogs_with_types_pipeline",
    "validate_catalog_type_pipeline",
    "search_catalogs_pipeline",
    
    # Order pipelines  
    "get_all_orders_pipeline",
    "get_orders_by_user_pipeline",
    "get_order_by_id_pipeline",
    "get_order_owner_pipeline",
    "get_existing_inprogress_order_pipeline",
    
    # Order detail pipelines
    "get_order_details_pipeline",
    "get_order_detail_by_id_pipeline"
]
