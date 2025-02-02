from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for exercises
exercises = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        exercise_name = request.form.get('exercise_name')
        if exercise_name:
            exercises.append(exercise_name)
    return render_template('home.html', exercises=exercises)

@app.route('/remove_exercise/<exercise_name>')
def remove_exercise(exercise_name):
    if exercise_name in exercises:
        exercises.remove(exercise_name)
    return redirect(url_for('home'))

@app.route('/exercise/<exercise_name>')
def exercise(exercise_name):
    return render_template('exercise.html', exercise_name=exercise_name)

if __name__ == '__main__':
    app.run(debug=True)
