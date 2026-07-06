from products.managers import product_manager

class ProductService:

    def __init__(self, manager):
        self.manager = manager


    def add(self, product):
        self.manager.add(product)


    def get(self, product_id):
        return self.manager.get(product_id)


    def update(self, product_id, product):
        self.manager.update(product_id, product)


    def delete(self, product_id):
        self.manager.delete(product_id)



product_service = ProductService(product_manager)