# session_manager.py - User Session Management
# Manages user conversation state

import logging
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user session and conversation state"""
    
    @staticmethod
    def get_user_state(phone_number):
        """Get the current state of a user based on their phone number"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_state WHERE phone_number = %s", (phone_number,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            logger.error(f"Error getting user state: {str(e)}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def set_user_state(phone_number, state, category=None):
        """Set or update the state of a user"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT * FROM user_state WHERE phone_number = %s", (phone_number,))
            if cursor.fetchone():
                if category is not None:
                    cursor.execute(
                        "UPDATE user_state SET current_state = %s, selected_category = %s WHERE phone_number = %s",
                        (state, category, phone_number)
                    )
                else:
                    cursor.execute(
                        "UPDATE user_state SET current_state = %s WHERE phone_number = %s",
                        (state, phone_number)
                    )
            else:
                cursor.execute(
                    "INSERT INTO user_state (phone_number, current_state, selected_category) VALUES (%s, %s, %s)",
                    (phone_number, state, category)
                )
            
            conn.commit()
            logger.info(f"User state updated: {phone_number} -> {state} ({category if category else 'N/A'})")
            return True
        except Exception as e:
            logger.error(f"Error setting user state: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def save_feedback(phone_number, category, rating, feedback=None):
        """Save user feedback to the database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO user_responses (phone_number, category, rating, feedback) VALUES (%s, %s, %s, %s)",
                (phone_number, category, rating, feedback)
            )
            
            conn.commit()
            logger.info(f"Feedback saved: {phone_number} -> {category} ({rating} stars)")
            return True
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    @staticmethod
    def get_user_stats(phone_number):
        """Get statistics about user feedback submissions"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_feedbacks,
                    AVG(rating) as average_rating,
                    MAX(timestamp) as last_feedback
                FROM user_responses
                WHERE phone_number = %s
            """, (phone_number,))
            
            result = cursor.fetchone()
            return result
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()