import requests
import json
from utils.model_selector import ModelSelector


def call_github_ai_model(messages, model_config):
    url = f"{model_config['endpoint']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {model_config['token']}",
        "Content-Type": "application/json"
    }
    body = {
        "messages": messages,
        "temperature": 1,
        "top_p": 1,
        "model": model_config['model']
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"Model API error: {response.text}")
    data = response.json()
    return data['choices'][0]['message']['content']

class AIService:

    def __init__(self):
        self.model_selector = ModelSelector()
    
    def generate_response(self, user_message, customer_info=None, products=None, missing_info=None, conversation_history=None):
        # Compose the conversation for the LLM
        messages = []
        # Improved system prompt for a strong intro
        system_prompt = (
            "You are a friendly virtual assistant for LaptopStore, an e-commerce site specializing in laptops. "
            "Always start the conversation with a warm welcome and a brief introduction: 'Welcome to LaptopStore! We help you find the perfect laptop for your needs.' "
            "Then, ask the user to provide their name, email, phone number, and what kind of laptop they are looking for. "
            "For every user message, reply with a JSON object containing the following fields: 'name', 'email', 'phone', 'looking_for', and a 'reply' field with your natural language response. "
            "If you don't know a field, leave it empty. Only reply with a single JSON object, no extra text. Example:\n"
            '{"name": "", "email": "", "phone": "", "looking_for": "", "reply": "Welcome to LaptopStore! To get started, may I have your name, email, phone number, and what kind of laptop you are looking for?"}'
        )
        messages.append({"role": "system", "content": system_prompt})
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg['type'] == "user" else "assistant"
                messages.append({"role": role, "content": msg['content']})
        # Add the latest user message
        messages.append({"role": "user", "content": user_message})

        # Get the current model config
        model_config = self.model_selector.get_current_model()
        try:
            ai_reply = call_github_ai_model(messages, model_config)
        except Exception as e:
            # If you hit a limit or error, switch to the next model and try again
            model_config = self.model_selector.switch_to_next_model()
            ai_reply = call_github_ai_model(messages, model_config)

        # Try to parse the reply as JSON
        parsed = None
        try:
            parsed = json.loads(ai_reply)
        except Exception:
            # If parsing fails, fallback to plain text
            return {
                "response": ai_reply,
                "needs_customer_info": False
            }

        # Optionally, update customer_info with parsed fields
        updated_fields = {}
        for field in ['name', 'email', 'phone', 'looking_for']:
            if parsed.get(field):
                updated_fields[field] = parsed[field]

        # Return the reply and the extracted fields
        return {
            "response": parsed.get("reply", ai_reply),
            "needs_customer_info": False,
            "extracted_fields": updated_fields
        }
    
    def _is_customer_info_complete(self, customer_info):
        required_fields = ['name', 'email', 'phone', 'looking_for']
        return all(field in customer_info and customer_info[field] for field in required_fields)
    
    def _ask_for_missing_info(self, missing_info, customer_info=None):
        name = customer_info.get('name', '') if customer_info else ''
        greeting = f"Hi {name}! " if name else "👋 Welcome to LaptopStore! "
        intro = (
            "I'm your virtual assistant for our e-commerce site specializing in laptops. "
            "I'll help you find the perfect laptop for your needs. "
        ) if not name else ""

        if 'name' in missing_info:
            return {
                'response': f"{greeting}{intro}To get started, what's your name?",
                'needs_customer_info': True
            }
        elif 'email' in missing_info:
            return {
                'response': f"{greeting}Great! May I have your email address so I can send you recommendations and updates?",
                'needs_customer_info': True
            }
        elif 'phone' in missing_info:
            return {
                'response': f"{greeting}Could you also provide your phone number? This helps us contact you about your orders.",
                'needs_customer_info': True
            }
        elif 'looking_for' in missing_info:
            return {
                'response': f"{greeting}What type of laptop are you looking for today? (e.g., gaming, business, student, etc.)",
                'needs_customer_info': True
            }
        elif 'preferences' in missing_info:
            return {
                'response': f"{greeting}To find the best match, could you tell me about your preferences? For example:\n- What's your budget range?\n- Any preferred brand or color?\n- Any specific features you need?",
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