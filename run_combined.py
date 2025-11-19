import subprocess
import time
import threading
from flask import Flask, request, Response
import requests

# ---------------------------------------
# 1) START FASTAPI IN BACKGROUND
# ---------------------------------------
def start_fastapi():
    subprocess.run([
        "uvicorn",
        "chatbots_api.main:app",
        "--host", "0.0.0.0",
        "--port", "5002"
    ])

threading.Thread(target=start_fastapi, daemon=True).start()
time.sleep(3)

# ---------------------------------------
# 2) CREATE FLASK APP
# ---------------------------------------
app = Flask(__name__)
app.secret_key = "aistudio_secret"

# ---------------------------------------
# 3) ADD CHATBOT API PROXY ROUTE
# ---------------------------------------
FASTAPI_URL = "http://127.0.0.1:5002"

@app.route("/chatbot_api_proxy/<path:path>", methods=["GET", "POST"])
def chatbot_api_proxy(path):
    url = f"{FASTAPI_URL}/{path}"

    try:
        if request.method == "GET":
            resp = requests.get(url, params=request.args)
        else:
            resp = requests.post(url, json=request.get_json())

        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type")
        )

    except Exception as e:
        return {"error": str(e)}, 500

# ---------------------------------------
# 4) IMPORT FLASK MAIN ROUTES (from app.py)
# ------
