from flask import Flask, send_file
from dotenv import load_dotenv
from openai import OpenAI
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import cohere
import io

load_dotenv()

COHERE_API_KEY = os.environ['COHERE_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

COHERE_MODEL = "command-r-plus-08-2024"
OPENAI_TTS_VOICE = "nova"

oa_langchain = ChatOpenAI(model="gpt-4o-mini")
oa = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1>The endpoint is working</h1>"

@app.route("/score/<current_score>")
def score(current_score):
    messages = [
    SystemMessage("Respond to the following instructions exactly as they are stated."),
    HumanMessage(f"Provide me with a short sentence telling someone they currently have {current_score} points."),
    ]

    response = oa_langchain.invoke(messages)

    audio_response = oa.audio.speech.create(
        model="tts-1",
        voice=OPENAI_TTS_VOICE,
        input=response.content
    )
    
    audio_buffer = io.BytesIO()
    
    for chunk in audio_response.iter_bytes():
        audio_buffer.write(chunk)
    
    audio_buffer.seek(0)

    return send_file(audio_buffer, mimetype="audio/mpeg", as_attachment=True, download_name="output.mp3")

@app.route("/goodjob")
def goodjob():
    messages = [
    SystemMessage("Respond to the following instructions exactly as they are stated."),
    HumanMessage("Provide me with a short, informal, and positive sentence telling someone they are doing a good job."),
    ]

    response = oa_langchain.invoke(messages)

    audio_response = oa.audio.speech.create(
        model="tts-1",
        voice=OPENAI_TTS_VOICE,
        input=response.content
    )
    
    audio_buffer = io.BytesIO()
    
    for chunk in audio_response.iter_bytes():
        audio_buffer.write(chunk)
    
    audio_buffer.seek(0)

    return send_file(audio_buffer, mimetype="audio/mpeg", as_attachment=True, download_name="output.mp3")

@app.route("/badjob")
def better_next_time():
    
    messages = [
    SystemMessage("Respond to the following instructions exactly as they are stated."),
    HumanMessage("Write a short, informal sentence telling the user that what they're doing isn't quite right, and to try again."),
    ]

    response = oa_langchain.invoke(messages)

    audio_response = oa.audio.speech.create(
        model="tts-1",
        voice=OPENAI_TTS_VOICE,
        input=response.content
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
