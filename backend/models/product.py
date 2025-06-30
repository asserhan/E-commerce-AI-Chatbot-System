class Product:
    def __init__(self, db):
        self.collection = db.products

    def insert_many(self, products):
        self.collection.insert_many(products)

    def find(self, query=None):
        return list(self.collection.find(query or {}))

    def find_by_query_and_preferences(self, query, preferences):
        mongo_query = {}

        # Filter by 'looking_for' (e.g., 'laptop', 'gaming laptop')
        if query:
            mongo_query['category'] = {'$regex': query, '$options': 'i'}

        # Filter by brand preference
        if preferences.get('brand_preference'):
            mongo_query['brand'] = {'$regex': preferences['brand_preference'], '$options': 'i'}

        # Filter by RAM (if specified)
        if preferences.get('ram'):
            mongo_query['specs.ram'] = {'$regex': preferences['ram'], '$options': 'i'}

        # Exclude unwanted brands (e.g., if user says "no MacBook" or "no Apple")
        if preferences.get('exclude_brand'):
            mongo_query['brand'] = {'$not': {'$regex': preferences['exclude_brand'], '$options': 'i'}}

        # You can add more filters for color, price, etc.

        return list(self.collection.find(mongo_query))
