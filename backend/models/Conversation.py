from datetime import datetime, timezone
from bson import ObjectId

class Conversation:
    def __init__(self, db):
        self.collection = db.conversations
        self.messages = db.messages

    def create(self, customer_id, session_id):
        data = {
            'customer_id': customer_id,
            'session_id': session_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'active'
        }
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def add_message(self, conversation_id, message_type, content, metadata=None):
        msg = {
            'conversation_id': conversation_id,
            'type': message_type,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.messages.insert_one(msg)

    # def get_recent_messages(self, conversation_id, limit=10):
    #     return list(self.messages.find({'conversation_id': conversation_id}).sort('timestamp', -1).limit(limit))
# Add these methods to your Conversation model class

    def get_by_session_id(self, session_id):
        """Get conversation by session_id"""
        return self.collection.find_one({'session_id': session_id})

    def get_recent_messages(self, conversation_id, limit=10):
        # Fetch from the messages collection, sorted by timestamp
        msgs = list(self.messages.find({'conversation_id': conversation_id}).sort('timestamp', 1).limit(limit))
        # Format for LLM
        return [
            {"type": msg["type"], "content": msg["content"]}
            for msg in msgs
        ]

    def update(self, conversation_id, data):
        """Update conversation data"""
        return self.collection.update_one(
            {'_id': conversation_id},
            {'$set': data}
        )