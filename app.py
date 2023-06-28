import os
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from imports import login_required
import re
import sqlite3
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# Configure app
app = Flask(__name__)

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
def index():
    """default screen to welcome every user, new and returning"""

    return render_template("startadventure.html")


@app.route("/home")
def home():
    """Home Screen for users"""

    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter your username.")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter your password.")

        username = request.form.get("username")
        userpass = request.form.get("password")

        # Query database for username
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        try:
            # Select query from database for username given
            cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,))
            rows = cursor.fetchall()
            # Select first item. (there should only be one item)
            result = rows[0]

        except:
            print("Login error: Username not found")
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(result[2], userpass):
            flash("Invalid username and/or password combination")
            print("Invalid username or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = result[0]

        # Redirect user to home page
        return redirect("/home")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    # register user's with no account
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        # get user name and password
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        # check that user inputs name, and valid password for registration
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE username = ?", (name,))
            rows = cursor.fetchall()
            result = rows[0][1]
            print(result)
            if result == name:
                flash("Username already taken! Choose a different Username!")
                raise ValueError

            if not name:
                flash("Missing Username!")
                raise ValueError
            if len(password) < 8:
                flash(f"Password must be at least 8 characters long!\n")
                raise ValueError
            if re.search('[0-9]', password) is None:
                flash("Password must contain at least one number!")
                raise ValueError
            if re.search('[A-Z]', password) is None:
                flash("Password must contain at least one uppercase letter!")
                raise ValueError
            # if password is empty or doesn't match confirmation return error/apology
            if not password or password != confirmation:
                flash("Password empty or does not match!")
                raise ValueError
            else:
                pass

        except ValueError:
            db.close()
            print("Input/Select ValueError")
            return render_template("register.html")

        passhash = generate_password_hash(password)  # hash user's password

        try:
            cursor.execute(
                "INSERT INTO users (username, hash, email) VALUES(?, ?, ?)", (name, passhash, email))
            db.commit()
            print("Register/Insert: Successful commit")

        except:
            db.close()
            flash("DatabaseError!")
            print("Register/Insert: Error")
            return render_template("register.html")
        db.close()
        flash("Registration Successful! WELCOME!")

        return redirect("/")
