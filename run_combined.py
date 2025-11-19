# ---------------------------------------------------------
# COMBINED FASTAPI + FLASK SERVER (Render-Compatible)
# ---------------------------------------------------------

import threading
import uvicorn
from chatbots_api.main import app as fastapi_app
from app import app as flask_app

# -----------------------------
# 1) START FASTAPI (PORT 5002)
# -----------------------------
def start_fastapi():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5002)

# Start FastAPI in a thread
threading.Thread(target=start_fastapi, daemon=True).start()


# ---------------------------------------------------------
# 2) PROXY TO FASTAPI FROM FLASK
# ---------------------------------------------------------
from flask import request, Response
import requests

FASTAPI_URL = "http://127.0.0.1:5002"


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
            content_type=resp.headers.get("Content-Type"),
        )

    except Exception as e:
        return {"error": str(e)}, 500


# ---------------------------------------------------------
# 3) START FLASK MAIN WEBSITE (PORT 5000)
# ---------------------------------------------------------
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)
