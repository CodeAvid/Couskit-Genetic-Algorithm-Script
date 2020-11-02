import threading
import requests
from flask import *
from algorithm import evolutionary_algorithm

app = Flask(__name__)


def format_timetable(timetable):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    timetable_data = []
    for d in timetable:
        period = d
        period["Length"] = int(period["Length"])
        period["AssignedDay"] = days[period["AssignedTime"] // 9]
        period["StartHour"] = (period["AssignedTime"] % 9) + 9
        period["EndHour"] = period["StartHour"] + period["Length"]
        period.pop("AssignedTime")
        timetable_data.append(period)

    return timetable_data


def timetable_callback(timetable_data, api_url="https://tbe-node-deploy.herokuapp.com/timetable"):
    timetable = evolutionary_algorithm(timetable_data)
    timetable = format_timetable(timetable)
    r = requests.get(api_url, json=timetable, headers={
        "Content-Type": "application/json"})
    print(timetable)


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
