from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "aistudio_secret"

# -----------------------------
# Create DB Tables if Missing
# -----------------------------
if not os.path.exists("messages.db"):
    with sqlite3.connect("messages.db") as conn:
        conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)")

# -----------------------------
# Email Helper
# -----------------------------
def send_email(subject, to, body):
    url = "https://api.resend.com/emails"
    api_key = os.getenv('RESEND_API_KEY')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "from": "AI Automation Studio <noreply@aiautomationstudio.online>",
        "to": [to],
        "subject": subject,
        "text": body
    }

    try:
        resp = requests.post(url, headers=headers, json=data)
        return resp.json()
    except Exception as e:
        print("Email error:", e)
        return {"ok": False}

# -----------------------------
# WEBSITE ROUTES
# -----------------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/ai-chatbots')
def ai_chatbots():
    return render_template('ai_chatbots.html')

@app.route('/ping')
def ping():
    return "Server alive!"

# CONTACT FORM
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        with sqlite3.connect("messages.db") as conn:
            conn.execute(
                "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                (name, email, message)
            )

        flash("Message received! Thank you 😊")
        return redirect('/contact')

    return render_template('contact.html')

# QUOTE FORM
@app.route('/quote', methods=['POST'])
def quote():
    name = request.form['name']
    email = request.form['email']
    service = request.form['service']
    details = request.form['details']

    with sqlite3.connect("messages.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            service TEXT,
            details TEXT
        )""")
        conn.execute(
            "INSERT INTO quotes (name, email, service, details) VALUES (?, ?, ?, ?)",
            (name, email, service, details)
        )

    flash("Quote submitted successfully!")
    return redirect('/')

# START PROJECT FORM
@app.route('/start_project', methods=['GET', 'POST'])
def start_project():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        service = request.form['service']
        budget = request.form['budget']
        details = request.form['details']

        with sqlite3.connect("messages.db") as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                company TEXT,
                service TEXT,
                budget TEXT,
                details TEXT
            )""")
            conn.execute(
                "INSERT INTO projects (name, email, company, service, budget, details) VALUES (?, ?, ?, ?, ?, ?)",
                (name, email, company, service, budget, details)
            )

        # Send email to admin
        send_email(
            subject=f"New Project from {name}",
            to="aiautomationstudio30@gmail.com",
            body=f"Name: {name}\nEmail: {email}\nCompany: {company}\nService: {service}\nBudget: {budget}\n\n{details}"
        )

        # Auto-response email
        send_email(
            subject="Thanks for contacting AI Automation Studio!",
            to=email,
            body=f"Hello {name},\n\nThank you for your project request! We'll contact you soon.\n\n— Team AI Automation Studio"
        )

        flash("Project submitted successfully!")
        return redirect('/start_project')

    return render_template('start_project.html')

# -----------------------------
# ADMIN APIs
# -----------------------------
ADMIN_API_KEY = "supersecretadminkey"

def check_api(req):
    return req.headers.get("X-API-KEY") == ADMIN_API_KEY

@app.route('/api/messages')
def api_messages():
    if not check_api(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect("messages.db")
    rows = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/projects')
def api_projects():
    if not check_api(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect("messages.db")
    rows = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/quotes')
def api_quotes():
    if not check_api(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect("messages.db")
    rows = conn.execute("SELECT * FROM quotes ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/delete_project/<int:id>', methods=['DELETE'])
def api_delete(id):
    if not check_api(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect("messages.db")
    conn.execute("DELETE FROM projects WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

# -----------------------------
# Run Locally
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
