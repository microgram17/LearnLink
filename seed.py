from models import db, Category





def seed_data():
    # Check if there are any existing entries in the database
    if db.session.query(Category).count() == 0:
        # If no entries in the database seed data

        #Category seed data
        categories_data = [
            {'category_name':'Programming'},
            {'category_name':'Math'},
            {'category_name':'Language'},
            {'category_name':'Chemistry'},
            {'category_name':'Pysics'},
        ]

        for category_data in categories_data:
            category = Category(**category_data)
            db.session.add(category)
            
        db.session.commit()
    else:
        #If entries exists, skip seeding
        print("Database already contains entries. Skipping seeding.")

