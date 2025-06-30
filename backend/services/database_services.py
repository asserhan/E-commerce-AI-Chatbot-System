from config.database import db_config
from models.Conversation import Conversation
from models.Customer import Customer
from models.product import Product

class DatabaseService:
    def __init__(self):
        self.db = db_config.get_database()
        self.customer_model = Customer(self.db)
        self.product_model = Product(self.db)
        self.conversation_model = Conversation(self.db)
    
    def get_customer_model(self):
        return self.customer_model
    
    def get_product_model(self):
        return self.product_model
    
    def get_conversation_model(self):
        return self.conversation_model
    

    def health_check(self):
        """Check if the database connection is healthy"""
        try:
            self.db.command("ping")
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            stats = {
                'customers': self.db.customers.count_documents({}),
                'products': self.db.products.count_documents({}),
                'conversations': self.db.conversations.count_documents({}),
                'active_conversations': self.db.conversations.count_documents({'is_active': True})
            }
            return stats
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}

db_service = DatabaseService()