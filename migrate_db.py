import os
import logging
from sqlalchemy import create_engine, text
import sqlalchemy as sa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    try:
        # Get database URL from environment variable
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL environment variable not set")
            return
        
        logger.info("Starting database migration...")
        
        # Create engine and connect to the database
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Check if locale column exists in user table
            inspector = sa.inspect(engine)
            user_columns = [column['name'] for column in inspector.get_columns('user')]
            
            if 'locale' not in user_columns:
                # Add locale column if it doesn't exist
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN locale VARCHAR(2) DEFAULT 'en'"))
                conn.commit()
                logger.info("Added locale column to user table")
            else:
                logger.info("Locale column already exists in user table, skipping")
                
            # Check if driver table exists
            tables = inspector.get_table_names()
            if 'driver' in tables:
                # Check if driver_code column exists in driver table
                driver_columns = [column['name'] for column in inspector.get_columns('driver')]
                
                if 'driver_code' not in driver_columns:
                    # Add driver_code column if it doesn't exist
                    conn.execute(text("ALTER TABLE driver ADD COLUMN driver_code VARCHAR(10) UNIQUE"))
                    conn.commit()
                    logger.info("Added driver_code column to driver table")
                else:
                    logger.info("driver_code column already exists in driver table, skipping")
                
                # Check if available column exists and remove it
                if 'available' in driver_columns:
                    # Remove available column as it's no longer needed
                    conn.execute(text("ALTER TABLE driver DROP COLUMN available"))
                    conn.commit()
                    logger.info("Removed available column from driver table")
                else:
                    logger.info("available column doesn't exist in driver table, skipping")
            else:
                logger.info("Driver table doesn't exist yet, will be created by the application")
        
        logger.info("Database migration completed successfully")
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_database()