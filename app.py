from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import requests
import os
from flask import jsonify
from dotenv import load_dotenv
load_dotenv()


# --- 1️⃣ Create the Flask app instance first ---
app = Flask(__name__)
app.secret_key = "aistudio_secret"


# --- Create DB if not exists ---
if not os.path.exists("messages.db"):
    with sqlite3.connect("messages.db") as conn:
        conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)")


def send_email(subject, to, body):
    url = "https://api.resend.com/emails"
    api_key = os.getenv('RESEND_API_KEY')

    print("\n========== EMAIL DEBUG ==========")
    print("API Key Loaded:", "YES" if api_key else "NO")
    print("Sending To:", to)
    print("Subject:", subject)
    print("=================================\n")

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
        response = requests.post(url, headers=headers, json=data)
        print("Resend Response Status:", response.status_code)
        print("Resend Response Text:", response.text)
        return response.json()
    except Exception as e:
        print("❌ Email send error:", str(e))
        return {"ok": False}


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        with sqlite3.connect("messages.db") as conn:
            conn.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        flash("Message sent successfully! We'll reach out soon 😊")
        msg = Message(
    subject=f"📩 New Contact from {name}",
    recipients=['YOUR_EMAIL@gmail.com'],
    body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")
        mail.send(msg)

        return redirect('/contact')
    return render_template('contact.html')

@app.route('/quote', methods=['POST'])
def quote():
    name = request.form['name']
    email = request.form['email']
    service = request.form['service']
    details = request.form['details']

    with sqlite3.connect("messages.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, name TEXT, email TEXT, service TEXT, details TEXT)")
        conn.execute("INSERT INTO quotes (name, email, service, details) VALUES (?, ?, ?, ?)", (name, email, service, details))
    flash("✅ Quote request sent successfully! We'll contact you soon.")
    msg = Message(
    subject=f"💬 New Quote Request from {name}",
    recipients=['YOUR_EMAIL@gmail.com'],
    body=f"Service: {service}\n\nDetails:\n{details}\n\nEmail: {email}")
    mail.send(msg)

    return redirect('/')
@app.route('/start_project', methods=['GET', 'POST'])
def start_project():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        service = request.form['service']
        budget = request.form['budget']
        details = request.form['details']

        # Save to database
        conn = sqlite3.connect('messages.db')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                company TEXT,
                service TEXT,
                budget TEXT,
                details TEXT
            )
        """)
        cur.execute("""
            INSERT INTO projects (name, email, company, service, budget, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, company, service, budget, details))
        conn.commit()
        conn.close()

        # ----------------------------------------
        # 1️⃣ Email to admin
        # ----------------------------------------
        send_email(
            subject=f"🚀 New Project Request from {name}",
            to="aiautomationstudio30@gmail.com",
            body=f"Name: {name}\nEmail: {email}\nCompany: {company}\nService: {service}\nBudget: {budget}\n\nDetails:\n{details}"
        )

        # ----------------------------------------
        # 2️⃣ Auto-reply to client
        # ----------------------------------------
        client_message = f"""
Hey {name},

Thanks for reaching out to AI Automation Studio! 🎉

We’ve received your project details:

📩 Email: {email}
🏢 Company: {company}
🛠 Service: {service}
💰 Budget: {budget}

Our team will contact you shortly.

— Team AI Automation Studio
"""

        send_email(
            subject="🎯 Thanks for contacting AI Automation Studio!",
            to=email,
            body=client_message
        )

        flash("✅ Your project request was submitted successfully! A confirmation email was sent.")
        return redirect('/start_project')

    return render_template('start_project.html')

@app.route('/ping')
def ping():
    return "✅ Server running fine!"

from flask import jsonify, request

# API KEY SECURITY
ADMIN_API_KEY = "supersecretadminkey"

def check_api_key(req):
    return req.headers.get("X-API-KEY") == ADMIN_API_KEY

# ----------- API: MESSAGES ----------
@app.route('/api/messages')
def api_messages():
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401

    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

# ----------- API: PROJECTS ----------
@app.route('/api/projects')
def api_projects():
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401

    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

# ----------- API: QUOTES ----------
@app.route('/api/quotes')
def api_quotes():
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401

    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM quotes ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

# ----------- API: DELETE PROJECT ----------
@app.route('/api/delete_project/<int:id>', methods=['DELETE'])
def api_delete_project(id):
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401
    
    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


if __name__ == '__main__':
    app.run(debug=True)
