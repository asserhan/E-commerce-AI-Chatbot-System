class Product:
    def __init__(self, db):
        self.collection = db.products

    def insert_many(self, products):
        self.collection.insert_many(products)

    def find(self, query=None):
        return list(self.collection.find(query or {}))

    def find_by_query_and_preferences(self, query, preferences):
        # Implement your matching logic here, similar to your current code
        # For now, just return all products for demo
        return list(self.collection.find({}))
