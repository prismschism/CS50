import os
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from imports import usd
import re
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

#Configure app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

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

@app.route("/register", methods=["GET", "POST"])
def register():
    #register user's with no account
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        # get user name and password
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # check that user inputs name, and valid password for registration
        if not name:
            flash("Missing Username!")
        if len(password) < 8:
            flash(f"Password must be at least 8 characters long!\n")

        if re.search('[0-9]', password) is None:
            flash("Password must contain at least one number!")
        if re.search('[A-Z]', password) is None:
            flash("Password must contain at least one uppercase letter!")
        if not password or password != confirmation:  # if password is empty or doesn't match confirmation return error/apology
            flash("Password empty or does not match!")

        passhash = generate_password_hash(password)  # hash user's password
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name, passhash)

        except:
            flash("DatabaseError!")
            return render_template("register.html")
        session["user_id"] = new_user
        flash("Registration Successful! WELCOME!")
        return redirect("/")
