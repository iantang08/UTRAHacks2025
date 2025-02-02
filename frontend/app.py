import ast
import subprocess

from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from pymongo import MongoClient
from bson.objectid import ObjectId  # For handling MongoDB ObjectId
import sys
import os

STR_LENGTH_LIMIT = 30
# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Now import the Stat class from the backend folder
from Stat import Stat

# Initialize an empty dictionary to store heart rates for each user ID
# Initialize user_heart_rates with sample data containing timestamps
user_heart_rates = {
    1: [    
        {'timestamp': 1609459200%1000, 'heart_rate': 10},
        {'timestamp': 1609459260%1000, 'heart_rate': 75},
        {'timestamp': 1609459320%1000, 'heart_rate': 80},
        # Add more entries as needed
    ],
    2: [
        {'timestamp': 1609459200%1000, 'heart_rate': 65},
        {'timestamp': 1609459260%1000, 'heart_rate': 68},
        # Add more entries as needed
    ]
}

app = Flask(__name__)

# Load MongoDB Atlas URI from environment variables
username = "iantang9000"
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://" + username + ":iloveyordles123@fitness.n3yup.mongodb.net/?retryWrites=true&w=majority&appName=fitness")

try:
    client = MongoClient(MONGO_URI)  # Connect to MongoDB Atlas
    db = client["fitness_db"]  # Database name
    collection = db["exercises"]  # Collection name
    people = db["people"]  # Collection name
    print("✅ Connected to MongoDB Atlas successfully")
except Exception as e:
    print(f"❌ Error connecting to MongoDB Atlas: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        exercise_name = request.form.get('exercise_name').strip()
        if exercise_name and len(exercise_name) <= STR_LENGTH_LIMIT:
            # Prevent duplicate entries
            existing_exercise = collection.find_one({"exercise_name": exercise_name})
            if not existing_exercise:
                collection.insert_one({"exercise_name": exercise_name, "moves": []})  # Store in MongoDB

    # Retrieve all exercises
    exercises = list(collection.find({}, {"exercise_name": 1, "moves": 1}))  # Include MongoDB _id
    
    return render_template('home.html', exercises=exercises)

@app.route('/remove_exercise/<exercise_id>')
def remove_exercise(exercise_id):
    try:
        collection.delete_one({"_id": ObjectId(exercise_id)})  # Remove by MongoDB ObjectId
    except Exception as e:
        print(f"❌ Error deleting exercise: {e}")
    return redirect(url_for('home'))

@app.route('/exercise/<exercise_name>')
def exercise(exercise_name):
    if collection.find_one({"exercise_name": exercise_name}):
        return render_template('exercise.html', exercise_name=exercise_name)
    else:
        return render_template('error.html')

@app.route('/edit/<exercise_name>')
def edit(exercise_name):
    if collection.find_one({"exercise_name": exercise_name}):
        return render_template('edit.html', exercise_name=exercise_name)
    else:
        return render_template('error.html')

# edit script!!!
@app.route('/edit-script/<exercise_name>')
def edit_script(exercise_name):
    def generate():
        # Run the Python script
        process = subprocess.Popen(
            ['python', '../backend/edit.py', ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Stream the output line by line
        for line in process.stdout:
            tuple_list = eval(line)
            collection.update_one(
                {"exercise_name": exercise_name},  # Filter to find the document
                {"$set": {"moves": tuple_list}})
            yield f"data: {line}\n\n"  # SSE format

        # Handle errors
        for line in process.stderr:
            yield "error"

    return Response(generate(), mimetype='text/event-stream')

def generate():
    # Run the Python script
    process = subprocess.Popen(
        ['python', '../backend/edit.py'],
        stdout=subprocess.PIPE,  # Capture stdout
        universal_newlines=True  # Ensure text mode
    )

    # Stream the output line by line
    for line in process.stdout:
        yield f"data: {line}\n\n"

    # Handle errors
    for line in process.stderr:
        yield "error"

# run script!!!
@app.route('/run-script/<exercise_name>')
def run_script(exercise_name):
    return Response(generate(exercise_name), mimetype='text/event-stream')

# ✅ New API Endpoint to Upload Data
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Parse incoming JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Insert data into MongoDB
        result = collection.insert_one(data)
        return jsonify({"message": "Data uploaded successfully", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ API Endpoint to Get All Exercises (Testing)
@app.route('/api/exercises', methods=['GET'])
def get_exercises():
    exercises = list(collection.find({}, {"exercise_name": 1}))
    return jsonify(exercises)

@app.route('/statistics')
def statistics():
    # Create Stat objects for each user
    stats = [
        Stat("John Doe", 1, (25, 36, 50), 75, (25, 35, 75)),
        Stat("Jane Doe", 2, (28, 40, 52), 80, (25, 36, 50))
    ]
    
    # Calculate consistency for each user
    user_consistency = {}
    for stat in stats:
        stat.consistency = stat.calculate_consistency()
        user_consistency[stat.id] = stat.consistency

    # Pass user heart rates and consistency to the template
    return render_template("statistics.html", stats=stats, user_heart_rates=user_heart_rates, user_consistency=user_consistency)

def calculate_average(heart_rate_list):
    return sum(heart_rate_list) / len(heart_rate_list)

@app.route('/update_heart_rate', methods=['POST'])
def update_heart_rate():
    data = request.get_json()
    user_id = data.get('id')
    heart_rate = data.get('heart_rate')
    timestamp = data.get('timestamp')  # Expecting timestamp input

    if not user_id or not heart_rate or not timestamp:
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Insert heart rate data into MongoDB
        db.heart_rates.insert_one({
            "user_id": user_id,
            "heart_rate": heart_rate,
            "timestamp": timestamp
        })

        # Calculate average heart rate for this user
        user_records = list(db.heart_rates.find({"user_id": user_id}))
        heart_rates = [record["heart_rate"] for record in user_records]
        average_heart_rate = sum(heart_rates) / len(heart_rates)

        return jsonify({
            "message": "Heart rate updated successfully",
            "average_heart_rate": average_heart_rate
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/average_heart_rates', methods=['GET'])
def get_average_heart_rates():
    try:
        users = db.heart_rates.distinct("user_id")  # Get unique user IDs
        user_averages = {}

        for user_id in users:
            user_records = list(db.heart_rates.find({"user_id": user_id}))
            heart_rates = [record["heart_rate"] for record in user_records]
            user_averages[user_id] = sum(heart_rates) / len(heart_rates)

        return jsonify(user_averages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/heart_rate_history/<int:user_id>', methods=['GET'])
def get_heart_rate_history(user_id):
    try:
        user_records = list(db.heart_rates.find({"user_id": user_id}, {"_id": 0, "heart_rate": 1, "timestamp": 1}))
        return jsonify(user_records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(threaded=True)
