from app import app, db, Driver, generate_driver_code
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_driver_codes():
    """
    Updates existing drivers with unique driver codes if they don't have one
    """
    try:
        with app.app_context():
            drivers = Driver.query.filter(Driver.driver_code.is_(None)).all()
            
            if not drivers:
                logger.info("No drivers found without driver codes")
                return
                
            logger.info(f"Found {len(drivers)} drivers without driver codes")
            
            # Generate and set driver codes
            for driver in drivers:
                driver.driver_code = generate_driver_code()
                logger.info(f"Generated code {driver.driver_code} for driver {driver.name}")
                
            # Commit changes
            db.session.commit()
            logger.info("Successfully updated all driver codes")
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating driver codes: {e}")

if __name__ == "__main__":
    update_driver_codes()