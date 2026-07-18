from products.exceptions import ProductAlreadyExistsError, ProductNotFoundError


class ProductManager:
    def __init__(self):
        self.products = {}

    def add(self, product):
        if self._is_product_exist(product.id):
            raise ProductAlreadyExistsError("Product already exists")
        self.products[product.id] = product

    def get(self, product_id):
        if not self._is_product_exist(product_id):
            raise ProductNotFoundError("Product not found")
        return self.products[product_id]

    def update(self, product_id, product):
        if not self._is_product_exist(product_id):
            raise ProductNotFoundError("Product not found")
        self.products[product_id] = product

    def delete(self, product_id):
        if not self._is_product_exist(product_id):
            raise ProductNotFoundError("Product not found")
        del self.products[product_id]

    def _is_product_exist(self, product_id):
        return product_id in self.products


product_manager = ProductManager()