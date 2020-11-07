import threading
import requests
from flask import *
from algorithm import evolutionary_algorithm

app = Flask(__name__)


def format_timetable(timetable, days):
    timetable_data = []
    for period in timetable:
        startHour = (period["AssignedTime"] % 9) + 9
        d = {
            "name": period["Subject"],
            "lecturer": period["Professor"],
            "type": "theory" if period["Type"] == "Theory" else "lab",
            "assignedDay": days[period["AssignedTime"] // 9],
            "startHour": startHour,
            "venue": period["AssignedClassroom"],
            "endHour": startHour + int(period["Length"])
        }
        timetable_data.append(d)

    return {"courses": timetable_data}


def preformat_timetable(timetable):
    classes = []
    for i, j in enumerate(timetable["courses"]):
        class_data = {
            "Subject": j["name"],
            "Type": "Theory" if j["type"] == "theory" else "Practical",
            "Professor": j["lecturer"],
            "Groups": [f"{i}"],
            "AllowedClassrooms": [i for i in timetable["classroom"] if timetable["classroom"][i]["capacity"] >= j["students"]]
        }
        if j["unit"] in [1, 2]:
            class_data["Length"] = str(j["unit"])
            classes.append(class_data)
        if j["unit"] == 3:
            class_data["Length"] = "1"
            classes.append(class_data)
            class_data["Length"] = "2"
            classes.append(class_data)
        if j["unit"] == 4:
            class_data["Length"] = "2"
            classes.append(class_data)
            class_data["Length"] = "2"
            classes.append(class_data)
    return classes


def timetable_callback(timetable_data, api_url="https://tbe-node-deploy.herokuapp.com/timetable"):
    days = timetable_data["selectedDay"]
    timetable = preformat_timetable(timetable_data)
    timetable = evolutionary_algorithm(
        timetable, api_url, days=days, timetable_id=timetable_data["timetableId"])
    timetable = format_timetable(timetable, days=days)
    timetable["timetableName"] = timetable_data["timetableName"]
    timetable["academicSession"] = timetable_data["academicSession"]
    timetable["timetableId"] = timetable_data["timetableId"]
    r = requests.get(api_url, json=timetable, headers={"Content-Type": "application/json"}, params={
                     "current_progress": 5000, "total_progress": 5000, "timetableId": timetable_data["timetableId"]})


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
        return jsonify({"success": False, "message": "the timetable data is missing"}), 400
    valid = True
    if None in [timetable_data.get("classroom"), timetable_data.get("courses"), timetable_data.get("selectedDay")]:
        valid = False
    if valid and (not isinstance(timetable_data.get("classroom"), dict)):
        valid = False
    if valid and (not isinstance(timetable_data.get("courses"), list)):
        valid = False
    if valid and (not isinstance(timetable_data.get("selectedDay"), list)):
        valid = False
    if valid:
        for i in timetable_data.get("classroom"):
            j = timetable_data["classroom"][i]
            if None in [j.get("type"), j.get("capacity")]:
                valid = False
                break
            if (not isinstance(j.get("type"), str)) or (not isinstance(j.get("capacity"), int)):
                valid = False
                break
            if j.get("type") not in ["theory", "lab"]:
                valid = False
                break
    if valid:
        for i in timetable_data.get("courses"):
            if None in [i.get("name"), i.get("lecturer"), i.get("type"), i.get("students"), i.get("unit")]:
                valid = False
                break
            if (not isinstance(i.get("name"), str)) or (not isinstance(i.get("lecturer"), str)) or (not isinstance(i.get("type"), str)) or (not isinstance(i.get("students"), int)) or (not isinstance(i.get("unit"), int)):
                valid = False
                break
            if i.get("type") not in ["theory", "lab"]:
                valid = False
                break
    if not valid:
        return jsonify({"success": False, "message": "the timetable data is not correctly formatted"}), 422

    thread = threading.Thread(target=timetable_callback, args=[timetable_data])
    thread.start()
    return jsonify({
        "success": True,
        "message": "the timetable is being generated",
        "current_progress": 0,
        "total_progress": 5000
    }), 202


if __name__ == "__main__":
    app.run(debug=True)
