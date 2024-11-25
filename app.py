from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import assemblyai as aai
import json

# Load the API key from .env
load_dotenv()
aai.settings.api_key = os.getenv('API_KEY')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key for session management

# Make sure the `audio_file` folder exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define the allowed file extensions for audio files
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to generate questions from audio file
def generate_questions_from_audio(file_path):
    # Initialize the transcriber
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_path)  # Transcribe the audio file
    
    # Define the prompt for generating questions
    prompt = 'You are a machine that generates MCQ questions strictly based on the provided transcript of an audio file. Given a transcript, create 10 high-quality multiple-choice questions. Each question should be factual, clear, and directly derived from the content of the transcript. Avoid adding any information not present in the transcript. Output the answers in the following JSON format with no explanation: {questions:[{question:What is the main topic discussed in the audio?,options:[Option A,Option B,Option C,Option D],correct_answer:Option A},{question:Which example was provided to illustrate the concept?,options:[Option A,Option B,Option C,Option D],correct_answer:Option C}]}'
    
    # Call AssemblyAI API to generate questions based on transcript
    result = transcript.lemur.task(
        prompt, final_model=aai.LemurModel.claude3_5_sonnet
    )
    
    return result.response

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "audio_file" not in request.files:
        return redirect(request.url)
    audio_file = request.files["audio_file"]
    
    if audio_file and allowed_file(audio_file.filename):
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        audio_file.save(filepath)
        
        try:
            # Generate questions directly in the request context
            questions_json_str = generate_questions_from_audio(filepath)  # Get the questions from the API
            
            # Parse the JSON string into a dictionary
            questions_json = json.loads(questions_json_str)  # Convert string to dictionary
            questions = questions_json.get("questions", [])  # Get the questions
            
            session["questions"] = questions  # Store questions in session
            
            # Redirect to quiz page after processing
            return redirect(url_for('quiz'))
        except json.JSONDecodeError:
            return "Error: Unable to parse the JSON response from the API."

    return redirect(url_for("home"))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        # Store submitted answers in session
        answers = {}
        for key, value in request.form.items():
            if key.startswith('q'):
                answers[key] = value
        session["answers"] = answers
        return redirect(url_for("results"))
    
    # Pass questions from session (if already generated) to the template
    questions = session.get("questions", [])  # Retrieve questions from session
    answers = session.get("answers", {})  # Retrieve answers (if any)
    return render_template("quiz.html", questions=questions, answers=answers)

@app.route("/results")
def results():
    questions = session.get("questions", [])
    answers = session.get("answers", {})
    score = 0
    results = []

    for i, question in enumerate(questions, start=1):
        user_answer = answers.get(f"q{i}")
        correct = question["correct_answer"]
        results.append({
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": correct,
            "is_correct": user_answer == correct
        })
        if user_answer == correct:
            score += 1

    return render_template("results.html", results=results, score=score, total=len(questions))

if __name__ == "__main__":
    app.run(debug=True)
