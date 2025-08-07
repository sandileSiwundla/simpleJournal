import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from flask_session import Session



load_dotenv()  # Load .env file


app = Flask(__name__)

entryList = []  

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["mydatabase"]
users_collection = db["users"]
journal_collection = db["journals"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        userName = request.form.get("username")
        password = request.form.get("password")

    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        date = request.form.get("date")
        content = request.form.get("content")
        return f'{date}: {content}'
    return render_template('add.html')

@app.route("/login", methods=["POST"])
def login():
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
        return redirect(url_for("content"))
    else:
        return render_template("index.html", error="Incorrect password.")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("Setpassword")
    confirmPassword = request.form.get("confirmPassword")

    if not username or not password or not confirmPassword:
        return "Missing fields", 400
    
    if confirmPassword != password:
        return "Passwords do not match", 400
    
    hashed_password = generate_password_hash(password)

    users_collection.insert_one({
        "username": username,
        "password": hashed_password
    })
    return "Account created successfully!"

@app.route("/content", methods=["GET", "POST"])
def content():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        entry = request.form.get("entry")
        if entry:
            journal_entry = {
                "username": username,
                "entry": entry,
                "timestamp": datetime.now()
            }
            journal_collection.insert_one(journal_entry)
            message = "Entry saved!"
            return render_template("content.html", username=username, message=message)

    return render_template("content.html", username=username)


if __name__ == '__main__':
    app.run(debug=True)