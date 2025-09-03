# import datetime
# from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# from pymongo import MongoClient
# from werkzeug.security import generate_password_hash, check_password_hash
# import os
# from dotenv import load_dotenv
# from flask_session import Session
# import secrets
# import string
# from pymongo.errors import ConnectionFailure

# # Load environment variables first
# load_dotenv()

# app = Flask(__name__)
# app.secret_key = os.getenv("SECRET_KEY")

# # Configure server-side sessions
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# # Connect to MongoDB with error handling
# try:
#     mongo_uri = os.getenv("MONGO_URI")
#     client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
#     client.admin.command('ismaster')
# except ConnectionFailure:
#     try:
#         # Standard connection string (non-SRV)
#         standard_uri = "mongodb://sandilemsiwundla_db_user:HnrfllQJsOJxlAMU@cluster0-shard-00-00.93nj6rx.mongodb.net:27017,cluster0-shard-00-01.93nj6rx.mongodb.net:27017,cluster0-shard-00-02.93nj6rx.mongodb.net:27017/?ssl=true&replicaSet=atlas-9vzy71-shard-0&authSource=admin&retryWrites=true&w=majority"
#         client = MongoClient(standard_uri, serverSelectionTimeoutMS=5000)
#         client.admin.command('ismaster')
#     except (ConnectionFailure, Exception):
#         print("Could not connect to MongoDB")
#         client = None

# if client:
#     db = client["mydatabase"]
#     users_collection = db["users"]
#     journal_collection = db["journals"]
# else:
#     print("Running without database connection")

# @app.route('/')
# def index():
#     if "username" in session:
#         return redirect(url_for("content"))
#     return render_template("index.html")

# @app.route('/add', methods=['GET', 'POST'])
# def add_entry():
#     if request.method == 'POST':
#         date = request.form.get("date")
#         content = request.form.get("content")
#         return f'{date}: {content}'
#     return render_template('add.html')

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "GET":
#         return render_template("index.html")

#     username = request.form.get("username")
#     password = request.form.get("password")
    
#     if not username or not password:
#         return render_template("index.html", error="Please fill in all fields.")

#     user = users_collection.find_one({"username": username}) if client else None

#     if not user:
#         return render_template("index.html", error="User not found.")

#     if check_password_hash(user["password"], password):
#         session["username"] = username
#         return redirect(url_for("content"))
#     else:
#         return render_template("index.html", error="Incorrect password.")

# @app.route("/register", methods=["POST"])
# def register():
#     username = request.form.get("username")
#     password = request.form.get("Setpassword")
#     confirmPassword = request.form.get("confirmPassword")

#     if not username or not password or not confirmPassword:
#         return "Missing fields", 400
    
#     if password != confirmPassword:
#         return "Passwords do not match", 400
    
#     # Check if user already exists
#     if users_collection.find_one({"username": username}):
#         return "Username already exists", 400
    
#     hashed_password = generate_password_hash(password)

#     users_collection.insert_one({
#         "username": username,
#         "password": hashed_password
#     })
    
#     session["username"] = username
#     return redirect(url_for("content"))

# @app.route("/logout")
# def logout():
#     session.pop("username", None)
#     return redirect(url_for("index"))

# @app.route("/content", methods=["GET", "POST"])
# def content():
#     if "username" not in session:
#         return redirect(url_for("login"))

#     username = session["username"]
#     message = None

#     if request.method == "POST" and client:
#         entry = request.form.get("entry")
#         status = request.form.get("status")
#         if entry:
#             alphabet = string.ascii_letters + string.digits
#             entry_id = ''.join(secrets.choice(alphabet) for i in range(10))
            
#             journal_entry = {
#                 "id": entry_id,
#                 "status": status == "true",
#                 "username": username,
#                 "entry": entry,
#                 "timestamp": datetime.datetime.now()
#             }
#             journal_collection.insert_one(journal_entry)
#             message = "Entry saved!"

#     # Fetch entries if database is connected
#     entries = []
#     if client:
#         entries = list(journal_collection.find({"username": username}).sort("timestamp", -1))

#     return render_template("content.html", username=username, message=message, entries=entries)

# @app.route("/delete/<entry_id>", methods=["POST"])
# def deleteEntry(entry_id):
#     if "username" not in session or not client:
#         return redirect(url_for("login"))
        
#     username = session["username"]
#     journal_collection.delete_one({"id": entry_id, "username": username})
#     return redirect(url_for("content"))



# if __name__ == '__main__':
#     app.run(debug=True)