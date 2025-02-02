from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Load exercises from a JSON file
def load_exercises():
    try:
        with open('exercises.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save exercises to a JSON file
def save_exercises(exercises):
    with open('exercises.json', 'w') as f:
        json.dump(exercises, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/home')
def home():
    exercises = load_exercises()
    return render_template('home.html', exercises=exercises)

@app.route('/exercise/<name>')
def exercise(name):
    return render_template('exercise.html', name=name)

@app.route('/api/exercises', methods=['GET', 'POST'])
def api_exercises():
    exercises = load_exercises()
    if request.method == 'POST':
        new_exercise = request.json['exercise']
        if new_exercise not in exercises:
            exercises.append(new_exercise)
            save_exercises(exercises)
            return jsonify({"success": True, "message": "Exercise added successfully"})
        else:
            return jsonify({"success": False, "message": "Exercise already exists"}), 400
    return jsonify(exercises)

@app.route('/api/exercises/<name>', methods=['DELETE'])
def api_delete_exercise(name):
    exercises = load_exercises()
    if name in exercises:
        exercises.remove(name)
        save_exercises(exercises)
        return jsonify({"success": True, "message": "Exercise deleted successfully"})
    return jsonify({"success": False, "message": "Exercise not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

