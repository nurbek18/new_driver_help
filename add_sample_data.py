from app import app, db, Driver, generate_driver_code

# List of fictional driver data
sample_drivers = [
    {
        "name": "张伟",
        "age": 32,
        "gender": "Male",
        "phone": "13812345678",
        "whatsapp": "+8613812345678",
        "available": True
    },
    {
        "name": "李娜",
        "age": 29,
        "gender": "Female",
        "phone": "13923456789",
        "whatsapp": "+8613923456789",
        "available": True
    },
    {
        "name": "王强",
        "age": 35,
        "gender": "Male",
        "phone": "13534567890",
        "whatsapp": "+8613534567890",
        "available": False
    },
    {
        "name": "刘芳",
        "age": 27,
        "gender": "Female",
        "phone": "13645678901",
        "whatsapp": "+8613645678901",
        "available": True
    },
    {
        "name": "陈明",
        "age": 41,
        "gender": "Male",
        "phone": "13756789012",
        "whatsapp": "+8613756789012",
        "available": True
    },
    {
        "name": "赵静",
        "age": 33,
        "gender": "Female",
        "phone": "13867890123",
        "whatsapp": "+8613867890123",
        "available": False
    },
    {
        "name": "黄磊",
        "age": 38,
        "gender": "Male",
        "phone": "13978901234",
        "whatsapp": "+8613978901234",
        "available": True
    },
    {
        "name": "周佳",
        "age": 25,
        "gender": "Female",
        "phone": "13189012345",
        "whatsapp": "+8613189012345",
        "available": True
    },
    {
        "name": "吴鹏",
        "age": 44,
        "gender": "Male",
        "phone": "13290123456",
        "whatsapp": "+8613290123456",
        "available": False
    },
    {
        "name": "郑宇",
        "age": 31,
        "gender": "Male",
        "phone": "13301234567",
        "whatsapp": "+8613301234567",
        "available": True
    }
]

# Function to add sample data to the database
def add_sample_drivers():
    # Check if data already exists
    existing_count = Driver.query.count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} drivers. No sample data added.")
        return
    
    # Add sample data
    try:
        for driver_data in sample_drivers:
            # Add a unique driver code for each driver
            driver_data['driver_code'] = generate_driver_code()
            driver = Driver(**driver_data)
            db.session.add(driver)
        
        db.session.commit()
        print(f"Successfully added {len(sample_drivers)} sample drivers to the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding sample data: {e}")

# Run within app context
with app.app_context():
    add_sample_drivers()