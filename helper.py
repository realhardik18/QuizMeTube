from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import assemblyai as aai
import os
import yt_dlp

load_dotenv()

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id,languages=['en'])
        return transcript
    except Exception as e:
        print(e)
        return False

def download_video(url, output_path='downloads'):
    # Define options for yt-dlp
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Save videos with title as filename
        'format': 'bestvideo+bestaudio/best',  # Best quality video + audio
        'merge_output_format': 'mp4',  # Ensure the output is in MP4 format
    }

    # Download the video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def generate_questions(transcript):    
    aai.settings.api_key=os.getenv('API_KEY')
    audio_file = "https://assembly.ai/sports_injuries.mp3"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)    
    prompt='You are a machine that generates MCQ questions strictly based on the provided transcript of an audio file. Given a transcript, create 10 high-quality multiple-choice questions. Each question should be factual, clear, and directly derived from the content of the transcript. Avoid adding any information not present in the transcript. out the answers in the following json format with no explanation: {questions:[{question:What is the main topic discussed in the audio?,options:[Option A,Option B,Option C,Option D],correct_answer:Option A},{question:Which example was provided to illustrate the concept?,options:[Option A,Option B,Option C,Option D],correct_answer:Option C}]}. your output should be only AND only this json data and nothing else'
    result = transcript.lemur.task(
        prompt, final_model=aai.LemurModel.claude3_5_sonnet
    )

    print(result.response)

generate_questions(None)