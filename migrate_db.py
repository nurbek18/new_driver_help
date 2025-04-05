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
            # Check if locale column exists
            inspector = sa.inspect(engine)
            columns = [column['name'] for column in inspector.get_columns('user')]
            
            if 'locale' not in columns:
                # Add locale column if it doesn't exist
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN locale VARCHAR(2) DEFAULT 'en'"))
                conn.commit()
                logger.info("Added locale column to user table")
            else:
                logger.info("Locale column already exists, skipping")
        
        logger.info("Database migration completed successfully")
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    migrate_database()