from flask import Flask, request, jsonify, session
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_socketio import SocketIO
import uuid
from config import Config
from models.customer import Customer
from models.product import Product
from models.conversation import Conversation
from services.ai_service import AIService
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)
db = mongo.db

cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

customer_model = Customer(db)
product_model = Product(db)
conversation_model = Conversation(db)
ai_service = AIService()

# Use your actual MongoDB URI here
client = MongoClient(Config.MONGO_URI)
db = client["ecomerce_chatbot"]  # Use your actual database name

# Drop the unique index on 'username' if it exists
try:
    db.customers.drop_index("username_1")
    # print("Dropped unique index on 'username'.")
except Exception as e:
    print("Index 'username_1' not found or already dropped.")

# Insert fake products if not present
if product_model.collection.count_documents({}) == 0:
    product_model.insert_many([
        {
            "name": "MacBook Pro 16-inch M3",
            "brand": "Apple",
            "price": 2499.99,
            "category": "laptop",
            "description": "Powerful laptop with M3 chip, 16GB RAM, 512GB SSD. Perfect for professionals and creatives.",
            "specs": {
                "processor": "Apple M3",
                "ram": "16GB",
                "storage": "512GB SSD",
                "screen": "16-inch Retina",
                "graphics": "Integrated"
            },
            "image_url": "https://example.com/macbook-pro-m3.jpg",
            "in_stock": True,
            "rating": 4.8,
            "color": "Space Gray",
            "tags": ["professional", "creative", "premium", "mac", "apple"]
        },
        {
            "name": "Dell XPS 13 Plus",
            "brand": "Dell",
            "price": 1399.99,
            "category": "laptop",
            "description": "Ultra-thin, lightweight laptop with 12th Gen Intel i7, 16GB RAM, 1TB SSD. Great for business and travel.",
            "specs": {
                "processor": "Intel i7-1260P",
                "ram": "16GB",
                "storage": "1TB SSD",
                "screen": "13.4-inch FHD+",
                "graphics": "Intel Iris Xe"
            },
            "image_url": "https://example.com/dell-xps-13.jpg",
            "in_stock": True,
            "rating": 4.7,
            "color": "Silver",
            "tags": ["business", "ultrabook", "dell", "portable"]
        },
        {
            "name": "HP Spectre x360 14",
            "brand": "HP",
            "price": 1249.99,
            "category": "laptop",
            "description": "Convertible 2-in-1 laptop with touch screen, Intel i7, 16GB RAM, 512GB SSD. Perfect for students and professionals.",
            "specs": {
                "processor": "Intel i7-1165G7",
                "ram": "16GB",
                "storage": "512GB SSD",
                "screen": "13.5-inch OLED",
                "graphics": "Intel Iris Xe"
            },
            "image_url": "https://example.com/hp-spectre-x360.jpg",
            "in_stock": True,
            "rating": 4.6,
            "color": "Nightfall Black",
            "tags": ["2-in-1", "touchscreen", "hp", "student"]
        },
        {
            "name": "Lenovo ThinkPad X1 Carbon Gen 11",
            "brand": "Lenovo",
            "price": 1599.99,
            "category": "laptop",
            "description": "Business-class laptop with Intel i7, 16GB RAM, 1TB SSD, legendary ThinkPad keyboard.",
            "specs": {
                "processor": "Intel i7-1355U",
                "ram": "16GB",
                "storage": "1TB SSD",
                "screen": "14-inch WUXGA",
                "graphics": "Intel Iris Xe"
            },
            "image_url": "https://example.com/thinkpad-x1-carbon.jpg",
            "in_stock": True,
            "rating": 4.9,
            "color": "Black",
            "tags": ["business", "thinkpad", "lenovo", "durable"]
        },
        {
            "name": "ASUS ROG Zephyrus G14",
            "brand": "ASUS",
            "price": 1799.99,
            "category": "laptop",
            "description": "High-performance gaming laptop with AMD Ryzen 9, RTX 4060, 32GB RAM, 1TB SSD.",
            "specs": {
                "processor": "AMD Ryzen 9 7940HS",
                "ram": "32GB",
                "storage": "1TB SSD",
                "screen": "14-inch QHD",
                "graphics": "NVIDIA RTX 4060"
            },
            "image_url": "https://example.com/asus-rog-g14.jpg",
            "in_stock": True,
            "rating": 4.8,
            "color": "White",
            "tags": ["gaming", "asus", "high-performance"]
        },
        {
            "name": "Acer Swift 3 OLED",
            "brand": "Acer",
            "price": 899.99,
            "category": "laptop",
            "description": "Affordable ultrabook with Intel i5, 8GB RAM, 512GB SSD, OLED display.",
            "specs": {
                "processor": "Intel i5-1240P",
                "ram": "8GB",
                "storage": "512GB SSD",
                "screen": "14-inch OLED",
                "graphics": "Intel Iris Xe"
            },
            "image_url": "https://example.com/acer-swift-3.jpg",
            "in_stock": True,
            "rating": 4.4,
            "color": "Silver",
            "tags": ["budget", "ultrabook", "acer"]
        },
        {
            "name": "Microsoft Surface Laptop 5",
            "brand": "Microsoft",
            "price": 1299.99,
            "category": "laptop",
            "description": "Sleek, lightweight laptop with Intel i5, 16GB RAM, 512GB SSD, touchscreen.",
            "specs": {
                "processor": "Intel i5-1235U",
                "ram": "16GB",
                "storage": "512GB SSD",
                "screen": "13.5-inch PixelSense",
                "graphics": "Intel Iris Xe"
            },
            "image_url": "https://example.com/surface-laptop-5.jpg",
            "in_stock": True,
            "rating": 4.5,
            "color": "Platinum",
            "tags": ["microsoft", "surface", "touchscreen"]
        },
        {
            "name": "Razer Blade 15",
            "brand": "Razer",
            "price": 2199.99,
            "category": "laptop",
            "description": "Premium gaming laptop with Intel i7, RTX 3070, 16GB RAM, 1TB SSD, 240Hz display.",
            "specs": {
                "processor": "Intel i7-12800H",
                "ram": "16GB",
                "storage": "1TB SSD",
                "screen": "15.6-inch QHD 240Hz",
                "graphics": "NVIDIA RTX 3070"
            },
            "image_url": "https://example.com/razer-blade-15.jpg",
            "in_stock": True,
            "rating": 4.7,
            "color": "Black",
            "tags": ["gaming", "razer", "high-refresh"]
        },
        {
            "name": "Apple MacBook Air M2",
            "brand": "Apple",
            "price": 1099.99,
            "category": "laptop",
            "description": "Lightweight, fanless laptop with Apple M2 chip, 8GB RAM, 256GB SSD. Great for students and everyday use.",
            "specs": {
                "processor": "Apple M2",
                "ram": "8GB",
                "storage": "256GB SSD",
                "screen": "13.6-inch Retina",
                "graphics": "Integrated"
            },
            "image_url": "https://example.com/macbook-air-m2.jpg",
            "in_stock": True,
            "rating": 4.6,
            "color": "Starlight",
            "tags": ["student", "macbook", "apple", "lightweight"]
        },
        {
            "name": "MSI Creator Z16",
            "brand": "MSI",
            "price": 1899.99,
            "category": "laptop",
            "description": "Creator-focused laptop with Intel i9, RTX 3060, 32GB RAM, 1TB SSD, 16-inch QHD+ display.",
            "specs": {
                "processor": "Intel i9-11900H",
                "ram": "32GB",
                "storage": "1TB SSD",
                "screen": "16-inch QHD+",
                "graphics": "NVIDIA RTX 3060"
            },
            "image_url": "https://example.com/msi-creator-z16.jpg",
            "in_stock": True,
            "rating": 4.7,
            "color": "Gray",
            "tags": ["creator", "msi", "high-performance"]
        }
    ])

