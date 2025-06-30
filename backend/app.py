from flask import Flask, request, jsonify, session
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import uuid
import re
from datetime import datetime

# Enhanced Mock services for demonstration
class MockAIService:
    def __init__(self, github_token=None):
        self.github_token = github_token
    
    def generate_response(self, user_message, customer_info=None, products=None, missing_info=None):
        # If we have missing info, ask for it
        if missing_info:
            return self._ask_for_missing_info(missing_info, customer_info)
        
        # If we have complete customer info but no products yet, search for products
        if customer_info and self._is_customer_info_complete(customer_info) and not products:
            return {
                'response': f"Perfect! Thank you {customer_info.get('name', '')} for providing all your information. Let me search for the best products based on your preferences...",
                'needs_customer_info': False,
                'search_products': True
            }
        
        # If we have complete info and products, show recommendations
        if customer_info and products and self._is_customer_info_complete(customer_info):
            return self._generate_product_recommendations(customer_info, products)
        
        # Default response for unclear messages
        return {
            'response': "I'd be happy to help you find the perfect products! Let me start by getting some information about you.",
            'needs_customer_info': True
        }
    
    def _is_customer_info_complete(self, customer_info):
        required_fields = ['name', 'email', 'phone', 'looking_for']
        return all(field in customer_info and customer_info[field] for field in required_fields)
    
    def _ask_for_missing_info(self, missing_info, customer_info=None):
        name = customer_info.get('name', '') if customer_info else ''
        greeting = f"Hi {name}! " if name else "Hi there! "
        
        if 'name' in missing_info:
            return {
                'response': f"{greeting}Welcome to our store! To help you find the perfect products, I'll need some information. Let's start with your name - what should I call you?",
                'needs_customer_info': True
            }
        elif 'email' in missing_info:
            return {
                'response': f"{greeting}Great! Now I'll need your email address to send you product recommendations and updates.",
                'needs_customer_info': True
            }
        elif 'phone' in missing_info:
            return {
                'response': f"{greeting}Perfect! Could you also provide your phone number? This helps us contact you about your orders.",
                'needs_customer_info': True
            }
        elif 'looking_for' in missing_info:
            return {
                'response': f"{greeting}Almost done! What type of product are you looking for today? (e.g., laptop, gaming laptop, business laptop, etc.)",
                'needs_customer_info': True
            }
        elif 'preferences' in missing_info:
            return {
                'response': f"{greeting}Great! To find the best match, could you tell me about your preferences? For example:\n- What's your budget range?\n- Any preferred brand or color?\n- Any specific features you need?",
                'needs_customer_info': True
            }
        
        return {
            'response': f"{greeting}I need a bit more information to help you better. Could you provide the missing details?",
            'needs_customer_info': True
        }
    
    def _generate_product_recommendations(self, customer_info, products):
        name = customer_info.get('name', 'there')
        looking_for = customer_info.get('looking_for', 'products')
        budget = customer_info.get('budget', '')
        
        response = f"Excellent, {name}! Based on your request for {looking_for}"
        if budget:
            response += f" within your budget of {budget}"
        response += ", I found some fantastic options for you. Here are my top recommendations:"
        
        if products:
            for i, product in enumerate(products[:3], 1):
                response += f"\n\n{i}. **{product['name']}** - ${product['price']}\n   {product['description']}"
                
                # Add personalized notes based on preferences
                if customer_info.get('brand_preference'):
                    if customer_info['brand_preference'].lower() in product['name'].lower():
                        response += f"\n   ✨ This matches your preferred brand!"
        
        response += f"\n\nWhich of these {looking_for} interests you the most? I can provide more details or help you with the purchase process!"
        
        return {
            'response': response,
            'needs_customer_info': False
        }

