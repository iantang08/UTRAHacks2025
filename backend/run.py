import math
import random
from pyjoycon import JoyCon, get_L_id, get_R_id
import time
from pymongo import MongoClient
from flask import Flask, request
from bson.objectid import ObjectId
import os

username = "iantang9000"
MONGO_URI = os.getenv("MONGO_URI", f"mongodb+srv://{username}:iloveyordles123@fitness.n3yup.mongodb.net/?retryWrites=true&w=majority&appName=fitness")

client = MongoClient(MONGO_URI)  # Connect to MongoDB Atlas
db = client["fitness_db"]  # Database name
collection = db["exercises"]  # Collection name

app = Flask(__name__)

POLLING_INTERVAL = 150
TOLERANCE = 20
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

joycon_id = get_R_id()
joycon = None
try:
    joycon = JoyCon(*joycon_id)
except Exception as e:
    print(f"Error initializing JoyCon: {e}")
    joycon = None

def calculate_distance(point1, point2):
    """Euclidean distance in 3D."""
    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))

def calculate_score(user_points, ideal_points):
    """
    Compare the user's points vs. the recorded ideal points,
    returning a score from 0 to 100 (best).
    """
    if not user_points or not ideal_points:
        return 0

    min_length = min(len(user_points), len(ideal_points))
    total_penalty = 0.0

    for i in range(min_length):
        dist = calculate_distance(user_points[i], ideal_points[i])
        penalty = (dist - TOLERANCE) ** VARIANCE_POWER if dist > TOLERANCE else 0
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
    """
    Updates heart_rate given the distance (dist) between consecutive frames.
    """
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

@app.route('/')
def home():
    host = request.host
    exercise_name = host[host.rfind('/'):]
    elm = collection
