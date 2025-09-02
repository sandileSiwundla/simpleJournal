import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from flask_session import Session
import secrets
import string


load_dotenv() 

app = Flask(__name__)

entryList = []  
app.secret_key = os.getenv("SECRET_KEY")

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["mydatabase"]
users_collection = db["users"]
journal_collection = db["journals"]

@app.route('/')
def index():
    
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        date = request.form.get("date")
        content = request.form.get("content")
        return f'{date}: {content}'
    return render_template('add.html')

@app.route("/login", methods=["GET", "POST"])
def login():

    # renders template after register
    if request.method == "GET":
        return render_template("index.html")

    username = request.form.get("username")
    password = request.form.get("password")
    print(username)
    print(password)
    
    if not username or not password:
        return  render_template("index.html", error="Please fill in all fields.")

    #  Look up user
    user = users_collection.find_one({"username": username})

    if not user:
        return render_template("index.html", error="User not found.")

    # Check password against stored hash
    if check_password_hash(user["password"], password):
        session["username"] = username
        username = ""
        password = ""
        return redirect(url_for("content"))
    else:
        return render_template("index.html", error="Incorrect password.")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("Setpassword")
    confirmPassword = request.form.get("confirmPassword")
    print(username)
    print(password)

    if not username or not password or not confirmPassword:
        return "Missing fields", 400
    
    if confirmPassword != password:
        return "Passwords do not match", 400
    
    hashed_password = generate_password_hash(password)

    users_collection.insert_one({
        "username": username,
        "password": hashed_password
    })
    return successfulLogin()

def successfulLogin():
    # "Account created successfully!"
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/public", methods=["GET"])
def publicContent():
    entries = list(
        journal_collection.find({"status": True}).sort("timestamp", -1)
    )
    pass

@app.route("/content", methods=["GET", "POST"])
def content():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    
    alphabet = string.ascii_letters + string.digits
    id = ''.join(secrets.choice(alphabet) for i in range(10)) 

    if request.method == "POST":
        entry = request.form.get("entry")
        status = request.form.get("status")
        if entry:
            journal_entry = {
                "id": id,
                "status":  True if status == "true" else False,
                "username": username,
                "entry": entry,
                "timestamp": datetime.datetime.now()
            }
            journal_collection.insert_one(journal_entry)
            message = "Entry saved!"
            # ✅ Fetch all entries for the logged-in user (latest first)
            entries = list(
                journal_collection.find({"username": username}).sort("timestamp", -1)
            )
            return render_template("content.html", username=username, message=message, entries=entries)

    # ✅ Fetch all entries for the logged-in user (latest first)
    entries = list(
        journal_collection.find({"username": username}).sort("timestamp", -1)
    )

    return render_template("content.html", username=username, entries=entries)

@app.route("/delete/<entry_id>", methods=["POST"])
def deleteEntry(entry_id):
    username = session["username"]
    journal_collection.delete_one({"id": entry_id})
    entries = list(
        journal_collection.find({"username": username}).sort("timestamp", -1)
    )
    return render_template("content.html", username=username, entries=entries)



if __name__ == '__main__':
    app.run(debug=True)