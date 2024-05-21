from flask import Flask, render_template, request, flash, redirect, url_for
from models import *
from flask_migrate import Migrate, upgrade
import os
from seed import seed_data

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learnlink.db"

db.init_app(app)

migrate = Migrate(app, db)

@app.route("/")
def category_page():
    category = Category.query.all()
    return render_template("category_page.html", category=category)

@app.route("/category/<int:category_id>")
def category_page_by_id(category_id):
    category = Category.query.get(category_id)
    return render_template("subcategory_page.html", category=category)

@app.route("/register", methods=["GET", "POST"])
def register_user():
    return render_template("register_user.html")

@app.route("/material/<int:material_id>")
def material_page(post_id):
    material = Post.query.get(post_id)
    return render_template("material_page.html", material = material)



if __name__ == '__main__':
    with app.app_context():
        upgrade()
        db.create_all()
        seed_data()


    app.run(debug=True, port=4500)