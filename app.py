from flask import Flask, render_template, request, redirect, url_for, session
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

import openai
load_dotenv  # Loads environment variables from a `.env` file, if available

# Initialize OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


load_dotenv()  # Load environment variables from a .env file

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Secret key for session management (update this in production for security)

# Supabase setup - URL and Key are fetched from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)  # Initializes the Supabase client

# Define a route for the homepage
@app.route("/")
def home():
    # Render the home page template `task_input.html`
    return render_template("task_input.html")


# Define a route to add a task, only accessible via POST requests
@app.route("/add_task", methods=["POST"])
def add_task():
    # Check if user is logged in (session contains user_id)
    if "user_id" not in session:
        return redirect(url_for("login"))  # Redirect to login if not authenticated

    # Retrieve current user ID from session and task data from the form
    user_id = session["user_id"]
    task_name = request.form.get("task_name")
    description = request.form.get("description")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    recurrence_interval = request.form.get("recurrence_interval")

    # Insert the task into the Supabase "tasks" table with the collected information
    supabase.table("tasks").insert(
        {
            "user_id": user_id,
            "task_name": task_name,
            "description": description,
            "start_date": start_date,
            "end_date": end_date,
            "recurrence_interval": recurrence_interval,
        }
    ).execute()

    return redirect(url_for("home"))  # Redirect to home page after adding task


# Define a route for user registration
@app.route("/register", methods=["GET", "POST"])
def register():
    # Handle form submission (only process POST requests)
    if request.method == "POST":
        email = request.form.get("email")  # Get email from form
        password = request.form.get("password")  # Get password from form
        hashed_password = generate_password_hash(password)  # Hash the password for security

        # Insert the new user into the Supabase "users" table
        supabase.table("users").insert(
            {"email": email, "password": hashed_password}
        ).execute()
        return redirect(url_for("login"))  # Redirect to login after successful registration

    # Render registration template if request method is GET
    return render_template("register.html")


# Define a route for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Handle form submission (only process POST requests)
    if request.method == "POST":
        email = request.form.get("email")  # Get email from form
        password = request.form.get("password")  # Get password from form

        # Fetch user data from Supabase based on the provided email
        user = supabase.table("users").select("*").eq("email", email).execute()

        # Verify password and check if user exists
        if user.data and check_password_hash(user.data[0]["password"], password):
            session["user_id"] = user.data[0]["id"]  # Save user ID in session for authentication
            return redirect(url_for("home"))  # Redirect to homepage after successful login
        else:
            return "Invalid credentials", 401  # Return error for invalid login

    # Render login template if request method is GET
    return render_template("login.html")


# Define a route for user logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove user ID from session to log out
    return redirect(url_for("login"))  # Redirect to login page


# Define a route to handle chat interactions, accessible only via POST requests
@app.route("/chat", methods=["POST"])
def chat():
    # Get the user's message from the JSON request body
    user_message = request.json.get("message")

    # Check if a message was provided
    if not user_message:
        return {"error": "Message is required"}, 400  # Return error if message is missing

    # Send user message to OpenAI API to generate a response
    response = openai.chat.completions.create(model="gpt-4o-mini",  # Specify the OpenAI model
            messages=[
                {
                    "role": "system",
                    "content": """
                    Role:
                    You are a professional AI assistant that manages tasks and scheduling.

                    Task:
                    Your job is to provide task details, including the task name, description, start and end dates, and recurrence interval.
                    Assist the user in creating tasks""",
                },
                {"role": "user", "content": user_message},
           ])

    # Extract the assistant's reply from the OpenAI response
    agent_reply = response.choices[0].message.content.strip()
    return {"reply": agent_reply}  # Return the reply as JSON


# Run the Flask app in debug mode
if __name__ == "__main__":
    app.run(debug=True)