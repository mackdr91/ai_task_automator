from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('task_input.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    task_name = request.form.get('task_name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    recurrence_interval = request.form.get('recurrence_interval')

    # Placeholder: Print values (later save to database)
    print(f"Task: {task_name}, Description: {description}, Start: {start_date}, End: {end_date}, Interval: {recurrence_interval}")

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)