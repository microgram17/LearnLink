from flask import Flask, render_template, request, flash, redirect, url_for
from models import *
from flask_migrate import Migrate, upgrade
import os
from seed import seed_data
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_login import login_required, current_user
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learnlink.db"

app.config['SECRET_KEY'] = '9d8^7F&4s2@Lp#N6'

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
def material_page(material_id):
    return render_template("material_page.html", material = material)

class PostForm(FlaskForm):
    post_title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    post_body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Create Post')

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    sub_cat_id = request.args.get('sub_cat_id', type=int)
    if not sub_cat_id:
        flash('Subcategory ID is required!', 'danger')
        return redirect(url_for('subcategory_page'))

    form = PostForm()
    
    if form.validate_on_submit():
        new_post = Post(
            post_title=form.post_title.data,
            post_body=form.post_body.data,
            user_id=1,  # Placeholder for the user ID since login is not implemented
            sub_cat_id=sub_cat_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            visibility='public'
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('category_page'))  # Replace 'some_page' with the endpoint you want to redirect to

    return render_template('create_post.html', form=form)

### ! V1 code

    # # Populate the subcategory choices
    # # form.sub_cat_id.choices = [(sub_category.sub_category_id, sub_category.sub_category_name) for sub_category in SubCategory.query.all()]

    # if form.validate_on_submit():
    #     new_post = Post(
    #         post_title=form.post_title.data,
    #         post_body=form.post_body.data,
    #         sub_cat_id=form.sub_cat_id.data,
    #         created_at=datetime.now(),
    #         updated_at=datetime.now(),
    #         visibility='public'
    #     )
    #     db.session.add(new_post)
    #     db.session.commit()
    #     flash('Post created successfully!', 'success')
    #     return redirect(url_for('category_page'))  # Replace 'some_page' with the endpoint you want to redirect to

    # return render_template('create_post.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        upgrade()
        db.create_all()
        seed_data()


    app.run(debug=True, port=4500)