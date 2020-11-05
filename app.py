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


@app.route("/")
def index():
    return "Hello World!"


@app.route("/generate/")
def generate():
    try:
        timetable_data = request.get_json()
        if timetable_data == None:
            raise Exception()
    except:
        return {"success": False, "message": "the timetable data is missing"}, 400
    if timetable_data.get("Classrooms") == None:
        return {"success": False, "message": "Classrooms variable is missing from the input"}, 400
    else:
        if not isinstance(timetable_data["Classrooms"], dict):
            return {"success": False, "message": "Classrooms variable must be a dictionary"}, 400
        for i in timetable_data["Classrooms"]:
            if not isinstance(timetable_data["Classrooms"][i], list):
                return {"success": False, "message": "each key in Classrooms dictionary must be a list"}, 400

    if timetable_data.get("Classes") == None:
        return {"success": False, "message": "Classes variable is missing from the input"}, 400
    else:
        if not isinstance(timetable_data["Classes"], list):
            return {"success": False, "message": "Classes variable must be a list"}, 400
        for i in timetable_data["Classes"]:
            if not isinstance(i, dict):
                return {"success": False, "message": "each element in Classes list must be a dictionary"}, 400
            if i.get("Subject") == None or i.get("Type") == None or i.get("Professor") == None or i.get("Groups") == None or i.get("AllowedClassrooms") == None or i.get("Length") == None:
                return {"success": False, "message": "each element in Classes list must be a dictionary containing all of Subject, Type, Professor, Groups, AllowedClassrooms and Length"}, 400
            if not isinstance(i["Groups"], list):
                return {"success": False, "message": "Groups variable in Classes dictionary must be a list"}, 400

    thread = threading.Thread(target=timetable_callback, args=[timetable_data])
    thread.start()
    return {"success": True, "message": "the timetable is being generated"}, 202


if __name__ == "__main__":
    app.run(debug=True)
