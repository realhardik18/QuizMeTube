from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import assemblyai
import os

load_dotenv()

def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id,languages=['en'])
    return transcript


