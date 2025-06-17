import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()



class DatabaseConfig:
    def __init__(self):
        self.client = None 
        self.db = None
        self.connect()
    
    def connect(self):
        try:
            mongodb_uri=os.getenv("MONGODB_URI" )
            db_name=os.getenv("MONGODB_DB_NAME")
            if not mongodb_uri or not db_name:
                raise ValueError("MONGODB_URI and MONGODB_DB_NAME must be set in environment variables.")
            self.client = MongoClient(mongodb_uri)
            print(f"✅MongoDB connection established successfully.")
            self.db = self.client[db_name]
            self.setup_indexes()
        except ConnectionFailure as e:
            print(f"❌Failed to connect to MongoDB: {e}")
            raise e
        
    def setup_indexes(self):
        try:
            #custom indexes 
            self.db.customers.create_index("email", unique=True)
            self.db.customers.create_index("username", unique=True)

            #product indexes
            self.db.products.create_index([("title", "text"), ("description", "text")])
            self.db.products.create_index("category")
            self.db.products.create_index("price")

            #consversatiion indexes
            self.db.conversations.create_index("session_id")
            self.db.conversations.create_index("customer_id")
            self.db.conversations.create_index("created_at")

            print("✅Indexes created successfully.")
        except Exception as e:
            print(f"❌Failed to create indexes: {e}")
            raise e

    def get_db(self):
        if self.db is None:
            raise ValueError("Database connection not established")
        return self.db

    def close_connection(self):
        if self.client:
            self.client.close()


db_config = DatabaseConfig()

# if __name__ == "__main__":
#     db = db_config.get_db()
#     print("Collections:", db.list_collection_names())

