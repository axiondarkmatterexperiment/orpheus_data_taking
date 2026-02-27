# main.py
import threading
from experiment_engine import take_data
import uvicorn
from control_api import app

# Start experiment thread
threading.Thread(target=take_data, daemon=True).start()

# Start API server
uvicorn.run(app, host="0.0.0.0", port=8000)
