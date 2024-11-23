from dotenv import load_dotenv
import assemblyai as aai
import os

load_dotenv()

def generate_questions(transcript):    
    aai.settings.api_key=os.getenv('API_KEY')
    audio_file = "https://assembly.ai/sports_injuries.mp3"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)    
    prompt='You are a machine that generates MCQ questions strictly based on the provided transcript of an audio file. Given a transcript, create 10 high-quality multiple-choice questions. Each question should be factual, clear, and directly derived from the content of the transcript. Avoid adding any information not present in the transcript. out the answers in the following json format with no explanation: {questions:[{question:What is the main topic discussed in the audio?,options:[Option A,Option B,Option C,Option D],correct_answer:Option A},{question:Which example was provided to illustrate the concept?,options:[Option A,Option B,Option C,Option D],correct_answer:Option C}]}. your output should be only AND only this json data and nothing else'
    result = transcript.lemur.task(
        prompt, final_model=aai.LemurModel.claude3_5_sonnet
    )

    result.response
