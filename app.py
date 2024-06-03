from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
from models import *
from flask_migrate import Migrate, upgrade
import os
from seed import seed_data
from forms import PostForm, CommentForm
from datetime import datetime
import re
from markupsafe import Markup
from flask_security.utils import hash_password
from flask_security import current_user, auth_required, permissions_accepted, roles_accepted, current_user, Security, SQLAlchemyUserDatastore, login_required
from sqlalchemy.orm import joinedload
import bleach
from flask_wtf import CSRFProtect
from sqlalchemy.exc import OperationalError
import config

app = Flask(__name__)
app.config.from_object(config.Config)


# csrf = CSRFProtect(app)
db.init_app(app)
migrate = Migrate(app, db)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)


def sanitize_input(input_text):
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a']
    allowed_attributes = {'a': ['href', 'title']}
    cleaned_text = bleach.clean(input_text, tags=allowed_tags, attributes=allowed_attributes)
    return cleaned_text

# @app.after_request
# def apply_csp(response):
#     response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self';"
#     response.headers['X-Content-Type-Options'] = 'nosniff'
#     response.headers['X-XSS-Protection'] = '1; mode=block'
#     response.headers['Referrer-Policy'] = 'no-referrer'
#     response.headers['X-Frame-Options'] = 'SAMEORIGIN'
#     return response

@app.route("/")
def landing_page():
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
    return render_template("landing_page.html", recent_posts=recent_posts)

@app.route("/categories")
def category_page():
    category = Category.query.all()
    return render_template("category_page.html", category=category)

@app.route("/category/<int:category_id>")
def category_page_by_id(category_id):
    category = Category.query.get(category_id)
    return render_template("subcategory_page.html", category=category)

@app.route("/about")
def about():
    return render_template("about_us.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

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
        created_at = datetime.now()
        user_datastore.create_user(
            user_name=username, email=email, password=hashed_password, roles=['User'], created_at=created_at)
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
    materials = (db.session.query(Post, db.func.sum(PostRating.rating).label('thumbs_up'))
                 .outerjoin(PostRating, Post.post_id == PostRating.post_id)
                 .filter(PostRating.rating == True, Post.sub_cat_id == sub_cat_id)
                 .group_by(Post.post_id)
                 .order_by(db.text('thumbs_up DESC'))
                 .all())
    
    sub_category = SubCategory.query.get(sub_cat_id)
    return render_template("materials_page.html", materials=materials, sub_category=sub_category)

@app.route("/materials/<int:sub_cat_id>/delete", methods=['POST'])
@login_required
def delete_post(sub_cat_id):
    post_id = request.form.get('post_id')
    post_to_delete = Post.query.get(post_id)

    if (post_to_delete.user_id == current_user.user_id) or ('Admin' in [role.name for role in current_user.roles]):
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('materials_page', sub_cat_id=sub_cat_id))
    else:
        return redirect(url_for('materials_page', sub_cat_id=sub_cat_id))

# Function to recursively fetch child comments for a given comment
def fetch_child_comments(comment, depth=0):
    """
    Recursively fetch child comments and include their depth level.
    Args:
    - comment: The parent comment object.
    - depth: The current depth level of the comment in the hierarchy.
    
    Returns:
    - A list of tuples where each tuple contains a comment object and its depth level.
    """
    child_comments = []
    
    # Query to fetch child comments of the given comment
    comments = Comments.query.filter_by(parent_comment_id=comment.comment_id).all()
    
    for child_comment in comments:
        # Append the child comment and its depth to the list
        child_comments.append((child_comment, depth + 1))
        # Recursively fetch and append the child comments of the current child comment
        child_comments.extend(fetch_child_comments(child_comment, depth + 1))
    
    return child_comments

def build_comment_tree(comments):
    """
    Build a nested comment tree from a flat list of comments.
    Args:
    - comments: List of comment objects.

    Returns:
    - A list of root comments with nested child comments.
    """
    comment_dict = {comment.comment_id: comment for comment in comments}
    for comment in comments:
        comment.child_comments = []
    root_comments = []

    for comment in comments:
        if comment.parent_comment_id is None:
            root_comments.append(comment)
        else:
            parent = comment_dict.get(comment.parent_comment_id)
            if parent:
                parent.child_comments.append(comment)

    # Debugging: Print the comment tree structure
    def print_comment_tree(comments, level=0):
        for comment in comments:
            print("  " * level + f"Comment ID: {comment.comment_id}, Parent ID: {comment.parent_comment_id}")
            if comment.child_comments:
                print_comment_tree(comment.child_comments, level + 1)

    print_comment_tree(root_comments)

    return root_comments