class MockProductService:
    def __init__(self, db):
        self.db = db
        # Enhanced laptop database with more variety
        self.laptops = [
            {
                "id": "lap001",
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
                "id": "lap002", 
                "name": "Dell XPS 13 Plus",
                "brand": "Dell",
                "price": 1299.99,
                "category": "laptop",
                "description": "Ultra-portable laptop with Intel i7, 16GB RAM, 256GB SSD. Great for business and travel.",
                "specs": {
                    "processor": "Intel Core i7-1260P",
                    "ram": "16GB",
                    "storage": "256GB SSD",
                    "screen": "13.4-inch 4K",
                    "graphics": "Intel Iris Xe"
                },
                "image_url": "https://example.com/dell-xps-13.jpg",
                "in_stock": True,
                "rating": 4.6,
                "color": "Platinum Silver",
                "tags": ["business", "portable", "premium", "ultrabook"]
            },
            {
                "id": "lap003",
                "name": "ASUS ROG Strix G15",
                "brand": "ASUS",
                "price": 1599.99,
                "category": "laptop",
                "description": "Gaming laptop with AMD Ryzen 7, 16GB RAM, RTX 4060, 512GB SSD. Built for gaming performance.",
                "specs": {
                    "processor": "AMD Ryzen 7 7735HS",
                    "ram": "16GB DDR5",
                    "storage": "512GB SSD",
                    "screen": "15.6-inch 144Hz",
                    "graphics": "RTX 4060"
                },
                "image_url": "https://example.com/asus-rog-strix.jpg",
                "in_stock": True,
                "rating": 4.7,
                "color": "Eclipse Gray",
                "tags": ["gaming", "performance", "ryzen", "rtx"]
            },
            {
                "id": "lap004",
                "name": "HP Pavilion 15",
                "brand": "HP",
                "price": 699.99,
                "category": "laptop",
                "description": "Budget-friendly laptop with Intel i5, 8GB RAM, 256GB SSD. Perfect for students and basic use.",
                "specs": {
                    "processor": "Intel Core i5-1135G7",
                    "ram": "8GB",
                    "storage": "256GB SSD",
                    "screen": "15.6-inch HD",
                    "graphics": "Intel Iris Xe"
                },
                "image_url": "https://example.com/hp-pavilion-15.jpg",
                "in_stock": True,
                "rating": 4.2,
                "color": "Natural Silver",
                "tags": ["budget", "student", "basic", "affordable"]
            }
        ]
    
    def search_products_by_query_and_preferences(self, query, customer_preferences=None):
        query_lower = query.lower()
        matching_products = []
        
        # Search by tags, name, brand, or description
        for laptop in self.laptops:
            score = 0
            
            # Basic matching
            if (any(tag in query_lower for tag in laptop['tags']) or
                laptop['name'].lower() in query_lower or
                laptop['brand'].lower() in query_lower or
                any(word in laptop['description'].lower() for word in query_lower.split())):
                score += 10
            
            # Preference matching
            if customer_preferences:
                # Budget matching
                if customer_preferences.get('budget'):
                    try:
                        budget_match = re.search(r'(\d+)', customer_preferences['budget'])
                        if budget_match:
                            budget = float(budget_match.group(1))
                            if laptop['price'] <= budget:
                                score += 5
                    except:
                        pass
                
                # Brand preference
                if customer_preferences.get('brand_preference'):
                    if customer_preferences['brand_preference'].lower() in laptop['brand'].lower():
                        score += 8
                
                # Color preference
                if customer_preferences.get('color_preference'):
                    if customer_preferences['color_preference'].lower() in laptop['color'].lower():
                        score += 3
            
            if score > 0:
                laptop_with_score = laptop.copy()
                laptop_with_score['match_score'] = score
                matching_products.append(laptop_with_score)
        
        # Sort by score and return top matches
        matching_products.sort(key=lambda x: x['match_score'], reverse=True)
        
        # If no specific matches, return all laptops for laptop queries
        if 'laptop' in query_lower and not matching_products:
            matching_products = self.laptops
            
        return matching_products[:5]
    
    def format_products_for_display(self, products):
        formatted = []
        for product in products:
            formatted.append({
                'id': product['id'],
                'name': product['name'],
                'brand': product['brand'],
                'price': product['price'],
                'description': product['description'],
                'specs': product['specs'],
                'image_url': product['image_url'],
                'rating': product['rating'],
                'color': product.get('color', 'Standard'),
                'in_stock': product['in_stock']
            })
        return formatted

