from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import assemblyai as aai
import json

load_dotenv()
aai.settings.api_key = os.getenv('API_KEY')


app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_questions_from_audio(file_path):    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_path) 
        
    prompt = 'You are a machine that generates MCQ questions strictly based on the provided transcript of an audio file. Given a transcript, create 10 high-quality multiple-choice questions. Each question should be factual, clear, and directly derived from the content of the transcript. Avoid adding any information not present in the transcript. Output the answers in the following JSON format with no explanation: {questions:[{question:What is the main topic discussed in the audio?,options:[Option A,Option B,Option C,Option D],correct_answer:Option A},{question:Which example was provided to illustrate the concept?,options:[Option A,Option B,Option C,Option D],correct_answer:Option C}]}'
        
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
            questions_json_str = generate_questions_from_audio(filepath)
                        
            questions_json = json.loads(questions_json_str)  
            questions = questions_json.get("questions", [])  
            
            session["questions"] = questions  
                
            return redirect(url_for('quiz'))
        except json.JSONDecodeError:
            return "Error: Unable to parse the JSON response from the API."

    return redirect(url_for("home"))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":        
        answers = {}
        for key, value in request.form.items():
            if key.startswith('q'):
                answers[key] = value
        session["answers"] = answers
        return redirect(url_for("results"))
    
    questions = session.get("questions", [])  
    answers = session.get("answers", {})  
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
