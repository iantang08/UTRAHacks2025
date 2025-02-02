from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId  # For handling MongoDB ObjectId
import os

app = Flask(__name__)

# Load MongoDB Atlas URI from environment variables
username = "dylanydai"
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
    # Fetch statistics data from MongoDB
    stats_data = list(collection.find())
    # pass statistics data to template
    return render_template('statistics.html', stats = stats_data)

if __name__ == '__main__':
    app.run(debug=True)
