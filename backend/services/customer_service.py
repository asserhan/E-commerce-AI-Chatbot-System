import re
from models.Customer import Customer
from models.Conversation import Conversation

class CustomerService:
    def __init__(self, db):
        self.customer_model = Customer(db)
        self.conversation_model = Conversation(db)
    
    def process_customer_info(self, message, conversation_id):
        # Extract customer information from message
        customer_info = self._extract_customer_info(message)
        
        if customer_info:
            # Check if customer already exists
            existing_customer = None
            if customer_info.get('phone'):
                existing_customer = self.customer_model.get_customer_by_phone(customer_info['phone'])
            
            if existing_customer:
                customer_id = str(existing_customer['_id'])
            else:
                # Create new customer
                customer_id = self.customer_model.create_customer(
                username=(customer_info.get('first_name', '') + customer_info.get('last_name', '')).strip() or customer_info.get('email') or customer_info.get('phone', ''),
                first_name=customer_info.get('first_name', ''),
                last_name=customer_info.get('last_name', ''),
                age=customer_info.get('age'),
                phone=customer_info.get('phone', ''),
                email=customer_info.get('email')
            )
            
            return {
                'customer_id': customer_id,
                'customer_info': customer_info,
                'is_new_customer': not existing_customer
            }
        
        return None
    
    def _extract_customer_info(self, message):
        customer_info = {}
        
        # Extract phone number
        phone_pattern = r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            customer_info['phone'] = phone_match.group(1)
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, message)
        if email_match:
            customer_info['email'] = email_match.group(0)
        
        # Extract names (simple approach)
        words = message.split()
        potential_names = [word for word in words if word.isalpha() and len(word) > 1]
        
        if len(potential_names) >= 2:
            customer_info['first_name'] = potential_names[0]
            customer_info['last_name'] = potential_names[1]
        elif len(potential_names) == 1:
            customer_info['first_name'] = potential_names[0]
        
        # Extract age
        age_pattern = r'\b(1[89]|[2-6][0-9]|70)\b'
        age_match = re.search(age_pattern, message)
        if age_match:
            customer_info['age'] = int(age_match.group(1))
        
        print("customer_info:", customer_info)
        print("email:", customer_info.get('email'))
        
        return customer_info if customer_info else None
    
    def update_conversation_lead_status(self, conversation_id, status):
        # Update lead status based on customer interaction
        valid_statuses = ['new', 'qualified', 'interested', 'converted', 'lost']
        
        if status in valid_statuses:
            # Update conversation lead status
            self.conversation_model.update_conversation(
                conversation_id=conversation_id,
                lead_status=status
            )
            return True
        else:
            raise ValueError(f"Invalid lead status: {status}. Must be one of {valid_statuses}")
    
    def validate_email(self, email):
        if not email:
            return False
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(email_pattern, email) is not None
    
    def validate_phone_number(self, phone):
        if not phone:
            return False
        phone_pattern = r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        return re.match(phone_pattern, phone) is not None
