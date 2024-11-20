from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import assemblyai as aai
import os

load_dotenv()

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id,languages=['en'])
        return transcript
    except Exception as e:
        print(e)
        return False

def generate_questions(transcript):    
    aai.settings.api_key=os.getenv('API_KEY')
    task_payload = {
        "prompt": (
            "Generate 5 multiple-choice questions (MCQs) strictly based on the provided transcript. "
            "Ensure:\n"
            "1. Each question tests a critical concept, fact, or insight discussed in the transcript.\n"
            "2. Distractors (incorrect options) are plausible and based on related topics or common misconceptions.\n"
            "3. The correct answer is clearly identifiable within the transcript.\n"
            "4. Explanations for the correct answer are included for educational purposes.\n\n"
            "Output the results strictly in the following JSON format:\n"
            "{\n"
            "  \"questions\": [\n"
            "    {\n"
            "      \"question\": \"Question text here\",\n"
            "      \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
            "      \"correct_answer\": \"Correct Option\",\n"
            "      \"explanation\": \"Explanation of the correct answer\"\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}"
        ),
        "context": (
            "This transcript contains educational material aimed at creating insightful questions to help students understand "
            "the subject matter thoroughly. Focus on delivering factual, concept-driven, and engaging questions."
        ),
        "final_model": "anthropic/claude-3-5-sonnet",
        "max_output_size": 3000,
        "temperature": 0,
        "transcript": transcript
    }
    response = aai.tasks.create(**task_payload)
    return response

t=get_transcript(video_id='DAOFpgocfrg')
if t:
    print(generate_questions(t))
else:
    print('no')
