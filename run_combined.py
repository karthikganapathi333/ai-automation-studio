import subprocess
import time

print("🚀 Starting FastAPI chatbot API on port 5002...")
fastapi_process = subprocess.Popen(["uvicorn", "chatbots_api.main:app", "--host", "0.0.0.0", "--port", "5002"])

time.sleep(3)

print("🌐 Starting Flask main website on port 5000...")
flask_process = subprocess.Popen(["python", "app.py"])

fastapi_process.wait()
flask_process.wait()
