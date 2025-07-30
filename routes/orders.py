from fastapi import APIRouter, Query, HTTPException, Depends
from models.orders import CreateOrder
from models.change_order_status import ChangeOrderStatus
from controllers.orders import (
    create_order,
    get_orders,
    get_order_by_id,
    update_order_status
)
from utils.security import validate_token, validate_admin

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", summary="Crear una nueva orden")
async def create_new_order(
    order_data: CreateOrder,
    user_data: dict = Depends(validate_token)
):
    """
    Crea una nueva orden asociada al usuario autenticado.
    
    - **order_data**: Objeto con la información de la orden.
    - **user_data**: Diccionario con información del usuario autenticado.
    """
    result = await create_order(order_data, user_data["id"])
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.get("/", summary="Obtener todas las órdenes")
async def get_all_orders(
    skip: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=50, ge=1, le=100, description="Número de registros a obtener"),
    user_data: dict = Depends(validate_token)
):
    """
    Devuelve todas las órdenes del usuario o todas si es administrador.
    
    - **skip**: Cantidad de resultados a omitir.
    - **limit**: Cantidad máxima de resultados.
    - **user_data**: Diccionario con datos del usuario (admin o no).
    """
    is_admin = user_data.get("role") == "admin"
    user_id = None if is_admin else user_data["id"]

    result = await get_orders(skip=skip, limit=limit, user_id=user_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.get("/{order_id}", summary="Obtener detalles de una orden")
async def get_order_details(
    order_id: str,
    user_data: dict = Depends(validate_token)
):
    """
    Obtiene los detalles de una orden específica.
    
    - **order_id**: ID de la orden a consultar.
    - **user_data**: Información del usuario autenticado.
    """
    is_admin = user_data.get("role") == "admin"
    user_id = None if is_admin else user_data["id"]

    result = await get_order_by_id(order_id, user_id, is_admin)

    if not result["success"]:
        if result["message"] == "Orden no encontrada":
            raise HTTPException(status_code=404, detail=result["message"])
        elif "permiso" in result["message"]:
            raise HTTPException(status_code=403, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.put("/{order_id}/status", summary="Finalizar orden (cambiar a Ordered)")
async def finalize_order(
    order_id: str,
    user_data: dict = Depends(validate_token)
):
    """
    Cambia el estado de una orden a 'Ordered'.
    
    - **order_id**: ID de la orden a modificar.
    - **user_data**: Información del usuario autenticado.
    """
    result = await update_order_status(
        order_id,
        None,  # Determinar estado automáticamente
        requesting_user_id=user_data["id"],
        is_admin=False
    )

    if not result["success"]:
        if result["message"] == "Orden no encontrada":
            raise HTTPException(status_code=404, detail=result["message"])
        elif "permiso" in result["message"]:
            raise HTTPException(status_code=403, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/{order_id}/status", summary="Cambiar estado de orden como administrador")
async def change_order_status_admin(
    order_id: str,
    status_data: ChangeOrderStatus,
    _: dict = Depends(validate_admin)
):
    """
    Permite a un administrador cambiar el estado de una orden.

    - **order_id**: ID de la orden a modificar.
    - **status_data**: Objeto con el nuevo estado `id_status`.
    """
    result = await update_order_status(
        order_id,
        status_data.id_status,
        is_admin=True
    )

    if not result["success"]:
        if result["message"] == "Orden no encontrada":
            raise HTTPException(status_code=404, detail=result["message"])
        else:
            raise HTTPException(status_code=400, detail=result["message"])

    return result
