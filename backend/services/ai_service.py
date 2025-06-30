
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import requests

load_dotenv()

# ihave github token for openai in environment variable GITHUB_TOKEN

class AIService:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = os.getenv('GITHUB_TOKEN')
        if not api_key:
            raise ValueError("GitHub token is required for Copilot Models API")
        self.api_key = api_key
        self.endpoint = "https://models.github.ai/inference"
        self.model = "openai/gpt-4.1"
        #Set up logging for AIService for debugging and error tracking
   
       
    
    def generate_response(self, user_message,customer_info=None,products=None, conversation_history=None,context=None):
        """Generate AI response based on user message and context"""
        try:
            #buld context for the AI model
            system_prompt = self._build_system_prompt(customer_info, products, context)
            messages = self._build_message_history(conversation_history, user_message)
    

            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                "temperature": 0.7,
                "top_p": 1.0,
                "model": self.model,
                "max_tokens": 150
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"{self.endpoint}/chat/completions",
                headers=headers,
                json=payload
            )
            if response.status_code != 200:
       
                return {
                    'response': "I'm having trouble processing your request right now. Please try again.",
                    'error': 'api_error'
                }
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]

            #extract structured data from responses
            structured_data = self._extract_structured_data(ai_response,user_message)

            result = {
                'response': ai_response,
                'structured_data': structured_data,
                'needs_customer_info': self._needs_customer_info(ai_response),
                'shows_products': bool(products and len(products) > 0),
                'confidence': 0.9  # You can adapt this as needed
            }

            return result
        except Exception as e:
            
            return {
                'response': "I apologize, but I'm having trouble processing your request. Please try again.",
                'error': 'unknown_error'
            }
        
    def _build_system_prompt(self, customer_info, products, context):
        """Build system prompt for AI"""
        base_prompt = """
        You are a helpful and enthusiastic e-commerce AI shopping assistant. Your primary goals are:
        
        1. Help customers find products that match their specific needs and budget
        2. Provide detailed, accurate product information
        3. Collect customer contact information when they show genuine interest
        4. Guide customers toward making purchasing decisions
        5. Be conversational, friendly, but professional
        
        IMPORTANT GUIDELINES:
        - Always be helpful and enthusiastic about helping customers
        - Ask clarifying questions to better understand their needs
        - When customers show interest in products, naturally ask for their contact information
        - Explain that contact info helps with follow-up and sending detailed specifications
        - Present products with key benefits and features that match their stated needs
        - If they mention a budget, respect it and suggest products within that range
        - Be concise but informative - avoid overly long responses
        - Use a conversational tone, like a knowledgeable salesperson
        
        CONTACT INFORMATION COLLECTION:
        - When customers say they're interested, want more info, or ask about purchasing
        - Ask politely for their name and phone number
        - Explain it's for follow-up and sending detailed product information
        - Don't be pushy, but be persistent in a friendly way
        """
        #add customer context
        if customer_info:
            base_prompt += f"\n\nCUSTOMER CONTEXT:\n{json.dumps(customer_info, indent=2)}"
        #add product context
        if products and len(products) > 0:
            base_prompt += f"\n\nAVAILABLE PRODUCTS:\n{json.dumps(products[:5], indent=2, default=str)}"

        #add additional context if provided
        if context:
            base_prompt += f"\n\nADDITIONAL CONTEXT:\n{context}"
        return base_prompt

    def _build_message_history(self, conversation_history, current_message):
        """Build message history for AI model"""
        messages = []
        if conversation_history:
            # Include last 8 messages for context (4 exchanges)
            recent_messages = conversation_history[-8:]
            for msg in recent_messages:
                role= "user" if msg['type'] == 'user' else 'assistant'
                messages.append({
                    "role": role,
                    "content": msg['content']
                })
        #add current message 
        messages.append({"role": "user", "content": current_message})
        return messages
    
    def _extract_structured_data(self, ai_response, user_message):
        """Extract structured information from AI response"""
        try:
            structured_data = {}
            response_lower = ai_response.lower()
            message_lower = user_message.lower()

            #detect if AI is asking for contact information
            contact_keywords = ['name', 'phone', 'email', 'contact', 'number']
            if any(keyword in response_lower for keyword in contact_keywords):
                structured_data['requesting_contact'] = True
          
            #detect if AI is showing products
            product_keywords = ['product', 'item', 'recommend', 'suggest','perfect for','great option','consider']
            if any(keyword in response_lower for keyword in product_keywords):
                structured_data['recommending_products'] = True
            #detect customer intent
            intent_keywords = {
            'browsing': ['looking for', 'need', 'want', 'searching'],
            'comparing': ['compare', 'difference', 'versus', 'better'],
            'ready_to_buy': ['buy', 'purchase', 'order', 'interested', 'want this'],
            'need_info': ['tell me more', 'details', 'specifications', 'more info']
             }
            for intent, keywords in intent_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    structured_data['customer_intent'] = intent
                    break
        except Exception as e:
          
            structured_data = {}
        return structured_data

    def _needs_customer_info(self, ai_response):
        """Check if AI response indicates need for customer info"""
        contact_indicators = [
            'contact information',
            'name and phone',
            'phone number',
            'how can i reach',
            'follow up with you',
            'send you',
            'contact you'
        ]
        response_lower = ai_response.lower()
        return any(indicator in response_lower for indicator in contact_indicators)
    
    def _calculate_confidence(self, openai_response):
        """Calculate confidence score based on response metadata"""
        try:
            # Simple confidence calculation based on response length and completion
            response_text = openai_response.choices[0].message.content
            finish_reason = openai_response.choices[0].finish_reason
            
            if finish_reason == 'stop' and len(response_text) > 20:
                return 0.9
            elif finish_reason == 'length':
                return 0.7
            else:
                return 0.5
        except:
            return 0.5