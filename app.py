# app.py
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
app.secret_key = os.getenv("FLASK_SECRET_KEY", "aistudio_secret")

# -----------------------------
# Create DB Tables if Missing
# -----------------------------
DB_FILE = "messages.db"
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        # original messages table (contact form)
        conn.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            message TEXT
        )""")
        # chat threads & messages tables for chatbots
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_threads (
            id INTEGER PRIMARY KEY,
            bot_key TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY,
            thread_id INTEGER,
            role TEXT,           -- 'user' or 'assistant' or 'system'
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(thread_id) REFERENCES chat_threads(id)
        )""")
init_db()

# -----------------------------
# Email Helper (unchanged)
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
# Bot system prompts
# -----------------------------
BOT_PROMPTS = {
    "real-estate": "You are a helpful, professional Real Estate Assistant 🏡. Provide clear, practical property advice, listings tips, negotiation pointers and next steps. Always include at least one emoji in each reply and keep tone friendly and helpful.",
    "student-mentor": "You are a friendly Student Mentor 🎓. Help with study plans, exam tips, motivation, and short examples. Always include at least one emoji in each reply and use an encouraging tone.",
    "fitness-coach": "You are a motivating Fitness Coach 💪. Provide workout ideas, nutrition tips, and safety warnings. Always include at least one emoji in each reply and be concise and motivating.",
    "restaurant": "You are a Restaurant Assistant 🍽️. Help with menu ideas, recipes, kitchen planning and food safety. Always include at least one emoji in each reply and be practical.",
    "travel-planner": "You are a Travel Planner ✈️. Suggest itineraries, budgets, and packing tips. Always include at least one emoji in each reply and be friendly and clear."
}

# -----------------------------
# LLM integration function
# -----------------------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def generate_bot_reply(system_prompt, conversation_messages):
    """
    conversation_messages: list of dicts: {"role":"user"/"assistant","content": "..."}
    returns: assistant reply string
    """
    # If OPENAI_KEY is not set, fallback to a simple canned echo reply (so UI still works)
    if not OPENAI_KEY:
        # simple fallback: mirror user with emoji
        last_user = ""
        for m in reversed(conversation_messages):
            if m['role'] == 'user':
                last_user = m['content']
                break
        return f"Thanks! I heard: \"{last_user}\" 😊 (demo reply — set OPENAI_API_KEY to enable real AI replies)"

    # Use OpenAI Chat Completions (HTTP) - adapt if you use openai SDK
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }

    # Build messages array: system + conversation
    messages = [{"role": "system", "content": system_prompt}]
    messages += conversation_messages

    body = {
        "model": "gpt-4o-mini",   # change model name if needed
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # extract assistant reply
        reply = data["choices"][0]["message"]["content"].strip()
        return reply
    except Exception as e:
        print("LLM error:", e)
        return "Sorry, I couldn't reach the AI service right now. Please try again later. 😕"

# -----------------------------
# WEBSITE ROUTES (preserve your existing pages)
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

# CONTACT / QUOTE / START PROJECT (preserve your code)
# ... (keep your existing contact, quote, start_project, admin API code)
# For brevity, assume your existing contact, quote and admin API blocks exist below unchanged.
# (If copying, paste your existing functions for /contact, /quote, /start_project and admin APIs here.)
# -------------------------------------------------------------------------
# Chat system routes below
# -------------------------------------------------------------------------

# Serve chat UI for a bot key
@app.route('/chat/<bot_key>')
def chat_page(bot_key):
    if bot_key not in BOT_PROMPTS:
        return "Unknown bot", 404
    bot_title_map = {
        "real-estate": "🏡 Real Estate Assistant",
        "student-mentor": "🎓 Student Mentor",
        "fitness-coach": "💪 Fitness Coach",
        "restaurant": "🍽️ Restaurant Assistant",
        "travel-planner": "✈️ Travel Planner"
    }
    # pass theme key for CSS differences
    theme = bot_key
    title = bot_title_map.get(bot_key, bot_key)
    return render_template('chatbots/base_chat_template.html', bot_key=bot_key, bot_title=title, theme=theme)

# API: create new chat thread
@app.route('/api/create_thread', methods=['POST'])
def api_create_thread():
    data = request.get_json() or {}
    bot_key = data.get('bot_key')
    title = data.get('title') or "New chat"
    if bot_key not in BOT_PROMPTS:
        return jsonify({"error": "invalid bot_key"}), 400
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("INSERT INTO chat_threads (bot_key, title) VALUES (?, ?)", (bot_key, title))
        thread_id = cur.lastrowid
    return jsonify({"thread_id": thread_id})

# API: list threads for a bot
@app.route('/api/threads/<bot_key>')
def api_threads(bot_key):
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT id, title, created_at FROM chat_threads WHERE bot_key=? ORDER BY id DESC", (bot_key,)).fetchall()
    threads = [{"id": r[0], "title": r[1], "created_at": r[2]} for r in rows]
    return jsonify(threads)

# API: get messages for a thread
@app.route('/api/thread/<int:thread_id>/messages')
def api_thread_messages(thread_id):
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT id, role, content, created_at FROM chat_messages WHERE thread_id=? ORDER BY id ASC", (thread_id,)).fetchall()
    msgs = [{"id": r[0], "role": r[1], "content": r[2], "created_at": r[3]} for r in rows]
    return jsonify(msgs)

# Main chat endpoint: receive user message and return AI reply
@app.route('/ask_bot', methods=['POST'])
def ask_bot():
    data = request.get_json() or {}
    thread_id = data.get('thread_id')           # optional: existing thread
    bot_key = data.get('bot')                   # required if creating new thread
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"error": "empty message"}), 400
    if not bot_key:
        return jsonify({"error": "bot required"}), 400
    if bot_key not in BOT_PROMPTS:
        return jsonify({"error": "invalid bot"}), 400

    # create thread if not exists
    if not thread_id:
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.execute("INSERT INTO chat_threads (bot_key, title) VALUES (?, ?)", (bot_key, "New chat"))
            thread_id = cur.lastrowid

    # store user message
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO chat_messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, "user", user_message))

    # fetch conversation history to send to LLM (we'll fetch last 10 messages)
    conv = []
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute("SELECT role, content FROM chat_messages WHERE thread_id=? ORDER BY id DESC LIMIT 20", (thread_id,)).fetchall()
    # rows are reversed (DESC) -> convert to chronological order
    rows = list(reversed(rows))
    for r in rows:
        conv.append({"role": r[0], "content": r[1]})

    # generate assistant reply
    system_prompt = BOT_PROMPTS[bot_key]
    assistant_reply = generate_bot_reply(system_prompt, conv)

    # save assistant reply
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO chat_messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, "assistant", assistant_reply))

    return jsonify({"thread_id": thread_id, "reply": assistant_reply})

# -------------------------------------------------------------------------
# Keep your admin APIs (api_messages, api_projects, ...) and other parts below
# -------------------------------------------------------------------------

# Example: keep your existing admin APIs here (make sure they don't conflict)
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY") or "supersecretadminkey"
def check_api(req):
    return req.headers.get("X-API-KEY") == ADMIN_API_KEY

@app.route('/api/messages')
def api_messages():
    if not check_api(request):
        return jsonify({"error": "unauthorized"}), 401
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(rows)

# ... keep /api/projects, /api/quotes, /api/delete_project etc as in your file

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
