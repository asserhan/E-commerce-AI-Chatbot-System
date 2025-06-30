from datetime import datetime
from bson import ObjectId # Import ObjectId for MongoDB document IDs
import re # Import regex for email validation
from pymongo import TEXT
from config.database import db_config



class Product:
    def __init__(self, db):
        self.collection = db.products
        self._ensure_text_index() 
    
    def _ensure_text_index(self):
        """Ensure text index exists for search functionality"""
        try:
            self.collection.create_index(
                [("name", TEXT), ("description", TEXT), ("category", TEXT)]
            )
        except:
            pass
    def create_product(self,name,description,price,category,specifications=None,image_url=None,sku=None):
        """Create a new product"""
        product_data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "specifications": specifications or {},
            "image_url": image_url,
            "sku": sku,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "in_stock": True,
            "view_count": 0,
            "interest_count": 0
        }
        
        result = self.collection.insert_one(product_data)
        return str(result.inserted_id)
    def get_product_by_id(self, product_id):
        """Get a product by its ID"""
        try:
            return self.collection.find_one({"_id": ObjectId(product_id)})
        except:
            return None

    def search_products(self, query=None,category=None,min_price=None,max_price=None,limit=10):
        """Search for products with filters"""
        filters = {'in_stock': True}
        # Apply category filter if provided
        if category:
            filters['category'] = {'$regex': category, '$options': 'i'}
        # Apply price range filter if provided
        price_filters = {}
        if min_price is not None:
            price_filters['$gte'] = float(min_price)
        if max_price is not None:
            price_filters['$lte'] = float(max_price)
        if price_filters:
            filters['price'] = price_filters
        # Apply text search if query is provided
        if query:
            filters['$text'] = {'$search': query}
            cursor = self.collection.find(
                filters,
                {'score': {'$meta': 'textScore'}}
            ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
        else:
            cursor = self.collection.find(filters).sort('created_at', -1).limit(limit)
        
        return list(cursor)
    
    def get_products_by_category(self, category, limit=10):
        """Get products by category"""
        return list(
            self.collection.find({
                'category': {'$regex': category, '$options': 'i'},
                'in_stock': True
            }).limit(limit)
        )
    
    def get_featured_products(self, limit=6):
        """Get featured products (most viewed or highest interest)"""
        return list(
            self.collection.find({'in_stock': True})
            .sort([('interest_count', -1), ('view_count', -1)])
            .limit(limit)
        )
    
    def increment_view_count(self, product_id):
        """Increment product view count"""
        try:
            self.collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$inc': {'view_count': 1}}
            )
        except:
            pass
    
    def increment_interest_count(self, product_id):
        """Increment product interest count"""
        try:
            self.collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$inc': {'interest_count': 1}}
            )
        except:
            pass
    
    def update_product(self, product_id, update_data):
        """Update product information"""
        update_data['updated_at'] = datetime.utcnow()
        
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def get_all_products(self, limit=50, skip=0):
        """Get all products with pagination"""
        return list(
            self.collection.find()
            .sort('created_at', -1)
            .limit(limit)
            .skip(skip)
        )
    
    def get_categories(self):
        """Get all unique product categories"""
        return self.collection.distinct('category')
    

# if __name__ == "__main__":
   
#     from config.database import db_config
#     db = db_config.get_db()
#     product_model = Product(db)

#     try:
#         product_id = product_model.create_product(
#             name="Sample Product",
#             description="This is a sample product.",
#             price=19.99,
#             category="Electronics",
#             specifications={"color": "black", "size": "medium"},
#             image_url="http://example.com/image.jpg",
#             sku="SP-001"
#         )
#         print(f"Product created with ID: {product_id}")
#     except ValueError as e:
#         print(f"Error creating product: {e}")