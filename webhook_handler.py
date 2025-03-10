# webhook_handler.py - Webhook Routes
# Handles webhook verification and incoming requests

import os
import json
import logging
import hmac
import hashlib
from flask import Blueprint, request, Response
from config import Config
from message_handler import process_webhook

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # Handle verification request from WhatsApp
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode and token:
            if mode == 'subscribe' and token == Config.VERIFY_TOKEN:
                logger.info("Webhook verified")
                return challenge, 200
            else:
                logger.warning("Failed webhook verification")
                return Response(status=403)
    
    # Handle incoming messages
    if request.method == 'POST':
        # Verify request signature using app secret
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        if signature:
            # Extract signature
            signature = signature.replace('sha256=', '')
            
            # Calculate expected signature
            expected_signature = hmac.new(
                Config.APP_SECRET.encode('utf-8'),
                request.data,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Invalid signature")
                return Response(status=403)
        
        # Process the webhook payload
        data = request.json
        logger.info(f"Received webhook: {json.dumps(data)}")
        
        try:
            process_webhook(data)
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
        
        return Response(status=200)