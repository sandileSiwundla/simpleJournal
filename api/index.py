from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import secrets
import string
from pymongo.errors import ConnectionFailure
import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Connect to MongoDB
try:
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ismaster')
except ConnectionFailure:
    try:
        standard_uri = "mongodb://sandilemsiwundla_db_user:HnrfllQJsOJxlAMU@cluster0-shard-00-00.93nj6rx.mongodb.net:27017,cluster0-shard-00-01.93nj6rx.mongodb.net:27017,cluster0-shard-00-02.93nj6rx.mongodb.net:27017/?ssl=true&replicaSet=atlas-9vzy71-shard-0&authSource=admin&retryWrites=true&w=majority"
        client = MongoClient(standard_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
    except (ConnectionFailure, Exception):
        client = None

if client:
    db = client["mydatabase"]
    users_collection = db["users"]
    journal_collection = db["journals"]
else:
    users_collection = None
    journal_collection = None

# Helper function to render templates with common context
def render_template_with_context(template_name, **context):
    return render_template(template_name, 
                         client=client, 
                         users_collection=users_collection,
                         journal_collection=journal_collection,
                         **context)

@app.route('/')
def index():
    if "username" in session:
        return redirect(url_for("content"))
    return render_template_with_context("index.html")

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        date = request.form.get("date")
        content = request.form.get("content")
        return f'{date}: {content}'
    return render_template_with_context('add.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_with_context("index.html")

    username = request.form.get("username")
    password = request.form.get("password")
    
    if not username or not password:
        return render_template_with_context("index.html", error="Please fill in all fields.")

    if not users_collection:
        return render_template_with_context("index.html", error="Database connection failed.")

    user = users_collection.find_one({"username": username})

    if not user:
        return render_template_with_context("index.html", error="User not found.")

    if check_password_hash(user["password"], password):
        session["username"] = username
        return redirect(url_for("content"))
    else:
        return render_template_with_context("index.html", error="Incorrect password.")

@app.route("/register", methods=["POST"])
def register():
    if not users_collection:
        return "Database connection failed", 500
        
    username = request.form.get("username")
    password = request.form.get("Setpassword")
    confirmPassword = request.form.get("confirmPassword")

    if not username or not password or not confirmPassword:
        return "Missing fields", 400
    
    if password != confirmPassword:
        return "Passwords do not match", 400
    
    if users_collection.find_one({"username": username}):
        return "Username already exists", 400
    
    hashed_password = generate_password_hash(password)

    users_collection.insert_one({
        "username": username,
        "password": hashed_password
    })
    
    session["username"] = username
    return redirect(url_for("content"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/content", methods=["GET", "POST"])
def content():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    message = None

    if request.method == "POST" and journal_collection:
        entry = request.form.get("entry")
        status = request.form.get("status")
        if entry:
            alphabet = string.ascii_letters + string.digits
            entry_id = ''.join(secrets.choice(alphabet) for i in range(10))
            
            journal_entry = {
                "id": entry_id,
                "status": status == "true",
                "username": username,
                "entry": entry,
                "timestamp": datetime.datetime.now()
            }
            journal_collection.insert_one(journal_entry)
            message = "Entry saved!"

    entries = []
    if journal_collection:
        entries = list(journal_collection.find({"username": username}).sort("timestamp", -1))

    return render_template_with_context("content.html", username=username, message=message, entries=entries)

@app.route("/delete/<entry_id>", methods=["POST"])
def deleteEntry(entry_id):
    if "username" not in session or not journal_collection:
        return redirect(url_for("login"))
        
    username = session["username"]
    journal_collection.delete_one({"id": entry_id, "username": username})
    return redirect(url_for("content"))

# Vercel expects a handler function named "app"
# This is the entry point for Vercel's serverless functions
handler = app