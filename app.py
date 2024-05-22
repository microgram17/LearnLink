from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from flask import Flask, render_template, request, flash, redirect, url_for
from models import *
from flask_migrate import Migrate, upgrade
import os
from seed import seed_data

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///learnlink.db"
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-salt'

db.init_app(app)
migrate = Migrate(app, db)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

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
        user_datastore.create_user(user_name=username, email=email, password=hashed_password, roles=['User'])
        db.session.commit()

        flash('User successfully registered')
        return redirect(url_for('security.login'))

    return render_template('register_user.html')


@app.route("/material/<int:material_id>")
def material_page(material_id):
    return render_template("material_page.html", material = material)

'''---------------------------------------------------------------'''

def user_seed_data():

    if not Role.query.first():
        user_datastore.create_role(name='Admin')
        user_datastore.create_role(name='User')
        db.session.commit()

    if not User.query.first():
        user_datastore.create_user(email='test@example.com', password=hash_password('password'), roles=['Admin','User'])
        user_datastore.create_user(email='c@c.com', password=hash_password('password'), roles=['User'])
        user_datastore.create_user(email='d@d.com', password=hash_password('password'), roles=['Admin'])
        db.session.commit()

'''---------------------------------------------------------------'''

if __name__ == '__main__':
    with app.app_context():
        upgrade()
        db.create_all()
        seed_data()
        user_seed_data()
    app.run(debug=True, port=4500)