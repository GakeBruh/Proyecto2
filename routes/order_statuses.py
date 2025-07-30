from fastapi import APIRouter, HTTPException, Body, Depends
from models.order_statuses import OrderStatus
from controllers.order_statuses import (
    create_order_status,
    get_order_statuses,
    get_order_status_by_id,
    update_order_status_and_manage_inventory,
    delete_order_status
)
from utils.security import validate_admin, validate_token

router = APIRouter()

@router.post("/order-statuses", response_model=dict, tags=["Order Status"])
async def create_order_status_endpoint(
    order_status: OrderStatus,
    _: dict = Depends(validate_admin)
) -> dict:
    return await create_order_status(order_status)

@router.get("/order-statuses", tags=["Order Status"])
async def get_order_statuses_endpoint() -> dict:
    return await get_order_statuses()

@router.get("/order-statuses/{order_status_id}", tags=["Order Status"])
async def get_order_status_by_id_endpoint(order_status_id: str) -> dict:
    return await get_order_status_by_id(order_status_id)

@router.put("/order-statuses/{order_status_id}", response_model=dict, tags=["Order Status"])
async def update_order_status_endpoint(
    order_status_id: str,
    order_status: OrderStatus,
    _: dict = Depends(validate_admin)
) -> dict:
    return await update_order_status_and_manage_inventory(order_status_id, order_status)

@router.delete("/order-statuses/{order_status_id}", tags=["Order Status"])
async def delete_order_status_endpoint(
    order_status_id: str,
    _: dict = Depends(validate_admin)
) -> dict:
    return await delete_order_status(order_status_id)


@router.put("/orders/{order_id}/status", tags=["Order Status"])
async def update_order_status_order_endpoint(
    order_id: str,
    status_update: dict = Body(
        ...,
        examples={
            "example1": {
                "summary": "Ejemplo de estado nuevo",
                "value": {"new_status": "ordered"}
            }
        }
    ),
    user_data: dict = Depends(validate_token)
):
    new_status = status_update.get("new_status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Se requiere 'new_status' en el body")

    is_admin = user_data.get("role") == "admin"
    user_id = user_data.get("id")

    return await update_order_status_and_manage_inventory(order_id, new_status, user_id, is_admin)
