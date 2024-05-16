from models import db, Role, User, Category, SubCategory, Post, Comments, Tags, FileAttachment, PostRating, CommentRating





def seed_data():

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