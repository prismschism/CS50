import os
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from imports import usd
import re
import sqlite3
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
        with sqlite3.connect("database.db") as db:
             cursor = db.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE username = ?", (name,))
            result = cursor.fetchall()
            for i in result:
                print(i[1])
                if i[1] == name:
                    flash("Username already taken! Choose a different Username!")
                    print("equal")
                    raise ValueError
                else:
                    
                    print("no match")

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
            if not password or password != confirmation:  # if password is empty or doesn't match confirmation return error/apology
                flash("Password empty or does not match!")
                raise ValueError
            else:
                pass

        except ValueError:
            print("Input/SelectValueError")
            return render_template("register.html")

        

        passhash = generate_password_hash(password)  # hash user's password
        try:
            cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (name, passhash))
            db.commit()
            print(name, passhash)
            print("Register/Insert success")


        except:
            flash("DatabaseError!")
            print("Register/Insert Error")
            return render_template("register.html")

        flash("Registration Successful! WELCOME!")
        
        return redirect("/")


