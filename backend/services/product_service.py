import re
from models.product import Product

class ProductService:
    def __init__(self, db):
        self.product_model = Product(db)
    
    def search_products_by_query(self, query, budget=None):
        # Extract budget from query if mentioned
        if not budget:
            budget = self._extract_budget_from_query(query)
        
        # Extract category from query
        category = self._extract_category_from_query(query)
        
        # Clean query for search
        clean_query = self._clean_search_query(query)
        
        # Search products
        products = self.product_model.search_products(
            query=clean_query,
            category=category,
            max_price=budget
        )
        
        return products
    
    def _extract_budget_from_query(self, query):
        # Look for price mentions like "$500", "under 1000", "around $800"
        price_patterns = [
            r'\$(\d+)',
            r'under (\d+)',
            r'around \$?(\d+)',
            r'budget of \$?(\d+)',
            r'up to \$?(\d+)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_category_from_query(self, query):
        categories = {
            'laptop': ['laptop', 'notebook', 'computer'],
            'phone': ['phone', 'smartphone', 'mobile'],
            'tablet': ['tablet', 'ipad'],
            'headphones': ['headphones', 'earbuds', 'headset'],
            'camera': ['camera', 'photography']
        }
        
        query_lower = query.lower()
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
    
    def _clean_search_query(self, query):
        # Remove price and budget related words
        clean_query = re.sub(r'\$\d+', '', query)
        clean_query = re.sub(r'under \d+', '', clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r'around \$?\d+', '', clean_query, flags=re.IGNORECASE)
        clean_query = re.sub(r'budget of \$?\d+', '', clean_query, flags=re.IGNORECASE)
        
        return clean_query.strip()
    
    def format_products_for_display(self, products):
        formatted_products = []
        
        for product in products:
            formatted_product = {
                'id': str(product['_id']),
                'name': product['name'],
                'price': product['price'],
                'description': product['description'][:200] + '...' if len(product['description']) > 200 else product['description'],
                'image_url': product.get('image_url', '/static/images/no-image.jpg'),
                'key_features': product.get('specifications', {}).get('key_features', [])
            }
            formatted_products.append(formatted_product)
        
        return formatted_products