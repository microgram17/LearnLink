from models import db, Category, SubCategory
import json

def seed_data():
    
    with open("seed_data.json") as file:
        data = json.load(file)

    categories_data = data["categories"]
    subcategories_data = data["subcategories"]

    # Dictionary to store created categories by name
    categories = {}

    # Check for existing categories and add new ones
    for category_data in categories_data:
        category_name = category_data['category_name']
        existing_category = db.session.query(Category).filter_by(category_name=category_name).first()
        if existing_category is None:
            category = Category(**category_data)
            db.session.add(category)
            db.session.flush()  # This assigns an id to the category
            categories[category_name] = category.category_id
        else:
            categories[category_name] = existing_category.category_id

    # Check for existing subcategories and add new ones
    for subcategory_data in subcategories_data:
        sub_category_name = subcategory_data['sub_category_name']
        category_name = subcategory_data['category_name']
        category_id = categories.get(category_name)
        
        if category_id:
            existing_subcategory = db.session.query(SubCategory).filter_by(sub_category_name=sub_category_name, category_id=category_id).first()
            if existing_subcategory is None:
                subcategory = SubCategory(sub_category_name=sub_category_name, category_id=category_id)
                db.session.add(subcategory)

    db.session.commit()
    print("Seeding completed. No duplicates were created.")

if __name__ == "__main__":
    seed_data()
