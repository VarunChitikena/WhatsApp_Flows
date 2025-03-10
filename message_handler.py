# message_handler.py - Message Processing
# Processes incoming messages and interactions

import logging
from flask import Blueprint, request, jsonify
from whatsapp_api import send_text_message, send_interactive_buttons, send_rating_buttons, send_category_list
from session_manager import SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
message_bp = Blueprint('message', __name__)

def handle_message(message, phone_number):
    """Handle incoming WhatsApp message"""
    # Get current user state
    user_state = SessionManager.get_user_state(phone_number)
    
    if not user_state:
        # New user or restarting conversation
        SessionManager.set_user_state(phone_number, 'WELCOME')
        send_text_message(phone_number, "Welcome to the Tirumala Tirupati Devasthanam Feedback Survey. Your opinion matters to us!")
        send_category_list(phone_number)
        return
    
    current_state = user_state['current_state']
    
    # Handle text messages
    if 'text' in message:
        text = message['text']['body'].strip()
        
        # If user sends "restart" at any point, reset the conversation
        if text.lower() == 'restart':
            SessionManager.set_user_state(phone_number, 'WELCOME')
            send_text_message(phone_number, "Welcome back to the TTD Feedback Survey.")
            send_category_list(phone_number)
            return
    
    # Handle interactive responses (button clicks or list selections)
    if 'interactive' in message:
        if message['interactive']['type'] == 'button_reply':
            # Handle button replies (like ratings)
            button_id = message['interactive']['button_reply']['id']
            
            if current_state == 'AWAITING_RATING':
                # Extract rating from button ID (format: rating_X)
                rating = int(button_id.split('_')[1])
                category = user_state['selected_category']
                
                # Save the feedback
                SessionManager.save_feedback(phone_number, category, rating)
                
                # Thank the user and ask if they want to provide feedback in another category
                send_text_message(phone_number, f"Thank you for your {rating}-star rating for {category}. Your feedback is valuable to us.")
                send_interactive_buttons(
                    phone_number, 
                    "Provide More Feedback?", 
                    "Would you like to provide feedback on another category?",
                    ["Yes", "No"]
                )
                SessionManager.set_user_state(phone_number, 'AWAITING_MORE_FEEDBACK')
                
            elif current_state == 'AWAITING_MORE_FEEDBACK':
                if button_id == 'btn_1':  # Yes
                    send_category_list(phone_number)
                    SessionManager.set_user_state(phone_number, 'WELCOME')
                else:  # No
                    send_text_message(phone_number, "Thank you for completing our survey. Your feedback helps us improve. Have a blessed day! 🙏")
                    SessionManager.set_user_state(phone_number, 'COMPLETED')
        
        elif message['interactive']['type'] == 'list_reply':
            # Handle list selections (like category selection)
            category = message['interactive']['list_reply']['id']
            
            # Set user state and selected category
            SessionManager.set_user_state(phone_number, 'AWAITING_RATING', category)
            
            # Ask for rating
            send_text_message(phone_number, f"Please rate your experience with {category}:")
            send_rating_buttons(phone_number)

# Function to process incoming webhook data
def process_webhook(data):
    """Process incoming webhook data from WhatsApp"""
    # Check if this is a WhatsApp message notification
    if 'object' in data and data['object'] == 'whatsapp_business_account':
        if 'entry' in data and data['entry']:
            for entry in data['entry']:
                if 'changes' in entry and entry['changes']:
                    for change in entry['changes']:
                        if 'value' in change and 'messages' in change['value']:
                            for message in change['value']['messages']:
                                handle_message(message, change['value']['contacts'][0]['wa_id'])