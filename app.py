import os
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from imports import usd
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

#Configure app
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem not cookies.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def home():
    """Show home screen, welcome user, 
    show shop categories and about info"""

    #current_user = session["user_id"]  # get current user id

    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")