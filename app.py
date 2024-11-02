from flask import Flask, render_template, request, redirect, url_for, session
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production!

# Supabase setup
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

@app.route('/')
def home():
    return render_template('task_input.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    task_name = request.form.get('task_name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    recurrence_interval = request.form.get('recurrence_interval')

    # Save task to Supabase
    supabase.table('tasks').insert({
        "user_id": user_id,
        "task_name": task_name,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "recurrence_interval": recurrence_interval
    }).execute()

    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        # Save user to Supabase
        supabase.table('users').insert({"email": email, "password": hashed_password}).execute()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user from Supabase
        user = supabase.table('users').select("*").eq('email', email).execute()
        if user.data and check_password_hash(user.data[0]['password'], password):
            session['user_id'] = user.data[0]['id']
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)