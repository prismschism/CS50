from flask import redirect, session, flash
from functools import wraps
import sqlite3


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def insertImage(name, photo):
    try:
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()
            cursor.execute("")
            print("insertImage successfully connected database.")
    except:
        flash("Upload Image Failed!")
        print("insertImage Error")
