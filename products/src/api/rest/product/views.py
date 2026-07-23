from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.permissions import Permissions
from core.product.services import product_service
from api.rest.decorators import check_permissions_decorator
from dependencies import get_current_user
from api.rest.product.decorators import handle_product_errors

products_router = APIRouter(prefix="/products", tags=["Продукты"])

class Product(BaseModel):
    id: int
    name: str
    price: float

@products_router.post("")
@check_permissions_decorator([Permissions.ADD_PRODUCT.value])
@handle_product_errors
async def create_product(product: Product, current_user=Depends(get_current_user)):
    product_service.add(product)
    return {
        "result": f"Product {product.name} was added successfully by {current_user.email}"
    }



@products_router.get("/{product_id}")
@check_permissions_decorator([Permissions.VIEW_PRODUCT.value])
@handle_product_errors
async def get_product(product_id: int, current_user=Depends(get_current_user)):
    return product_service.get(product_id)


@products_router.put("/{product_id}")
@check_permissions_decorator([Permissions.UPDATE_PRODUCT.value])
@handle_product_errors
async def update_product(product_id: int, product: Product, current_user=Depends(get_current_user)):
    product_service.update(product_id, product)
    return {"result": f"Product {product.name} was updated by {current_user.email}"}


@products_router.delete("/{product_id}")
@check_permissions_decorator([Permissions.DELETE_PRODUCT.value])
@handle_product_errors
async def delete_product(product_id: int, current_user=Depends(get_current_user)):
    product_service.delete(product_id)
    return {"result": f"Product with id {product_id} was deleted by {current_user.email}"}


