# database.py - Database Operations
# Database operations using SQLite for storing feedback

import logging
import mysql.connector
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection"""
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USERNAME,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database and tables if they don't exist"""
    try:
        # Create connection without database specified
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USERNAME,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        cursor.execute(f"USE {Config.DB_NAME}")
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_responses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phone_number VARCHAR(20),
            category VARCHAR(50),
            rating INT,
            feedback TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (phone_number)
        )
        """)
        
        # Create table for user state
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_state (
            phone_number VARCHAR(20) PRIMARY KEY,
            current_state VARCHAR(50),
            selected_category VARCHAR(50),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        logger.info("Database initialized successfully")
    except mysql.connector.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_survey_stats():
    """Get overall survey statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Overall response count
        cursor.execute("SELECT COUNT(*) as total_responses FROM user_responses")
        total = cursor.fetchone()['total_responses']
        
        # Rating average by category
        cursor.execute("""
            SELECT 
                category, 
                AVG(rating) as avg_rating,
                COUNT(*) as count
            FROM user_responses
            GROUP BY category
            ORDER BY avg_rating DESC
        """)
        
        categories = cursor.fetchall()
        
        # Total unique users
        cursor.execute("SELECT COUNT(DISTINCT phone_number) as unique_users FROM user_responses")
        unique_users = cursor.fetchone()['unique_users']
        
        return {
            'total_responses': total,
            'unique_users': unique_users,
            'categories': categories
        }
    except Exception as e:
        logger.error(f"Error getting survey stats: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()