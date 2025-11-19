# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory, abort, Response
import sqlite3
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# --- 1️⃣ Create the Flask app instance first ---
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "aistudio_secret"

# --- Create DB if not exists ---
if not os.path.exists("messages.db"):
    with sqlite3.connect("messages.db") as conn:
        conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)")

# (your existing helper functions - preserve)
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

# -------------------------
# Your existing Flask routes
# (I left them exactly as you provided — unchanged)
# -------------------------
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
        # Email sending code (keeps the same calls you had)
        try:
            from flask_mail import Message, Mail
            mail = Mail(app)
            msg = Message(
                subject=f"📩 New Contact from {name}",
                recipients=['YOUR_EMAIL@gmail.com'],
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
        except Exception as e:
            print("Mail send error (contact):", e)

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
    try:
        from flask_mail import Message, Mail
        mail = Mail(app)
        msg = Message(
            subject=f"💬 New Quote Request from {name}",
            recipients=['YOUR_EMAIL@gmail.com'],
            body=f"Service: {service}\n\nDetails:\n{details}\n\nEmail: {email}"
        )
        mail.send(msg)
    except Exception as e:
        print("Mail send error (quote):", e)

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

        # Email admin + auto-reply using send_email helper
        send_email(
            subject=f"🚀 New Project Request from {name}",
            to="aiautomationstudio30@gmail.com",
            body=f"Name: {name}\nEmail: {email}\nCompany: {company}\nService: {service}\nBudget: {budget}\n\nDetails:\n{details}"
        )

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

@app.route('/ai-chatbots')
def ai_chatbots():
    return render_template('ai_chatbots.html')

@app.route('/ping')
def ping():
    return "✅ Server running fine!"

# -------------------------
# API keys + admin APIs (unchanged)
# -------------------------
ADMIN_API_KEY = "supersecretadminkey"
def check_api_key(req):
    return req.headers.get("X-API-KEY") == ADMIN_API_KEY

@app.route('/api/messages')
def api_messages():
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/projects')
def api_projects():
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/api/quotes')
def api_quotes():
    if not check_api_key(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM quotes ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

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

# --- CHATBOT INTEGRATION ---
# Serve the React build copy placed in static/chatbot (index.html + assets)
CHATBOT_BUILD_DIR = os.path.join(app.static_folder, "chatbot")  # static/chatbot/

@app.route('/chat/<path:subpath>', methods=['GET'])
def serve_chat_app(subpath):
    """
    Any route under /chat/* should serve the React app index (so React Router handles it).
    Example: /chat/real-estate or /chat/fitness-coach
    """
    index_path = os.path.join(CHATBOT_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(CHATBOT_BUILD_DIR, "index.html")
    else:
        # If build not present, show friendly message with instructions
        return """
        <h2>Chat UI not found</h2>
        <p>Please build the chatbot frontend and copy the build into <code>static/chatbot/</code></p>
        <p>Commands:</p>
        <pre>
        cd chatbot_frontend
        npm install
        npm run build
        mkdir -p ../static/chatbot
        cp -r dist/* ../static/chatbot/
        </pre>
        """, 500

@app.route('/chatbot_assets/<path:filename>')
def serve_chatbot_assets(filename):
    """
    Serve any static asset requested by the chatbot build.
    In React build, assets paths will be relative and should map to /chatbot_assets/<asset>.
    (When copying build into static/chatbot, preserve paths)
    """
    file_path = os.path.join(CHATBOT_BUILD_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(CHATBOT_BUILD_DIR, filename)
    return abort(404)

@app.route('/chatbot_api_proxy/<path:url_path>', methods=['GET', 'POST'])
def chatbot_api_proxy(url_path):
    """
    Proxy requests to the chat API server (127.0.0.1:5002).
    Example client call path: /chatbot_api_proxy/api/real-estate/chat
    This avoids CORS and makes frontend call the same origin.
    """
    target_base = "http://127.0.0.1:5002"
    target_url = f"{target_base}/{url_path}"
    try:
        if request.method == "GET":
            resp = requests.get(target_url, params=request.args, timeout=15)
            return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
        else:
            # POST — forward JSON/body & headers
            headers = {k: v for k, v in request.headers if k.lower() != "host"}
            resp = requests.post(target_url, json=request.get_json(silent=True), data=request.form or None, headers=headers, timeout=30)
            return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        return jsonify({"error": "proxy error", "detail": str(e)}), 500

from flask import send_from_directory

# Serve built React frontend
@app.route('/chat/<path:subpath>')
def serve_chat_ui(subpath):
    return app.send_static_file(f'chatbot/index.html')

@app.route('/chat')
def chatbot_root():
    return app.send_static_file('chatbot/index.html')

# Serve JS/CSS assets
@app.route('/assets/<path:filename>')
def chatbot_assets(filename):
    return app.send_static_file(f'chatbot/assets/{filename}')

# --------------------------------------------
# PROXY CHATBOT API ROUTES  (Required for Render)
# --------------------------------------------
import requests

CHATBOT_API_URL = "http://127.0.0.1:5002"

@app.route("/chatbot_api_proxy/<path:path>", methods=["GET", "POST"])
def chatbot_api_proxy(path):
    url = f"{CHATBOT_API_URL}/{path}"

    try:
        if request.method == "POST":
            resp = requests.post(url, json=request.get_json())
        else:
            resp = requests.get(url, params=request.args)

        return (resp.text, resp.status_code, resp.headers.items())

    except Exception as e:
        return {"error": "proxy_failed", "details": str(e)}, 500

# -------------------------
# End chatbot integration
# -------------------------

if __name__ == '__main__':
    # When developing: run Flask as usual (chat API must be started separately on :5002)
    app.run(debug=True, host="0.0.0.0", port=5000)
