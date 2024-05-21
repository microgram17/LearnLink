from models import db, Category, SubCategory

def seed_data():
    # Category seed data
    categories_data = [
        {'category_name': 'Programming'},
        {'category_name': 'Math'},
        {'category_name': 'Language'},
        {'category_name': 'Chemistry'},
        {'category_name': 'Physics'},
        {'category_name': 'Biology'},
    ]

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

    # SubCategory seed data
    subcategories_data = [
            {'sub_category_name': 'Python', 'category_name': 'Programming'},
            {'sub_category_name': 'JavaScript', 'category_name': 'Programming'},
            {'sub_category_name': 'Matlab', 'category_name': 'Programming'},
            {'sub_category_name': 'Analytical Chemistry', 'category_name': 'Chemistry'},
            {'sub_category_name': 'Computational Chemistry', 'category_name': 'Chemistry'},
            {'sub_category_name': 'Medicinal Chemistry', 'category_name': 'Chemistry'},
            {'sub_category_name': 'Inorganic Chemistry', 'category_name': 'Chemistry'},
            {'sub_category_name': 'Physical Chemistry', 'category_name': 'Chemistry'},
            {'sub_category_name': 'Organic Chemistry', 'category_name': 'Chemistry'},
            {'sub_category_name': 'Biochemistry', 'category_name': 'Chemistry'},
            {'sub_category_name': 'Microbiology', 'category_name': 'Biology'},
            {'sub_category_name': 'Molecularbiology', 'category_name': 'Biology'},
            {'sub_category_name': 'Ecology', 'category_name': 'Biology'}
            ]
    
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
