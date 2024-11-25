This is a submission for the [AssemblyAI Challenge ](https://dev.to/challenges/assemblyai): No More Monkey Business.*

## What I Built
Quizme.mp3 is a platform where students and learners can upload their audio lessons and receive a generated quiz with 10 questions based on the content of the audio file. Users can then attempt the quiz and receive a report of their responses along with an accuracy score. The website is built using HTML, Tailwind CSS, and the Flask web framework. It integrates AssemblyAI's Lemur for audio transcription and dynamic question generation.
## Demo
[Visit Quizme.mp3](https://quizme-mp3.onrender.com/)
![Home Page](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/tviu4cz02ywll4xzaste.png)
[Demo Video](https://vimeo.com/1032980330?share=copy)
## Journey
To create quiz questions from uploaded audio files, I used LeMUR with AssemblyAI's Lemur model. First, the audio file is transcribed using AssemblyAI’s Transcriber. Once we have the transcript, I craft a prompt that asks Lemur to generate 10 multiple-choice questions based solely on the transcript’s content. The questions are designed to be clear, accurate, and directly related to the audio, with the options and correct answers formatted in a neat JSON structure. The Claude 3.5 Sonnet model of Lemur is then used to generate these questions, and the result is returned to the user. This approach ensures the quiz is tailored to the specific audio content, making the whole process dynamic and context-driven.


