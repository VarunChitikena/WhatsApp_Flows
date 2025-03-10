# whatsapp_api.py - WhatsApp API Functions
# Handles communication with the WhatsApp Cloud API

import logging
import requests
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_text_message(phone_number, message):
    """Send a simple text message via WhatsApp API"""
    url = f"https://graph.facebook.com/v18.0/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Message sent to {phone_number}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message: {str(e)}")
        if response := getattr(e, 'response', None):
            logger.error(f"Response: {response.text}")
        return None

def send_interactive_buttons(phone_number, header_text, body_text, buttons):
    """Send a message with interactive buttons"""
    url = f"https://graph.facebook.com/v18.0/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Prepare buttons in the required format
    button_items = []
    for idx, button in enumerate(buttons, start=1):
        button_items.append({
            "type": "reply",
            "reply": {
                "id": f"btn_{idx}",
                "title": button
            }
        })
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": header_text
            },
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": button_items
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Interactive message sent to {phone_number}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send interactive message: {str(e)}")
        if response := getattr(e, 'response', None):
            logger.error(f"Response: {response.text}")
        return None

def send_rating_buttons(phone_number):
    """Send rating buttons (1-5 stars)"""
    url = f"https://graph.facebook.com/v18.0/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Prepare rating buttons
    buttons = []
    for rating in range(1, 6):
        stars = "⭐" * rating
        buttons.append({
            "type": "reply",
            "reply": {
                "id": f"rating_{rating}",
                "title": stars
            }
        })
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "Rate Your Experience"
            },
            "body": {
                "text": "Please select a rating from 1 to 5 stars:"
            },
            "action": {
                "buttons": buttons
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Rating buttons sent to {phone_number}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send rating buttons: {str(e)}")
        if response := getattr(e, 'response', None):
            logger.error(f"Response: {response.text}")
        return None

def send_category_list(phone_number):
    """Send a list of categories for selection"""
    url = f"https://graph.facebook.com/v18.0/{Config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Prepare rows for each category
    category_rows = []
    for category in Config.CATEGORIES:
        category_rows.append({
            "id": category,
            "title": category
        })
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "TTD Feedback Survey"
            },
            "body": {
                "text": "Please select a category to provide your feedback:"
            },
            "footer": {
                "text": "Thank you for your valuable feedback"
            },
            "action": {
                "button": "Select Category",
                "sections": [
                    {
                        "title": "Services",
                        "rows": category_rows
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Category list sent to {phone_number}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send category list: {str(e)}")
        if response := getattr(e, 'response', None):
            logger.error(f"Response: {response.text}")
        return None