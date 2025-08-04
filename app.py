from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, request, render_template, redirect, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv


load_dotenv()  # Load .env file


app = Flask(__name__)

entryList = []  

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["mydatabase"]
users_collection = db["users"]

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
def submit():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return "Missing fields", 400

    hashed_password = generate_password_hash(password)

    users_collection.insert_one({
        "username": username,
        "password": hashed_password
    })

    return "Account created successfully!"

if __name__ == '__main__':
    app.run(debug=True)