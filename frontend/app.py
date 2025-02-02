from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId  # For handling MongoDB ObjectId
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Now import the Stat class from the backend folder
from Stat import Stat

# Initialize an empty dictionary to store heart rates for each user ID
# Initialize user_heart_rates with sample data containing timestamps
user_heart_rates = {
    1: [
        {'timestamp': 1609459200, 'heart_rate': 72},
        {'timestamp': 1609459260, 'heart_rate': 75},
        {'timestamp': 1609459320, 'heart_rate': 78},
        # Add more entries as needed
    ],
    2: [
        {'timestamp': 1609459200, 'heart_rate': 65},
        {'timestamp': 1609459260, 'heart_rate': 68},
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
        if exercise_name and len(exercise_name) <= 20:
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
    stats = [
        Stat("John Doe", 1, (25, 36, 50), 75, (25, 35, 50)),
        Stat("Jane Doe", 2, (28, 40, 52), 80, (25, 36, 50))
    ]
    
    # Calculate consistency for each stat and pass to template
    for stat in stats:
        stat.consistency = stat.calculate_consistency()
    
    return render_template("statistics.html", stats=stats)

def calculate_average(heart_rate_list):
    return sum(heart_rate_list) / len(heart_rate_list)

@app.route('/update_heart_rate', methods=['POST'])
def update_heart_rate():
    data = request.get_json()

    user_id = data['id']
    heart_rate = data['heart_rate']

    # If the user doesn't have a heart rate list, create one
    if user_id not in user_heart_rates:
        user_heart_rates[user_id] = []

    # Add the new heart rate to the list
    user_heart_rates[user_id].append(heart_rate)

    # If the list exceeds 10, pop the first (oldest) heart rate
    if len(user_heart_rates[user_id]) > 10:
        user_heart_rates[user_id].pop(0)

    # Calculate the average heart rate if we have 10 or more entries
    average_heart_rate = calculate_average(user_heart_rates[user_id])

    # Store the average heart rate (you could save it to a database)
    user_heart_rates[user_id].append(average_heart_rate)

    return jsonify({
        'message': 'Heart rate updated successfully',
        'average_heart_rate': average_heart_rate
    })

if __name__ == '__main__':
    app.run(debug=True)
