from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from helper import generate_questions

load_dotenv()

app = Flask(__name__)
app.secret_key = 'secret'
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# MongoDB setup
client = MongoClient(os.getenv('MONGO_DB_URI'))
db = client["quizmetube"]
users_collection = db["users"]
quizzes_collection = db["quizzes"]

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    if "username" in session:        
        quizzes = list(quizzes_collection.find({"creator": session["username"]}))
        return render_template('home.html', username=session['username'], quizzes=quizzes)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        if users_collection.find_one({"username": username}):
            flash("Username already exists", "danger")
        else:            
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({
                "username": username,
                "email": email,
                "password": hashed_password
            })
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/add_quiz", methods=["POST"])
def add_quiz():
    if "username" not in session:
        return redirect(url_for("login"))

    audio_file = request.files.get("audio_file")
    if not audio_file:
        flash("Please upload a valid audio file.", "danger")
        return redirect(url_for("home"))

    # Save the audio file
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)

    try:
        # Generate questions using the helper function
        questions = generate_questions(file_path)
        if not questions:
            flash("Failed to generate questions.", "danger")
            return redirect(url_for("home"))

        # Save the quiz to the database
        quiz_id = quizzes_collection.insert_one({
            "title": audio_file.filename,
            "questions": questions,
            "creator": session["username"]
        }).inserted_id

        flash("Quiz added successfully!", "success")
    except Exception as e:
        print(f"Error in generating quiz: {e}")
        flash("An error occurred while processing the audio file.", "danger")

    return redirect(url_for("home"))

@app.route("/attempt/<quiz_id>", methods=["GET", "POST"])
def attempt_quiz(quiz_id):
    quiz = quizzes_collection.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        flash("Quiz not found.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        # Evaluate answers (not implemented here but can be added)
        flash("Quiz submitted successfully!", "success")
        return redirect(url_for("home"))

    return render_template("attempt_quiz.html", quiz=quiz)

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
