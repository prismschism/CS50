import os
import base64
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from imports import allowed_file
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
    current_user = session["user_id"]  # get current user id
        # Query database for username
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()

        try:
            # Select query from database for username given
            cursor.execute(
                "SELECT * FROM users WHERE id = ?", (current_user,))
            rows = cursor.fetchall()
            # Select first item. (there should only be one item)
            users_name = rows[0][1]

        except:
                print("DB Error: User not found.")
                db.close()

    # get photos to display on home page
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()

        try:
            cursor.execute( 
                "SELECT mimetype, image_data, upload_date, location, description FROM images WHERE user_profile = ?", (current_user,))
            rows = cursor.fetchall()
            all_images = rows
            
            
        except:
            print("DB ERROR: Image SELECT Fail!")
            db.close()

    posts_range = len(all_images)
    image_list = []


    # converting tuples from db into dict for easy use.
    for post in all_images:
        # create a dictionary with image info for each image
        image_dict = {"mimetype" :"", 
                "image_data" : "", 
                "upload_date" : "",
                "location" : "",
                "description" : ""
                }

        mime = post[0]
        image_dict["mimetype"] = mime
        #convert from blob to base64 then to UTF-8 to show images later
        og_blob = post[1]
        converted_data = base64.b64encode(og_blob)
        converted_data = converted_data.decode("UTF-8")
        image_dict["image_data"] = converted_data

        upload_date = post[2]
        image_dict["upload_date"] = upload_date

        location = post[3]
        image_dict["location"] = location

        desc = post[4]
        image_dict["description"] = desc
        image_list.append(image_dict)

    # test prints to ensure all items are accessessible
    for post in image_list:
        print(post["location"])
            


    return render_template("home.html", user=users_name.upper(), image_list=image_list, posts_range=posts_range)


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
            print(result)

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
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        # check that user inputs name, and valid password for registration
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE username = ?", (username,))
            rows = cursor.fetchall()
            if rows:
                result = rows[0]
                print(result)
                if username in result:
                    flash("Username already taken! Choose a different Username!")
                    raise ValueError
            else:
                pass

            if not username:
                flash("Missing Username!")
                raise ValueError
            
            # make sure password is strong
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
                "INSERT INTO users (username, hash, email) VALUES(?, ?, ?)", (username, passhash, email))
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


@app.route("/upload", methods=["GET", "POST"])
def file_upload():
    if request.method == "GET":
        return render_template("upload.html")

    if request.method == "POST":
        # check if file was posted
        if 'image' not in request.files:
            flash("No file part")
            return redirect("/upload")

        location = request.form.get("location")
        desc = request.form.get("desc")
        image = request.files['image']

        # check for empty file field
        if image.filename == "":
            flash("No selected file")
            return render_template("/upload.html")

        # if we have an image file and its extension is allowed proceed
        if image and allowed_file(image.filename):
            # store image data
            image_data = image.read()
            mimetype = image.mimetype
            timestamp = datetime.datetime.now()

            user = session["user_id"]
            
            # test prints
            print("mimetype: ", mimetype)
            print("location: ", location)
            print("desc: ", desc)

            # save image and its data to db
            with sqlite3.connect("database.db") as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO images (user_profile, image_data, mimetype, upload_date, location, description) VALUES (?, ?, ?, ?, ?, ?)", (
                    user, image_data, mimetype, timestamp.date(), location, desc))
                db.commit()
            flash("Upload success!")
            return redirect("/home")

        else:
            flash("Upload to database failed! / File type not supported.")
            return render_template("/upload.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    
    if request.method == "GET":
        current_user = session["user_id"]  # get current user id
        # Query database for username
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        try:
            # Select query from database for username given
            cursor.execute(
                "SELECT * FROM users WHERE id = ?", (current_user,))
            rows = cursor.fetchall()
            # Select first item. (there should only be one item)
            users_name = rows[0][1]
            users_email = rows[0][3]

        except:
                print("DB Error: User not found.")
                db.close()
        return render_template("profile.html", user=users_name, user_email=users_email)


@app.route("/username-change", methods=["GET", "POST"])
def change_username():

    if request.method == "GET":
        current_user = session["user_id"]  # identify user

        # Query database for username
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        try:
            # Select query from database for username given
            cursor.execute(
                "SELECT * FROM users WHERE id = ?", (current_user,))
            rows = cursor.fetchall()
            # Select first item. (there should only be one item)
            users_name = rows[0][1]
        except:
                print("DB Error: User not found.")
                db.close()

        return render_template("username-change.html", user=users_name)
    
    if request.method == "POST":
        current_user = session["user_id"]  # identify user
        #  Get the new username
        new_name = request.form.get("new_username")
        
        #  open database
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        #  check if username is available
        try:
            cursor.execute(
                "SELECT * FROM users WHERE username = ?", (new_name,))
            rows = cursor.fetchall()
            if rows:
                result = rows[0]
                print(result)
                if new_name in result:
                    flash("Username already taken! Choose a different Username!")
                    raise ValueError
            else:
                pass

            if not new_name:
                flash("Missing Username!")
                raise ValueError
                  
        except ValueError:
            db.close()
            print("Input/Select ValueError")
            return redirect("/username-change")
        
        #  Change the username
        #  open database
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        try:
            cursor.execute(
                "UPDATE users SET username = ? WHERE id = ?", (new_name, current_user,))
            print(new_name)
            print(current_user)
            
            db.commit()
            flash("Successfully changed username!")
        except:
            db.close()
            print("username change error/ DB error")

            return redirect("/username-change")

        return redirect("/profile")


@app.route("/email-change", methods=["GET", "POST"])
def change_email():

    if request.method == "GET":
        current_user = session["user_id"]  # identify user

        # Query database for e-mail
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

        try:
            # Select query from database for current email
            cursor.execute(
                "SELECT email FROM users WHERE id = ?", (current_user,))
            rows = cursor.fetchall()
            # Select first item. (there should only be one item)
            users_email = rows[0][0]
            print(users_email)
        except:
                print("DB Error: User not found.")
                db.close()

        return render_template("email-change.html", users_email=users_email)
    
    if request.method == "POST":
        current_user = session["user_id"]  # identify user
        #  Get the new email address
        new_email = request.form.get("new_email")

        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET email = ? WHERE id = ?", (new_email, current_user,))
            print(new_email)
            print(current_user)
            
            db.commit()
            flash("Successfully changed email!")
        except:
            db.close()
            print("Email change error/ DB error")

            return redirect("/email-change")

        return redirect("/profile")
    
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("reset-password.html")

    if request.method == "POST":
        current_user = session["user_id"]  # identify user
        #  Get the new email address
        password = request.form.get("new_pass")
        confirmation = request.form.get("confirmation")
        try:
                # make sure password is strong
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

            print("Input/Select ValueError")
            return render_template("reset-password.html")
        # If password passes all checks, generate new HASH
        new_pass = generate_password_hash(password)

        # Save new Password Hash in DB
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()
        
        try:
            cursor.execute(
                "UPDATE users SET hash = ? WHERE id = ?", (new_pass, current_user,))
            print(new_pass)
            print(current_user)
            
            db.commit()
            flash("Successfully reset password!")

        except:
            db.close()
            print("psswrd change error/ DB error")

            return redirect("/profile")

        return redirect("/profile")