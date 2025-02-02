import math
import random
from flask import Flask, jsonify
from pyjoycon import JoyCon, get_L_id
import time
import serial
import os

from pyjoycon import JoyCon, get_R_id
import time
import serial
import aiohttp
import asyncio
import io
from pydub import AudioSegment
import simpleaudio as sa

POLLING_INTERVAL = 150  
TOLERANCE = 10
GYRO_SCALE = 100

VARIANCE_POWER = 1.5
SCALE = 0.5

HEART_RATE_MIN = 60.0     
HEART_RATE_MAX = 180.0    

BASE_GROWTH = 0.02                
GROWTH_DECAY_INCREMENT = 0.0002   
GROWTH_INDEX_MAX = 200           


BASE_DECAY = 0.05        
DECAY_INCREMENT = 0.0     
DECAY_INDEX_MAX = 3      

DELTA_THRESHOLD = 5.0   

BASELINE_RANGE = 10.0

arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2) 

joycon_id = get_R_id()
joycon = JoyCon(*joycon_id)

async def fetch_mp3(url):
    """Fetch MP3 file asynchronously and return it as bytes."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"Failed to fetch MP3: {response.status}")
                return None

async def play_audio(url):
    """Fetch and play MP3 file asynchronously."""
    mp3_data = await fetch_mp3(url)
    if mp3_data is None:
        return
    
    # Convert MP3 bytes to WAV format
    audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
    wav_data = io.BytesIO()
    audio.export(wav_data, format="wav")
    
    # Play the audio
    wave_obj = sa.WaveObject.from_wave_file(io.BytesIO(wav_data.getvalue()))
    play_obj = wave_obj.play()
    play_obj.wait_done()


def calculate_distance(point1, point2):
    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))

def calculate_score(user_points, ideal_points):
    if not user_points or not ideal_points:
        return 0

    min_length = min(len(user_points), len(ideal_points))
    total_penalty = 0.0

    for i in range(min_length):
        dist = calculate_distance(user_points[i], ideal_points[i])
        if dist > TOLERANCE:
            penalty = (dist - TOLERANCE) ** VARIANCE_POWER
        else:
            penalty = 0
        total_penalty += penalty

    avg_penalty = total_penalty / min_length

    length_diff = abs(len(user_points) - len(ideal_points))
    length_penalty = length_diff * 2  

    score = 100 - (avg_penalty * SCALE) - length_penalty
    return max(int(score), 0)

def update_heart_rate(
    heart_rate,
    growth_index,
    decay_index,
    dist,
    baseline_hr,
    baseline_active
):

    if dist > DELTA_THRESHOLD:
        growth_index = min(growth_index + 1, GROWTH_INDEX_MAX)
        decay_index = 0
    else:
        decay_index = min(decay_index + 1, DECAY_INDEX_MAX)
        growth_index = 0

    growth_factor = max(0.0, BASE_GROWTH - growth_index * GROWTH_DECAY_INCREMENT)

    decay_factor = BASE_DECAY + decay_index * DECAY_INCREMENT

    heart_rate += dist * growth_factor

    if baseline_active:
        heart_rate -= (decay_factor / 2.0)
    else:
        heart_rate -= decay_factor

    heart_rate = max(HEART_RATE_MIN, min(heart_rate, HEART_RATE_MAX))
    return heart_rate, growth_index, decay_index

ideal = []
points = []
active = False
recording_mode = False
play_mode = True


baseline_hr = None
baseline_active = True 

heart_rate = 0
growth_index = 0
decay_index = 0

heart_rate_history = []

print("Controls:")
print("- Press LEFT to enter routine-recording mode (records the 'ideal' routine).")
print("- Press DOWN to enter play mode (records the user attempt).")
print("- Press and hold UP to start recording or playing; release UP to stop.")

while True:
    status = joycon.get_status()
    gyro = status['gyro']

    buttons = status['buttons']['left']
    play_mode = True
    buttons = status['buttons']['right']

    up_button = buttons['x']
    left_button = buttons['y']
    down_button = buttons['b']

    if left_button == 1:
        if not recording_mode and not play_mode:
            print("Entering recording mode (ideal routine)...")
            recording_mode = True
            play_mode = False
            time.sleep(0.5) 
        elif recording_mode:
            print("Exiting recording mode...")
            recording_mode = False
            time.sleep(0.5)

    if down_button == 1:
        if not play_mode and not recording_mode:
            print("Entering play mode (user attempt)...")
            play_mode = True
            recording_mode = False
            time.sleep(0.5)
        elif play_mode:
            print("Exiting play mode...")
            play_mode = False
            time.sleep(0.5) 

    if up_button == 1 and not active:
        if recording_mode:
            print("Starting routine recording...")
            points = []
            active = True
            time.sleep(0.5)  

        elif play_mode:
            print("Starting user attempt...")
            points = []
            active = True

            baseline_hr = random.uniform(70.0, 80.0)
            heart_rate = baseline_hr

            growth_index = 0
            decay_index = 0

            heart_rate_history = []
            time.sleep(0.5)  

    if up_button == 0 and active:
        if recording_mode:
            print("Stopping routine recording...")
            ideal = points.copy()
            points = []
            active = False
            print("Routine saved!")
            print("Ideal routine:", ideal)
            time.sleep(0.5)  

        elif play_mode:
            print("Stopping user attempt...")
            score = calculate_score(points, ideal)
            print("User points:", points)
            print("Score:", score)
            asyncio.run(play_audio(f"http://34.169.141.219:5000/score/{score}"))
            distance = (score ** 2) / 400
            arduino.write((str(score) + "\n").encode())
            print("Sent " + str(distance) + " command to Arduino.")

            points = []
            active = False

            if heart_rate_history:
                avg_hr = sum(heart_rate_history) / len(heart_rate_history)
            else:
                avg_hr = heart_rate
            print(f"Average heart rate: {avg_hr:.2f}")

            heart_rate_history = []
            baseline_hr = None
            baseline_active = True
            heart_rate = 0
            growth_index = 0
            decay_index = 0

            time.sleep(0.5) 


    if active:
        x, y, z = map(lambda g: int(g // GYRO_SCALE), [gyro['x'], gyro['y'], gyro['z']])
        points.append((x, y, z))
        print(f"Recorded point: ({x}, {y}, {z})")

        if play_mode and baseline_hr is not None:
            if len(points) >= 2:
                px, py, pz = points[-2]
                dist = calculate_distance((px, py, pz), (x, y, z))
            else:
                dist = 0.0

            heart_rate, growth_index, decay_index = update_heart_rate(
                heart_rate,
                growth_index,
                decay_index,
                dist,
                baseline_hr,
                baseline_active
            )

            if baseline_active:
                if (heart_rate > baseline_hr + BASELINE_RANGE) or (heart_rate < baseline_hr - BASELINE_RANGE):
                    baseline_active = False

            heart_rate_history.append(heart_rate)

    time.sleep(POLLING_INTERVAL / 1000)
