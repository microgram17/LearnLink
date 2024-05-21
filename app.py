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
import re
from markupsafe import Markup

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

# Place holder för att titta på posts manuellet
@app.route('/post/<int:post_id>')
def view_post(post_id):
    # Assuming you have a function to fetch a post by its ID
    post = Post.query.get(post_id)
    return render_template('video.html', post=post)

# Model for Post creation form
class PostForm(FlaskForm):
    post_title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    post_body = TextAreaField('Body', validators=[DataRequired()])
    submit = SubmitField('Create Post')

# Route for Post creation form
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    sub_cat_id = request.args.get('sub_cat_id', type=int)
    if not sub_cat_id:
        flash('Subcategory ID is required!', 'danger')
        return redirect(url_for('subcategory_page'))  # Ensure 'subcategory_page' is a valid route

    form = PostForm()
    
    if form.validate_on_submit():
        new_post = Post(
            post_title=form.post_title.data,
            post_body=form.post_body.data,
            user_id=1,  # Placeholder for the user ID since login is not implemented
            sub_cat_id=sub_cat_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            visibility='public'
        )
        
        db.session.add(new_post)
        db.session.commit()

        # Parse the post_body for video URLs and store them as video attachments
        video_urls = re.findall(r'(https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)|https?://youtu\.be/([a-zA-Z0-9_-]+))', form.post_body.data)
        for match in video_urls:
            youtube_id = match[1] if match[1] else match[2]
            if youtube_id:
                youtube_embed_url = f"https://www.youtube.com/embed/{youtube_id}"
                new_video = FileAttachment(
                    post_id=new_post.post_id,  # Associate the FileAttachment with the new_post
                    file_name='Video',
                    file_url=youtube_embed_url,
                    file_type='video'
                )
                db.session.add(new_video)
        
        db.session.commit()  # Commit changes after adding FileAttachment objects

        flash('Post created successfully!', 'success')
        return redirect(url_for('category_page'))  # Replace 'category_page' with the endpoint you want to redirect to

    return render_template('create_post.html', form=form)

# Jinjia filter to change urls in post body to clickable links
def make_links(text):
    # Regular expression to find urls
    url_regex = re.compile(r'(https?://[^\s]+)')
    # Function to replace URLs with anchor tags
    return Markup(re.sub(url_regex, r'<a href="\1" target="_blank">\1<a\>', text))

app.jinja_env.filters['make_links'] = make_links

if __name__ == '__main__':
    with app.app_context():
        upgrade()
        db.create_all()
        seed_data()


    app.run(debug=True, port=4500)