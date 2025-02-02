from flask import Flask, send_file
from dotenv import load_dotenv
from openai import OpenAI
import cohere
import os
import io

load_dotenv()

COHERE_API_KEY = os.environ['COHERE_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

COHERE_MODEL = "command-r-plus-08-2024"
OPENAI_TTS_VOICE = "nova"

co = cohere.ClientV2(api_key=COHERE_API_KEY)
oa = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>The endpoint is working</h1>"

@app.route("/goodjob")
def goodjob():
    response = co.chat(
        model=COHERE_MODEL,
        messages=[
        {
            "role": "user",
            "content": "Write a short, informal, positive sentence congratulating someone on doing a good job",
        }
    ],
    )

    audio_response = oa.audio.speech.create(
        model="tts-1",
        voice=OPENAI_TTS_VOICE,
        input=response.message.content[0].text
    )
    
    audio_buffer = io.BytesIO()
    
    for chunk in audio_response.iter_bytes():
        audio_buffer.write(chunk)
    
    audio_buffer.seek(0)

    return send_file(audio_buffer, mimetype="audio/mpeg", as_attachment=True, download_name="output.mp3")

@app.route("/badjob")
def better_next_time():
    response = co.chat(
        model=COHERE_MODEL,
        messages=[
        {
            "role": "user",
            "content": "Write a short, informal sentence telling the user that what they're doing isn't quite right, and to try again",
        }
    ],
    )

    audio_response = oa.audio.speech.create(
        model="tts-1",
        voice=OPENAI_TTS_VOICE,
        input=response.message.content[0].text
    )
    
    # Create a BytesIO buffer to hold the audio data
    audio_buffer = io.BytesIO()
    
    # Stream the response content into the buffer
    for chunk in audio_response.iter_bytes():
        audio_buffer.write(chunk)
    
    # Seek to the beginning of the buffer
    audio_buffer.seek(0)

    # Return the buffer as an audio file response
    return send_file(audio_buffer, mimetype="audio/mpeg", as_attachment=True, download_name="output.mp3")

@app.route("/audio")
def audio_gen():
    response = oa.audio.speech.create(
        model="tts-1",
        voice=OPENAI_TTS_VOICE,
        input="Hello world!"
    )
    
    # Create a BytesIO buffer to hold the audio data
    audio_buffer = io.BytesIO()
    
    # Stream the response content into the buffer
    for chunk in response.iter_bytes():
        audio_buffer.write(chunk)
    
    # Seek to the beginning of the buffer
    audio_buffer.seek(0)

    # Return the buffer as an audio file response
    return send_file(audio_buffer, mimetype="audio/mpeg", as_attachment=True, download_name="output.mp3")

app.run(debug=True)