def extract_customer_info(message, conversation_id, existing_customer_data=None):
    # This is a simplified version; you can expand with your regex logic
    customer_data = existing_customer_data.copy() if existing_customer_data else {}
    message_lower = message.lower()

    import re
    # Name
    if not customer_data.get('name'):
        name_patterns = [
            r'(?:my name is|i am|i\'m|call me|name is)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!)',
            r'^([a-zA-Z]+)(?:\s+[a-zA-Z]+)?\s*(?:here|!|\.|\s*$)',
            r'(?:i\'m|im)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!)'
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, message, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip().title()
                if name.lower() not in ['looking', 'searching', 'need', 'want', 'here', 'hello', 'hi']:
                    customer_data['name'] = name
                    break

    # Email
    if not customer_data.get('email'):
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', message)
        if email_match:
            customer_data['email'] = email_match.group(1)

    # Phone
    if not customer_data.get('phone'):
        phone_patterns = [
            r'(?:phone|number|tel|mobile|call)\s*:?0\s*([0-9\s\-\(\)\+]{7,})',
            r'([0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{4})',
            r'(\+[0-9\s\-\(\)]{10,})',
            r'([0-9]{6,})'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, message, re.IGNORECASE)
            if phone_match:
                customer_data['phone'] = phone_match.group(1).strip()
                break

    # Looking for
    if not customer_data.get('looking_for'):
        looking_patterns = [
            r'(?:looking for|need|want|searching for|interested in)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!)',
            r'(?:buy|purchase|get)\s+(?:a|an|some)?\s*([a-zA-Z\s]+?)(?:\s|$|,|\.|!)',
            r'(laptop|computer|gaming laptop|business laptop|ultrabook|notebook)',
        ]
        for pattern in looking_patterns:
            looking_match = re.search(pattern, message, re.IGNORECASE)
            if looking_match:
                looking_for = looking_match.group(1).strip().lower()
                customer_data['looking_for'] = looking_for
                break

    # Preferences (budget, brand, color)
    if not customer_data.get('budget'):
        budget_match = re.search(r'budget\s*(?:is|of|around)?\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', message, re.IGNORECASE)
        if budget_match:
            customer_data['budget'] = f"${budget_match.group(1)}"
    if not customer_data.get('brand_preference'):
        # Positive brand preference (e.g., 'I want HP')
        for brand in ['apple', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'microsoft', 'surface', 'macbook', 'thinkpad', 'msi', 'razer']:
            if re.search(rf'\b{brand}\b', message_lower) and not re.search(rf"(don\'t want|no|avoid|not|without)\s+{brand}", message_lower):
                customer_data['brand_preference'] = brand.title()
                break
    # Exclude brand (e.g., 'I don\'t want MacBook', 'no Apple')
    if not customer_data.get('exclude_brand'):
        for brand in ['apple', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'microsoft', 'surface', 'macbook', 'thinkpad', 'msi', 'razer']:
            if re.search(rf"(don\'t want|no|avoid|not|without)\s+{brand}", message_lower):
                customer_data['exclude_brand'] = brand.title()
                break
    if not customer_data.get('color_preference'):
        for color in ['black', 'white', 'silver', 'gray', 'grey', 'gold', 'rose gold', 'blue', 'red']:
            if color in message_lower:
                customer_data['color_preference'] = color.title()
                break

    customer_data['conversation_id'] = conversation_id
    customer_data['timestamp'] = datetime.now(timezone.utc).isoformat()
    return customer_data

def get_missing_info(customer_data):
    required_fields = ['name', 'email', 'phone', 'looking_for']
    missing = [field for field in required_fields if not customer_data.get(field)]
    if not missing and not customer_data.get('budget') and not customer_data.get('brand_preference'):
        missing.append('preferences')
    return missing

def mongo_to_dict(doc):
    """Recursively convert MongoDB document to dict with string _id and nested ObjectIds."""
    if not doc:
        return doc
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, list):
        return [mongo_to_dict(item) for item in doc]
    if isinstance(doc, dict):
        doc = dict(doc)
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                doc[k] = str(v)
            elif isinstance(v, (dict, list)):
                doc[k] = mongo_to_dict(v)
        return doc
    return doc

