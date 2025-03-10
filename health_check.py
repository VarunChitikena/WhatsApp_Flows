# health_check.py - Health Check Endpoint
# Health check endpoint with public/private key verification

import os
import logging
import hmac
import hashlib
import base64
import json
from flask import Blueprint, request, jsonify, Response
from config import Config
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
health_bp = Blueprint('health', __name__)

def load_private_key():
    """Load private key from file"""
    try:
        with open(Config.PRIVATE_KEY_PATH, 'rb') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading private key: {str(e)}")
        return None

def load_public_key():
    """Load public key from file"""
    try:
        with open(Config.PUBLIC_KEY_PATH, 'rb') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading public key: {str(e)}")
        return None

@health_bp.route('/health', methods=['GET', 'POST'])
def health_check():
    """Health check endpoint with public/private key verification"""
    
    # Check database connection
    db_connected = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        db_connected = True
        cursor.close()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
    
    # Prepare health data
    health_data = {
        "status": "healthy" if db_connected else "degraded",
        "database_connected": db_connected,
        "version": "1.0.0"
    }
    
    # For signature verification requests (skip Base64 encoding)
    if request.method == 'POST' and request.headers.get('X-Signature') and request.headers.get('X-Skip-Base64'):
        # Get the signature from header
        signature_header = request.headers.get('X-Signature')
        
        try:
            # Verify the signature using private key
            request_data = request.data
            
            # Get the private key
            private_key = load_private_key()
            if not private_key:
                logger.error("Failed to load private key")
                return jsonify({"error": "Server configuration error"}), 500
            
            # Calculate HMAC signature
            calculated_signature = hmac.new(
                private_key,
                request_data,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            if hmac.compare_digest(calculated_signature, signature_header):
                logger.info("Health check signature verified")
                health_data["whatsapp_api_connected"] = True
                return jsonify(health_data), 200
            else:
                logger.warning("Invalid signature in health check request")
                return jsonify({"error": "Invalid signature"}), 401
            
        except Exception as e:
            logger.error(f"Error processing health check: {str(e)}")
            return jsonify({"error": "Server error"}), 500
    
    # DEFAULT: Return Base64 encoded response for WhatsApp Flow health checks
    json_data = json.dumps(health_data)
    base64_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    logger.info(f"Returning Base64 encoded health check: {base64_data}")
    return Response(base64_data, mimetype='text/plain')