class MockCustomerService:
    def __init__(self, db):
        self.db = db
        self.customers = {}  # In-memory storage for demo
    
    def process_customer_info(self, message, conversation_id, existing_customer_data=None):
        # Start with existing data or empty dict
        customer_data = existing_customer_data.copy() if existing_customer_data else {}
        message_lower = message.lower()
        
        # Extract name
        if not customer_data.get('name'):
            name_patterns = [
                r'(?:my name is|i am|i\'m|call me|name is)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!)',
                r'^([a-zA-Z]+)(?:\s+[a-zA-Z]+)?\s*(?:here|!|\.|\s*$)',  # Name at start
                r'(?:i\'m|im)\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!)'
            ]
            
            for pattern in name_patterns:
                name_match = re.search(pattern, message, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip().title()
                    # Filter out common words that aren't names
                    if name.lower() not in ['looking', 'searching', 'need', 'want', 'here', 'hello', 'hi']:
                        customer_data['name'] = name
                        break
        
        # Extract email
        if not customer_data.get('email'):
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', message)
            if email_match:
                customer_data['email'] = email_match.group(1)
        
        # Extract phone
        if not customer_data.get('phone'):
            phone_patterns = [
                r'(?:phone|number|tel|mobile|call)\s*:?\s*([0-9\s\-\(\)\+]{7,})',
                r'([0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{4})',  # US format
                r'(\+[0-9\s\-\(\)]{10,})',  # International format
                r'([0-9]{6,})'  # Simple number pattern for cases like "56789" or "798990809"
            ]
            
            for pattern in phone_patterns:
                phone_match = re.search(pattern, message, re.IGNORECASE)
                if phone_match:
                    customer_data['phone'] = phone_match.group(1).strip()
                    break
        
        # Extract what they're looking for
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
        
        # Extract preferences
        self._extract_preferences(message, customer_data)
        
        # Store customer data
        if customer_data:
            customer_data['conversation_id'] = conversation_id
            customer_data['timestamp'] = datetime.now().isoformat()
            self.customers[conversation_id] = customer_data
        
        return customer_data
    
    def _extract_preferences(self, message, customer_data):
        message_lower = message.lower()
        
        # Extract budget
        if not customer_data.get('budget'):
            budget_patterns = [
                r'budget\s*(?:is|of|around)?\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'under\s*\$?(\d+(?:,\d{3})*)',
                r'less than\s*\$?(\d+(?:,\d{3})*)',
                r'around\s*\$?(\d+(?:,\d{3})*)',
                r'\$(\d+(?:,\d{3})*)'
            ]
            
            for pattern in budget_patterns:
                budget_match = re.search(pattern, message, re.IGNORECASE)
                if budget_match:
                    customer_data['budget'] = f"${budget_match.group(1)}"
                    break
        
        # Extract brand preference
        if not customer_data.get('brand_preference'):
            brands = ['apple', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'microsoft', 'surface', 'macbook', 'thinkpad']
            for brand in brands:
                if brand in message_lower:
                    customer_data['brand_preference'] = brand.title()
                    break
        
        # Extract color preference
        if not customer_data.get('color_preference'):
            colors = ['black', 'white', 'silver', 'gray', 'grey', 'gold', 'rose gold', 'blue', 'red']
            for color in colors:
                if color in message_lower:
                    customer_data['color_preference'] = color.title()
                    break
    
    def get_missing_info(self, customer_data):
        required_fields = ['name', 'email', 'phone', 'looking_for']
        missing = []
        
        for field in required_fields:
            if not customer_data.get(field):
                missing.append(field)
        
        # Check for preferences after basic info is collected
        if not missing and not customer_data.get('budget') and not customer_data.get('brand_preference'):
            missing.append('preferences')
        
        return missing

class MockConversation:
    def __init__(self, db):
        self.db = db
        self.conversations = {}
        self.messages = {}
    
    def create_conversation(self, customer_id=None, session_id=None):
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            'id': conversation_id,
            'customer_id': customer_id,
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        self.messages[conversation_id] = []
        return conversation_id
    
    def add_message(self, conversation_id, message_type, content, metadata=None):
        if conversation_id not in self.messages:
            self.messages[conversation_id] = []
        
        message = {
            'id': str(uuid.uuid4()),
            'conversation_id': conversation_id,
            'type': message_type,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        self.messages[conversation_id].append(message)
        return message['id']
    
    def get_recent_messages(self, conversation_id, limit=10):
        if conversation_id not in self.messages:
            return []
        return self.messages[conversation_id][-limit:]

# Global storage for CLI session persistence
CLI_SESSION_STORAGE = {
    'conversation_id': None,
    'customer_data': {}
}

# Config
class Config:
    SECRET_KEY = 'your-secret-key-here'
    GITHUB_TOKEN = 'mock-token'
    MONGO_URI = 'mongodb://localhost:27017/ecommerce'

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

ai_service = MockAIService(app.config['GITHUB_TOKEN'])
product_service = MockProductService(None)
customer_service = MockCustomerService(None)
conversation_model = MockConversation(None)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id') or str(uuid.uuid4())
        use_cli_storage = data.get('use_cli_storage', False)  # Flag for CLI mode

        # Get or create conversation
        if use_cli_storage:
            # Use global CLI storage for persistence
            conversation_id = CLI_SESSION_STORAGE['conversation_id']
            if not conversation_id:
                conversation_id = conversation_model.create_conversation(
                    customer_id=None,
                    session_id=session_id
                )
                CLI_SESSION_STORAGE['conversation_id'] = conversation_id
            existing_customer_data = CLI_SESSION_STORAGE['customer_data']
        else:
            # Use Flask session for web requests
            conversation_id = session.get('conversation_id')
            if not conversation_id:
                conversation_id = conversation_model.create_conversation(
                    customer_id=None,
                    session_id=session_id
                )
                session['conversation_id'] = conversation_id
                session['customer_data'] = {}
            existing_customer_data = session.get('customer_data', {})

        # Add user message
        conversation_model.add_message(
            conversation_id=conversation_id,
            message_type='user',
            content=user_message
        )

        # Process customer info (extract and update)
        customer_data = customer_service.process_customer_info(
            user_message, 
            conversation_id, 
            existing_customer_data
        )
        
        # Update storage with new customer data
        if use_cli_storage:
            CLI_SESSION_STORAGE['customer_data'] = customer_data
        else:
            session['customer_data'] = customer_data
        
        # Check what information is still missing
        missing_info = customer_service.get_missing_info(customer_data)
        
        products = []
        
        # Only search for products if we have complete customer info
        if not missing_info and customer_data.get('looking_for'):
            products = product_service.search_products_by_query_and_preferences(
                customer_data['looking_for'],
                customer_data
            )
            products = product_service.format_products_for_display(products)

        # Generate AI response
        ai_response_data = ai_service.generate_response(
            user_message=user_message,
            customer_info=customer_data,
            products=products,
            missing_info=missing_info
        )

        # Add bot response to conversation
        conversation_model.add_message(
            conversation_id=conversation_id,
            message_type='bot',
            content=ai_response_data['response'],
            metadata={
                'products_shown': len(products),
                'customer_info_collected': len([k for k, v in customer_data.items() if v]),
                'missing_info': missing_info
            }
        )

        response_data = {
            'response': ai_response_data['response'],
            'products': products[:3] if products else [],
            'session_id': session_id,
            'needs_customer_info': ai_response_data.get('needs_customer_info', False),
            'customer_info': customer_data if customer_data else None,
            'missing_info': missing_info,
            'info_progress': {
                'collected': len([k for k, v in customer_data.items() if v and k not in ['timestamp', 'conversation_id']]),
                'total_required': 5  # name, email, phone, looking_for, preferences
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Enhanced debug endpoint
@app.route('/api/debug', methods=['GET'])
def debug():
    return jsonify({
        'conversations': conversation_model.conversations,
        'messages': conversation_model.messages,
        'customers': customer_service.customers,
        'cli_storage': CLI_SESSION_STORAGE,
        'sample_customer_data_structure': {
            'name': 'John Doe',
            'email': 'john@example.com', 
            'phone': '123-456-7890',
            'looking_for': 'gaming laptop',
            'budget': '$1500',
            'brand_preference': 'ASUS',
            'color_preference': 'Black'
        }
    })

# Endpoint to reset conversation (for testing)
@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    session.clear()
    CLI_SESSION_STORAGE['conversation_id'] = None
    CLI_SESSION_STORAGE['customer_data'] = {}
    return jsonify({'message': 'Conversation reset'})

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        print("🤖 Enhanced E-commerce Assistant CLI")
        print("Type your message and press Enter. Type 'exit' to quit.")
        print("Try: 'Hi, my name is John' then provide email, phone, what you're looking for, etc.\n")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ("exit", "quit"):
                break
                
            payload = {
                "message": user_input,
                "use_cli_storage": True  # Use CLI storage for persistence
            }
                
            try:
                with app.test_client() as client:
                    response = client.post("/api/chat", json=payload)
                    data = response.get_json()
                    
                    if "response" in data:
                        print("🤖 Assistant:", data["response"])
                        
                        if data.get("products"):
                            print(f"\n📦 Found {len(data['products'])} products:")
                            for i, product in enumerate(data["products"], 1):
                                print(f"   {i}. {product['name']} - ${product['price']} ({product['color']})")
                        
                        if data.get("customer_info"):
                            collected_count = len([k for k,v in data['customer_info'].items() 
                                                 if v and k not in ['timestamp', 'conversation_id']])
                            print(f"\n👤 Customer info collected: {collected_count}/5")
                            for key, value in data['customer_info'].items():
                                if value and key not in ['timestamp', 'conversation_id']:
                                    print(f"   ✓ {key}: {value}")
                        
                        if data.get("missing_info"):
                            print(f"📝 Still need: {', '.join(data['missing_info'])}")
                            
                    elif "error" in data:
                        print("❌ Error:", data["error"])
                    else:
                        print("🤖 Assistant: (no response)")
                        
            except Exception as e:
                print("❌ Error:", str(e))
    else:
        print("🚀 Starting Enhanced E-commerce Assistant Server...")
        print("🌐 Server running on http://localhost:5001")
        print("🧪 Test in CLI mode with: python app.py cli")
        print("🔄 Reset conversation: POST /api/reset")
        app.run(debug=True, port=5001)