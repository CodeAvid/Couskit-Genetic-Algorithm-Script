import threading
import requests
from flask import *
from algorithm import evolutionary_algorithm

app = Flask(__name__)


def timetable_callback(timetable_data, api_url="http://127.0.0.1:5000"):
    timetable = evolutionary_algorithm(timetable_data)
    r = requests.get(api_url, json=timetable, headers={
        "Content-Type": "application/json"})


@app.route("/")
def index():
    return "Hello World!"


@app.route("/generate/")
def generate():
    timetable_data = request.get_json()
    thread = threading.Thread(target=timetable_callback, args=[timetable_data])
    thread.start()
    return {"success": True}, 202


if __name__ == "__main__":
    app.run(debug=True)