def mongo_list_to_dicts(docs):
    return [mongo_to_dict(doc) for doc in docs]

def merge_customer_data(old, new):
    merged = old.copy()
    for k, v in new.items():
        if v not in [None, '', []]:  # Only overwrite if new value is not empty/None
            merged[k] = v
    return merged

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    session_id = data.get('session_id') or str(uuid.uuid4())

    # Get or create conversation - FIXED: Use session_id consistently
    conversation = conversation_model.get_by_session_id(session_id)
    if not conversation:
        conversation_id = conversation_model.create(
            customer_id=None,
            session_id=session_id
        )
        conversation = {'_id': conversation_id, 'session_id': session_id}
    else:
        conversation_id = conversation['_id']

    # Get existing customer data from session or database
    existing_customer_data = session.get('customer_data', {})
    
    # Add user message to conversation
    conversation_model.add_message(
        conversation_id=conversation_id,
        message_type='user',
        content=user_message
    )

    # Extract and merge customer info
    customer_data_new = extract_customer_info(user_message, conversation_id, existing_customer_data)
    customer_data = merge_customer_data(existing_customer_data, customer_data_new)

    # Save/update customer in database
    customer_id = None
    if customer_data.get('email'):
        existing = customer_model.get_by_email(customer_data['email'])
        if existing:
            updated_data = merge_customer_data(existing, customer_data)
            if '_id' in updated_data:
                del updated_data['_id']
            customer_model.update(existing['_id'], updated_data)
            customer_id = str(existing['_id'])
            customer_data = mongo_to_dict(customer_model.get_by_id(existing['_id']))
        else:
            customer_id = customer_model.create(customer_data)
            customer_data = mongo_to_dict(customer_model.get_by_id(customer_id))
        session['customer_id'] = customer_id

    # Update session with current customer data
    session['conversation_id'] = str(conversation_id)
    session['customer_data'] = mongo_to_dict(customer_data)
    session['session_id'] = session_id

    # Check what information is still missing
    missing_info = get_missing_info(customer_data)

    # Get products if we have enough info
    products = []
    if not missing_info or (customer_data.get('looking_for') and len(missing_info) <= 1):
        products = product_model.find_by_query_and_preferences(
            customer_data.get('looking_for', 'laptop'),
            customer_data
        )
        if products:
            products = mongo_list_to_dicts(products)

    if products:
        products = mongo_list_to_dicts(products)
    if customer_data:
        customer_data = mongo_to_dict(customer_data)

    # Generate AI response with current context
    ai_response_data = ai_service.generate_response(
        user_message=user_message,
        customer_info=customer_data,
        products=products,
        missing_info=missing_info,
        conversation_history=conversation_model.get_recent_messages(conversation_id, limit=5)
    )

    # Merge extracted fields from LLM into customer_data
    if 'extracted_fields' in ai_response_data:
        customer_data = merge_customer_data(customer_data, ai_response_data['extracted_fields'])

    # If we now have an email, update or create the customer in DB
    if customer_data.get('email'):
        existing = customer_model.get_by_email(customer_data['email'])
        if existing:
            updated_data = merge_customer_data(existing, customer_data)
            if '_id' in updated_data:
                del updated_data['_id']
            customer_model.update(existing['_id'], updated_data)
            customer_id = str(existing['_id'])
            customer_data = mongo_to_dict(customer_model.get_by_id(existing['_id']))
        else:
            customer_id = customer_model.create(customer_data)
            customer_data = mongo_to_dict(customer_model.get_by_id(customer_id))
        session['customer_id'] = customer_id

    # Update session with the latest customer_data
    session['customer_data'] = mongo_to_dict(customer_data)

    # Check what information is still missing
    missing_info = get_missing_info(customer_data)

    # Get products if we have enough info
    products = []
    if not missing_info or (customer_data.get('looking_for') and len(missing_info) <= 1):
        products = product_model.find_by_query_and_preferences(
            customer_data.get('looking_for', 'laptop'),
            customer_data
        )
        if products:
            products = mongo_list_to_dicts(products)

    if products:
        products = mongo_list_to_dicts(products)
    if customer_data:
        customer_data = mongo_to_dict(customer_data)

    # Add bot response to conversation
    conversation_model.add_message(
        conversation_id=conversation_id,
        message_type='bot',
        content=ai_response_data['response']
    )

    response_data = {
        'response': ai_response_data['response'],
        'products': products[:3] if products else [],
        'session_id': session_id,
        'needs_customer_info': ai_response_data.get('needs_customer_info', False),
        'customer_info': customer_data if customer_data else None,
        'missing_info': missing_info,
        'conversation_id': str(conversation_id)
    }

    return jsonify(response_data)

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    session.clear()
    return jsonify({'message': 'Conversation reset'})

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        print("🤖 E-commerce AI Chatbot CLI")
        print("Type your message and press Enter. Type 'exit' to quit.\n")
        session_id = str(uuid.uuid4())
        session_data = {}

        while True:
            user_input = input("You: ")
            if user_input.lower() in ("exit", "quit"):
                break

            # Simulate a POST request to /api/chat
            with app.test_client() as client:
                response = client.post("/api/chat", json={
                    "message": user_input,
                    "session_id": session_id
                })
                data = response.get_json()
                print("🤖 AI:", data.get("response", "(no response)"))

                if data.get("products"):
                    print("\n📦 Product Recommendations:")
                    for i, product in enumerate(data["products"], 1):
                        print(f"  {i}. {product['name']} - ${product['price']} ({product['color']})")

                if data.get("missing_info"):
                    print(f"📝 Still need: {', '.join(data['missing_info'])}")

    else:
        app.run(debug=True, port=5001)