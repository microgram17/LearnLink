from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home_page():
    return render_template("category_page.html")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    return render_template("register_user.html")

@app.route("/category/<int:category_id>")
def category_page(category_id):
    return render_template("category_page.html", category = category)

@app.route("/material/<int:material_id>")
def material_page(material_id):
    return render_template("material_page.html", material = material)