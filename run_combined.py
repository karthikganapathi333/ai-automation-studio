import threading
import uvicorn
import requests
from flask import request, Response

# -----------------------------
# IMPORT FLASK MAIN APP
# -----------------------------
import app as flask_app_module
flask_app = flask_app_module.app

# -----------------------------
# START FASTAPI SERVER
# -----------------------------
def start_fastapi():
    uvicorn.run(
        "chatbots_api.main:app",
        host="0.0.0.0",
        port=5002
    )

FASTAPI_URL = "http://127.0.0.1:5002"

# -----------------------------
# PROXY ROUTE
# -----------------------------
@flask_app.route("/chatbot_api_proxy/<path:path>", methods=["GET", "POST"])
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

# -----------------------------
# RUN BOTH SERVERS
# -----------------------------
if __name__ == "__main__":
    # Start FastAPI in background
    t = threading.Thread(target=start_fastapi)
    t.daemon = True
    t.start()

    # Start Flask normally
    flask_app.run(host="0.0.0.0", port=5000)
