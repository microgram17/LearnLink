from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
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
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask_security import current_user, auth_required, SQLAlchemySessionUserDatastore, permissions_accepted, roles_accepted

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learnlink.db"
app.config['SECRET_KEY'] = '9d8^7F&4s2@Lp#N6'
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-salt'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'

db.init_app(app)
migrate = Migrate(app, db)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)



@app.route("/")
def category_page():
    category = Category.query.all()
    return render_template("category_page.html", category=category)

@app.route("/category/<int:category_id>")
def category_page_by_id(category_id):
    category = Category.query.get(category_id)
    return render_template("subcategory_page.html", category=category)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email address already exists')
            return redirect(url_for('register'))

        hashed_password = hash_password(password)
        user_datastore.create_user(
            user_name=username, email=email, password=hashed_password, roles=['User'])
        db.session.commit()

        flash('User successfully registered')
        return redirect(url_for('login'))

    return render_template('register_user.html')

@app.route("/login",methods=['GET', 'POST'])
def login():
    roles = current_user.roles
    list_roles = []
    for role in roles:
        list_roles.append(role.name)
    roles = list_roles[0]
    if request.method == ["POST"]:
        if role == "Admin":
            return redirect(url_for("login"))

@app.route("/materials/<int:sub_cat_id>")
def materials_page(sub_cat_id):
    materials = Post.query.filter_by(sub_cat_id=sub_cat_id).all()
    sub_category = SubCategory.query.get(sub_cat_id)
    return render_template("materials_page.html", materials=materials, sub_category=sub_category)


@app.route("/material/<int:post_id>")
def material_page(post_id):
    material = Post.query.get(post_id)
    return render_template("material_page.html", material=material)

# Place holder för att titta på posts manuellet


@app.route('/post/<int:post_id>')
def view_post(post_id):
    # Assuming you have a function to fetch a post by its ID
    post = Post.query.get(post_id)
    return render_template('video.html', post=post)

# Model for Post creation form


class PostForm(FlaskForm):
    post_title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    post_body = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Create Post')

# Route for Post creation form


@app.route('/create_post/<sub_cat_id>', methods=['GET', 'POST'])
@auth_required()
def create_post(sub_cat_id):
    if request.method == 'GET':
        sub_category = SubCategory.query.get(sub_cat_id)
        form = PostForm()
        return render_template('create_post.html', sub_category=sub_category, sub_cat_id=sub_cat_id, form=form)

    if request.method == 'POST':
        form = PostForm(request.form)

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
            video_urls = re.findall(
                r'(https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)|https?://youtu\.be/([a-zA-Z0-9_-]+))', form.post_body.data)
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
            # Replace 'category_page' with the endpoint you want to redirect to
            return redirect(url_for('category_page'))

        return render_template('create_post.html', sub_cat_id=sub_cat_id, form=form)

# Jinjia filter to change urls in post body to clickable links


def make_links(text):
    # Regular expression to find urls
    url_regex = re.compile(r'(https?://[^\s]+)')
    # Function to replace URLs with anchor tags

    def replace(match):
        url = match.group(0)  # Extract Full URLs
        # return url as a clickable link
        return f'<a href="{url}" target="_blank">{url}</a><br>'
    # Function to replace URLs with anchor tags
    return Markup(re.sub(url_regex, replace, text))


app.jinja_env.filters['make_links'] = make_links

def user_seed_data():

    if not Role.query.first():
        user_datastore.create_role(name='Admin')
        user_datastore.create_role(name='User')
        db.session.commit()

    if not User.query.first():
        user_datastore.create_user(
            email='test@example.com', password=hash_password('password'), roles=['Admin', 'User'])
        user_datastore.create_user(
            email='c@c.com', password=hash_password('password'), roles=['User'])
        user_datastore.create_user(
            email='d@d.com', password=hash_password('password'), roles=['Admin'])
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        upgrade()
        db.create_all()
        seed_data()
        user_seed_data()

    app.run(debug=True, port=4500)
