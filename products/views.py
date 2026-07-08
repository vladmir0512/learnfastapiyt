from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from starlette import status

from users.dependencies import check_permissions
from users.permissions import Permissions
from .managers import product_manager, ProductAlreadyExistsError, ProductNotFoundError
from .services import product_service

products_router = APIRouter(prefix="/products", tags=["Продукты"])

class Product(BaseModel):
    id: int
    name: str
    price: float

@products_router.post("")
def create_product(product: Product, current_user=Depends(check_permissions([Permissions.ADD_PRODUCT]))):
    try:
        product_service.add(product)
    except ProductAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return {
        "result": f"Product {product.name} was added successfully by {current_user.email}"
    }


@products_router.get("/{product_id}")
def get_product(product_id: int, current_user=Depends(check_permissions([Permissions.VIEW_PRODUCT]))):
    try:
        return product_service.get(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@products_router.put("/{product_id}")
def update_product(product_id: int, product: Product, current_user=Depends(check_permissions([Permissions.UPDATE_PRODUCT]))):
    try:
        product_service.update(product_id, product)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


    return {"result": f"Product {product.name} was updated by {current_user.email}"}


@products_router.delete("/{product_id}")
def delete_product(product_id: int, current_user=Depends(check_permissions([Permissions.DELETE_PRODUCT]))):
    try:
        product_service.delete(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return {"result": f"Product with id {product_id} was deleted by {current_user.email}"}


