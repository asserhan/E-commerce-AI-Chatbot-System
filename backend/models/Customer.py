from datetime import datetime, timezone
from bson import ObjectId

class Customer:
    def __init__(self, db):
        self.collection = db.customers

    def create(self, data):
        data['timestamp'] = datetime.now(timezone.utc).isoformat()
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def update(self, customer_id, data):
        self.collection.update_one({'_id': ObjectId(customer_id)}, {'$set': data})

    def get_by_id(self, customer_id):
        return self.collection.find_one({'_id': ObjectId(customer_id)})

    def get_by_email(self, email):
        return self.collection.find_one({'email': email})
