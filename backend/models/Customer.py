from datetime import datetime
from pymongo.errors import DuplicateKeyError
from bson import ObjectId # Import ObjectId for MongoDB document IDs
import re # Import regex for email validation

class Customer:
    def __init__(self,db):
        self.collection = db.customers
    
    def create_customer(self,useraname, email, phone_number):

        if not self.validate_email(email):
            raise ValueError("Invalid email format")
        if not self.validate_phone_number(phone_number):
            raise ValueError("Invalid phone number format")
        
        customer_data = {
            "username": useraname,
            "email": email,
            "phone_number": phone_number,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "active",
            "total_conversations": 0,
            "last_conversation_date": None
        }
        try:
            result = self.collection.insert_one(customer_data)
            return str(result.inserted_id)  # Return the inserted document ID as a string
        except DuplicateKeyError:
            raise ValueError("Customer with this email already exists")
    #username and email should be unique
    def get_customer_by_email(self,email):
        customer = self.collection.find_one({"email": email})
        if customer:
            customer["_id"] = str(customer["_id"])
        return customer
    
    def get_customer_by_username(self,username):
        customer = self.collection.find_one({"username": username})
        if customer:
            customer["_id"] = str(customer["_id"])
        return customer
    
    def get_customer_by_id(self, customer_id):
        try:
           return self.collection.find_one({"_id": ObjectId(customer_id)})
        except:
            return None
        
    def update_customer(self, customer_id, update_data):
        update_data["updated_at"] = datetime.now()
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0 # Check if any document was modified
        except:
            return False
    def get_all_customers(self):
        customers = list(self.collection.find())
        for customer in customers:
            customer["_id"] = str(customer["_id"])
        return customers
    
    def validate_email(self, email):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None
    def validate_phone_number(self, phone_number):
        phone_regex = r"^\+?[1-9]\d{1,14}$"
        return re.match(phone_regex, phone_number) is not None
    
    def delete_customer(self, customer_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(customer_id)})
            return result.deleted_count > 0  # Check if any document was deleted
        except:
            return False
    def increment_conversation_count(self, customer_id):
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(customer_id)},
                {"$inc": {"total_conversations": 1}, "$set": {"last_conversation_date": datetime.now()}}
            )
            return result.modified_count > 0  # Check if any document was modified
        except:
            return False

#test code
if __name__ == "__main__":
    from backend.config.database import db_config
    db = db_config.get_db()
    customer_model = Customer(db)
    
    # Example usage
    try:
        customer_id = customer_model.create_customer("john_doe", "hh@gmail.com", "+1234567890")
        print(f"Customer created with ID: {customer_id}")
    except ValueError as e:
        print(f"Error creating customer: {e}")
    # Fetch customer by email