from flask import Flask, render_template, redirect, url_for, request


app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')