@app.route("/material/<int:post_id>", methods=['GET', 'POST'])
def material_page(post_id):
    """
    View function to handle the material page, including displaying and adding comments.
    Args:
    - post_id: The ID of the material post.

    Returns:
    - Rendered HTML template for the material page.
    """
    material = Post.query.get_or_404(post_id)
    comment_form = CommentForm()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to be logged in to comment.', 'danger')
            return redirect(url_for('login', next=request.url))

        if comment_form.validate_on_submit():
            new_comment = Comments(
                post_id=post_id,
                user_id=current_user.user_id,
                comment_text=sanitize_input(comment_form.comment_text.data),
                parent_comment_id=request.form.get('parent_comment_id', type=int),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment posted successfully!', 'success')
            return redirect(url_for('material_page', post_id=post_id))

    comments = Comments.query.filter_by(post_id=post_id).options(joinedload(Comments.child_comments)).all()
    root_comments = build_comment_tree(comments)
    current_user_id = current_user.user_id if current_user.is_authenticated else None
    return render_template("material_page.html", material=material, comments=root_comments, comment_form=comment_form, current_user_id=current_user_id)



# Route for Post creation form
@app.route('/create_post/<sub_cat_id>', methods=['GET', 'POST'])
@roles_accepted("Admin", "User")
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
                post_title=sanitize_input(form.post_title.data),
                post_body=sanitize_input(form.post_body.data),
                user_id=current_user.user_id,
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
            return redirect(url_for('materials_page', sub_cat_id=sub_cat_id))

        return render_template('create_post.html', sub_cat_id=sub_cat_id, form=form)

@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@auth_required()
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Kolla vilken användare
    if post.user_id != current_user.user_id:
        abort(403)  # Om användare inte äger detta, kicka han

    if request.method == 'GET':
        form = PostForm(obj=post)
        return render_template('edit_post.html', post=post, form=form)

    if request.method == 'POST':
        form = PostForm(request.form)

        if form.validate_on_submit():
            # Updatera
            post.post_title = sanitize_input(form.post_title.data)
            post.post_body = sanitize_input(form.post_body.data)
            post.updated_at = datetime.now()

            # Extract current video URLs from the updated post body
            video_urls = re.findall(
                r'(https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)|https?://youtu\.be/([a-zA-Z0-9_-]+))',
                form.post_body.data
            )
            current_video_ids = {match[1] if match[1] else match[2] for match in video_urls}

            # Find existing video attachments
            existing_attachments = FileAttachment.query.filter_by(post_id=post.post_id, file_type='video').all()
            existing_video_ids = {attachment.file_url.split('/')[-1] for attachment in existing_attachments}

            # Delete video attachments that are no longer in the post body
            for attachment in existing_attachments:
                youtube_id = attachment.file_url.split('/')[-1]
                if youtube_id not in current_video_ids:
                    db.session.delete(attachment)

            # Add new video URLs that are not already in the database
            for youtube_id in current_video_ids:
                if youtube_id not in existing_video_ids:
                    youtube_embed_url = f"https://www.youtube.com/embed/{youtube_id}"
                    new_video = FileAttachment(
                        post_id=post.post_id,
                        file_name='Video',
                        file_url=youtube_embed_url,
                        file_type='video'
                    )
                    db.session.add(new_video)

            db.session.commit()

            flash('Post updated successfully!', 'success')
            return redirect(url_for('material_page', post_id=post.post_id))

        return render_template('edit_post.html', post=post, form=form)

@app.route("/search", methods=["POST", "GET"])
def search():

    ###remove links from body-text
    def remove_links(text):
    # Regular expression to find urls
        url_regex = re.compile(r'(https?://[^\s]+)')
        # Function to replace URLs with anchor tags
        def replace_remove(match):
            url = match.group(0)  # Extract Full URLs
            return f' '
        # Function to remove URLs
        return Markup(re.sub(url_regex, replace_remove, text))

# create search_lib strings for each post
    search_lib = {}
    posts = Post.query.all()
    users = User.query.all()
    subcat = SubCategory.query.all()
    for k in subcat:
        for i in posts:
            if k.sub_category_id == i.sub_cat_id:
                for j in users:
                    if i.user_id == j.user_id:
                        search_lib[i.post_id] = k.sub_category_name + " "
                        search_lib[i.post_id] += j.email + " "
                        search_lib[i.post_id] += i.post_title + " "
                        search_lib[i.post_id] += remove_links(i.post_body)

# vectorize search_lib
    vector_lib = {}
    for i in search_lib.keys():
        vector = search_lib[i].lower()
        vector = vector.split(' ')
        for j in range(len(vector)):
            vector[j].replace(' ', '')
        vector_lib[i] = set(vector)

    if request.method == "POST":
        search = request.form.get('search')
        search = search.lower()
        search = search.split(' ')
        for i in range(len(search)):
            search[i].replace(' ', '')
        search_kw = set(search)
        hits = {}

        for i in vector_lib.keys():
            shared_entries = search_kw.intersection(vector_lib[i])

            if len(search_kw) <=2 and len(shared_entries) >=1:
                hits[i] = i

            if len(search_kw) >2 and len(search_kw) <=5 and len(shared_entries) >=2:
                hits[i] = i

            if len(search_kw) >5 and len(shared_entries) >=3:
                hits[i] = i

        return render_template("search.html", posts=posts, hit_id = hits.keys())
    return render_template("search.html")


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

    # Define the users you want to create or update
    users = [
        {
            "user_name": "Admin",
            "email": "test@example.com",
            "password": "password",
            "roles": ["Admin"],
        },
        {
            "user_name": "Both",
            "email": "both@role.com",
            "password": "password",
            "roles": ["Admin", "User"],
        },
        {
            "user_name": "tomato",
            "email": "tomato@farmer.com",
            "password": "tomato",
            "roles": ["User"],
        }
    ]

    try:
        with db.session.no_autoflush:
            for user_info in users:
                user = User.query.filter_by(email=user_info["email"]).first()
                if user:
                    # Update user details if they differ
                    needs_update = False
                    if user.user_name != user_info["user_name"]:
                        user.user_name = user_info["user_name"]
                        needs_update = True
                    if not user.password or not user.password.startswith("pbkdf2:sha256"):
                        user.password = hash_password(user_info["password"])
                        needs_update = True
                    if set(role.name for role in user.roles) != set(user_info["roles"]):
                        user.roles = [user_datastore.find_or_create_role(role) for role in user_info["roles"]]
                        needs_update = True
                    if needs_update:
                        user.created_at = datetime.now()  # Update timestamp if any changes
                else:
                    # Create user if not exists
                    user_datastore.create_user(
                        user_name=user_info["user_name"],
                        email=user_info["email"],
                        password=hash_password(user_info["password"]),
                        roles=user_info["roles"],
                        created_at=datetime.now()
                    )
            db.session.commit()
    except OperationalError as e:
        print(f"OperationalError: {e}")
        db.session.rollback()

@app.route("/rate_post/<int:post_id>/<int:rating>", methods=['POST'])
def rate_post(post_id, rating):
    """
    Route to handle rating a post.
    Args:
    - post_id: The ID of the post to rate.
    - rating: The rating value (1 for thumbs up, 0 for thumbs down).

    Returns:
    - Redirects to the material page.
    """
    if not current_user.is_authenticated:
        flash('You need to be logged in to rate posts.', 'danger')
        return redirect(url_for('login', next=request.url))

    existing_rating = PostRating.query.filter_by(post_id=post_id, user_id=current_user.user_id).first()

    if existing_rating:
        existing_rating.rating = bool(rating)
    else:
        new_rating = PostRating(
            post_id=post_id,
            user_id=current_user.user_id,
            rating=bool(rating)
        )
        db.session.add(new_rating)

    db.session.commit()
    return redirect(url_for('material_page', post_id=post_id))


if __name__ == '__main__':
    with app.app_context():
        upgrade()
        db.create_all()
        seed_data()
        user_seed_data()

    app.run(debug=True, port=4500)
