from datetime import datetime
from bson import ObjectId
from backend.config.database import db_config

class Conversation:
    def __init__(self, db):
        self.collection = db.conversations
    
    def create_conversation(self, session_id, customer_id=None):
        """Create a new conversation"""
        conversation_data = {
            'session_id': session_id,
            'customer_id': customer_id,
            'messages': [],
            'products_discussed': [],
            'products_interested': [],
            'lead_status': 'new',  # new, qualified, interested, converted, lost
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'is_active': True,
            'customer_info_collected': False,
            'total_messages': 0
        }
        
        result = self.collection.insert_one(conversation_data)
        return str(result.inserted_id)
    
    def get_conversation_by_id(self, conversation_id):
        """Get conversation by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(conversation_id)})
        except:
            return None
    
    def get_conversation_by_session(self, session_id):
        """Get conversation by session ID"""
        return self.collection.find_one({'session_id': session_id})
    
    def add_message(self, conversation_id, message_type, content, metadata=None):
        """Add a message to conversation"""
        message = {
            'type': message_type,  # 'user' or 'bot'
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(conversation_id)},
                {
                    '$push': {'messages': message},
                    '$set': {'updated_at': datetime.now()},
                    '$inc': {'total_messages': 1}
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def add_product_discussion(self, conversation_id, product_id, action='viewed'):
        """Add product to discussed products list"""
        product_entry = {
            'product_id': product_id,
            'action': action,  # viewed, interested, requested_info
            'timestamp': datetime.now()
        }
        
        try:
            self.collection.update_one(
                {'_id': ObjectId(conversation_id)},
                {'$push': {'products_discussed': product_entry}}
            )
        except:
            pass
    
    def add_product_interest(self, conversation_id, product_id, interest_level='medium'):
        """Add product to interested products list"""
        interest_entry = {
            'product_id': product_id,
            'interest_level': interest_level,  # low, medium, high
            'timestamp': datetime.now()
        }
        
        try:
            self.collection.update_one(
                {'_id': ObjectId(conversation_id)},
                {'$push': {'products_interested': interest_entry}}
            )
        except:
            pass
    
    def update_customer_id(self, conversation_id, customer_id):
        """Update conversation with customer ID"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(conversation_id)},
                {
                    '$set': {
                        'customer_id': customer_id,
                        'customer_info_collected': True,
                        'updated_at': datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def update_lead_status(self, conversation_id, status):
        """Update lead status"""
        valid_statuses = ['new', 'qualified', 'interested', 'converted', 'lost']
        
        if status not in valid_statuses:
            return False
        
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(conversation_id)},
                {
                    '$set': {
                        'lead_status': status,
                        'updated_at': datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def get_recent_messages(self, conversation_id, limit=10):
        """Get recent messages from conversation"""
        try:
            conversation = self.collection.find_one(
                {'_id': ObjectId(conversation_id)},
                {'messages': {'$slice': -limit}}
            )
            return conversation.get('messages', []) if conversation else []
        except:
            return []
    
    def get_conversations_by_customer(self, customer_id, limit=10):
        """Get conversations by customer ID"""
        return list(
            self.collection.find({'customer_id': customer_id})
            .sort('created_at', -1)
            .limit(limit)
        )
    
    def get_all_conversations(self, limit=50, skip=0):
        """Get all conversations with pagination"""
        return list(
            self.collection.find()
            .sort('created_at', -1)
            .limit(limit)
            .skip(skip)
        )
    
    def close_conversation(self, conversation_id):
        """Mark conversation as inactive"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(conversation_id)},
                {
                    '$set': {
                        'is_active': False,
                        'updated_at': datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
        

# if __name__ == "__main__":
#     db = db_config.get_db()
#     conversation_model = Conversation(db)
#     try:
#         # Example usage
#         new_conv_id = conversation_model.create_conversation(session_id='12345')
#         print(f"New conversation created with ID: {new_conv_id}")
        
#         # Add a message
#         conversation_model.add_message(new_conv_id, 'user', 'Hello, I need help with my order.')
        
#         # Get conversation by ID
#         conv = conversation_model.get_conversation_by_id(new_conv_id)
#         print(conv)
#         # Update lead status
#         conversation_model.update_lead_status(new_conv_id, 'qualified')
#         # Get recent messages
#         recent_msgs = conversation_model.get_recent_messages(new_conv_id, limit=5)
#         print(recent_msgs)
#     except Exception as e:
#         print(f"An error occurred: {e}")