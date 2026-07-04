from fastapi import APIRouter
from pydantic import BaseModel

from .managers import product_manager

products_router = APIRouter(prefix="/products", tags=["Продукты"])

class Product(BaseModel):
    id: int
    name: str
    price: float

@products_router.post("")
def create_product(product: Product):
    product_manager.add_product(product)
    return {"result": f"Product {product.name} was added successfully"}


@products_router.get("/{product_id}")
def get_product(product_id: int):
    return product_manager.get_product(product_id)


@products_router.put("")
def update_product(product_id: int, product: Product):
    product_manager.update_product(product_id, product)
    return {"result": f"Product {product.name} was updated"}


@products_router.delete("/{product_id}")
def delete_product(product_id: int):
    product_manager.delete_product(product_id)
    return {"result": f"Product with id {product_id} was deleted"}


