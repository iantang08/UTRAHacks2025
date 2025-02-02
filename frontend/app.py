from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId  # For handling MongoDB ObjectId
import os

app = Flask(__name__)

# Load MongoDB Atlas URI from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://<user>:<pass>@fitness.n3yup.mongodb.net/?retryWrites=true&w=majority&appName=fitness")

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
        if exercise_name:
            # Prevent duplicate entries
            existing_exercise = collection.find_one({"exercise_name": exercise_name})
            if not existing_exercise:
                collection.insert_one({"exercise_name": exercise_name})  # Store in MongoDB

    # Retrieve all exercises
    exercises = list(collection.find({}, {"_id": 1, "exercise_name": 1}))  # Include MongoDB _id
    
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
    return render_template('exercise.html', exercise_name=exercise_name)

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
    exercises = list(collection.find({}, {"_id": 0, "exercise_name": 1}))
    return jsonify(exercises)

if __name__ == '__main__':
    app.run(debug=True)
