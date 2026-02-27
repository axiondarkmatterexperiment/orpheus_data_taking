# control_api.py
from fastapi import FastAPI, Query
from typing import List
from state import state

app = FastAPI()

@app.get("/status")
def get_status():
    with state.lock:
        return state.__dict__

@app.get("/na_fc")
def get_na_fc():
    with state.lock:
        return {"na_fc": state.na_fc}

@app.get("/na_span")
def get_na_span():
    with state.lock:
        return {"na_span": state.na_span}

@app.get("/get")
def get_value(keys: List[str] = Query(...)):
    """
    Fetch specific attributes from the state.
    Example: /get?keys=na_fc&keys=dl_cm
    """
    result = {}
    with state.lock:
        for key in keys:
            if hasattr(state, key):
                result[key] = getattr(state, key)
            else:
                result[key] = None  # explicitly show missing keys
    return result

@app.post("/set")
def set_value(payload: dict):
    with state.lock:
        for key, value in payload.items():
            if hasattr(state, key):
                setattr(state, key, value)
    return {"success": True}

#@app.get("/get")
#def get_value(payload):
#    with state.lock:
#        for key in payload:
#            if hasattr(state, key):
#                value = getattr(state, key)
#    return value

@app.post("/pause")
def pause():
    state.pause = True
    return {"paused": True}

@app.post("/resume")
def resume():
    state.pause = False
    return {"paused": False}

@app.post("/quit")
def quit_experiment():
    state.run_condition = False
    state.pause = False
    return {"stopping": True}
