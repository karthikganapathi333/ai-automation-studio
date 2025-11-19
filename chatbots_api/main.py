# chatbots_api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
from typing import List, Dict
from openai import OpenAI
# Load env
load_dotenv()

client = OpenAI(api_key=OPENAI_KEY, http_client=None)



app = FastAPI(title="AI Automation Studio Chatbots API")

# ---------------- DB Setup ----------------
DB_PATH = "chat_history.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        sender TEXT,
        text TEXT,
        timestamp TEXT,
        FOREIGN KEY(chat_id) REFERENCES chats(id)
    )
    """)

    conn.commit()
    conn.close()

def save_message(chat_id: int, sender: str, text: str):
    conn = get_db()
    cur = conn.cursor()
    now = datetime.now().isoformat()

    cur.execute(
        "INSERT INTO messages (chat_id, sender, text, timestamp) VALUES (?, ?, ?, ?)",
        (chat_id, sender, text, now)
    )

    conn.commit()
    conn.close()

init_db()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Models ----------------
class Message(BaseModel):
    chat_id: int
    message: str


# ---------------- Chat Session Endpoints ----------------

@app.post("/api/chat/new")
async def create_chat():
    conn = get_db()
    cur = conn.cursor()

    now = datetime.now().isoformat()
    cur.execute("INSERT INTO chats (title, created_at) VALUES (?, ?)", ("New Chat", now))
    chat_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {"chat_id": chat_id}


@app.post("/api/chat/title")
async def generate_title(data: Dict):
    chat_id = data.get("chat_id")
    user_message = data.get("message", "")

    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id required")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate a short, clean chat title (max 5 words)."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=16,
        )

        title = response.choices[0].message.content.strip()
        if not title:
            title = "Conversation"

    except Exception:
        title = "Conversation"

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
    conn.commit()
    conn.close()

    return {"title": title}


@app.get("/api/chat/list")
async def list_chats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, title, created_at FROM chats ORDER BY id DESC")
    rows = cur.fetchall()

    chats = [
        {"id": r["id"], "title": r["title"] or "New Chat", "created_at": r["created_at"]}
        for r in rows
    ]

    conn.close()
    return {"chats": chats}


@app.get("/api/chat/{chat_id}/messages")
async def get_chat_messages(chat_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
    rows = cur.fetchall()

    msgs = [
        {
            "id": r["id"],
            "chat_id": r["chat_id"],
            "sender": r["sender"],
            "text": r["text"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]

    conn.close()
    return {"messages": msgs}


@app.delete("/api/chat/{chat_id}/delete")
async def delete_chat(chat_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cur.execute("DELETE FROM chats WHERE id = ?", (chat_id,))

    conn.commit()
    conn.close()

    return {"status": "deleted"}


# ---------------- AI Helper Function ----------------

def call_chat_model(system_prompt: str, user_msg: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    )
    return response.choices[0].message.content.strip()


# ---------------- Individual Chatbots ----------------

@app.post("/api/real-estate/chat")
async def chat_real_estate(msg: Message):
    save_message(msg.chat_id, "user", msg.message)

    system_prompt = (
        "You are a professional real estate assistant. "
        "Use headings, bullet points, and short paragraphs. Avoid markdown symbols."
    )

    reply = call_chat_model(system_prompt, msg.message)
    save_message(msg.chat_id, "bot", reply)

    return {"reply": reply}


@app.post("/api/student-mentor/chat")
async def chat_student(msg: Message):
    save_message(msg.chat_id, "user", msg.message)

    system_prompt = (
        "You are a friendly student mentor. Provide helpful, motivating answers."
    )

    reply = call_chat_model(system_prompt, msg.message)
    save_message(msg.chat_id, "bot", reply)

    return {"reply": reply}


@app.post("/api/fitness-coach/chat")
async def chat_fitness(msg: Message):
    save_message(msg.chat_id, "user", msg.message)

    system_prompt = (
        "You are a certified fitness coach. Provide workouts, diets, tips in bullet form."
    )

    reply = call_chat_model(system_prompt, msg.message)
    save_message(msg.chat_id, "bot", reply)

    return {"reply": reply}


@app.post("/api/restaurant/chat")
async def chat_restaurant(msg: Message):
    save_message(msg.chat_id, "user", msg.message)

    system_prompt = (
        "You are a cooking & restaurant assistant. Provide recipes, tips, steps."
    )

    reply = call_chat_model(system_prompt, msg.message)
    save_message(msg.chat_id, "bot", reply)

    return {"reply": reply}


@app.post("/api/travel-planner/chat")
async def chat_travel(msg: Message):
    save_message(msg.chat_id, "user", msg.message)

    system_prompt = (
        "You are a travel planner. Provide itineraries, costs, tips in bullet points."
    )

    reply = call_chat_model(system_prompt, msg.message)
    save_message(msg.chat_id, "bot", reply)

    return {"reply": reply}


# Health
@app.get("/health")
async def health():
    return {"status": "ok"}
