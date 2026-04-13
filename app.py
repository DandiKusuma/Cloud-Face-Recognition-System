import face_recognition
import numpy as np
import cv2
import pickle

from flask import Flask, request, jsonify

ENCODING_FILE = "encodings.pkl"

with open(ENCODING_FILE, "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

app = Flask(__name__)

doors = {
    "door1": {"username": "admin1", "password": "1234", "unlock": False},
    "door2": {"username": "admin2", "password": "5678", "unlock": False},
    "door3": {"username": "admin3", "password": "9999", "unlock": False},
}

@app.route("/")
def home():
    return "Cloud Server Running"

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    door_id = data.get("door_id")
    username = data.get("username")
    password = data.get("password")

    if door_id in doors:
        if doors[door_id]["username"] == username and doors[door_id]["password"] == password:
            doors[door_id]["unlock"] = True
            return jsonify({"status": "success"})
    return jsonify({"status": "failed"})

@app.route("/remote_status/<door_id>")
def remote_status(door_id):
    if door_id in doors:
        if doors[door_id]["unlock"]:
            doors[door_id]["unlock"] = False
            return jsonify({"unlock": True})
        return jsonify({"unlock": False})
    return jsonify({"unlock": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route("/check_face", methods=["POST"])
def check_face():

    img_bytes = request.data

    if not img_bytes or len(img_bytes) < 100:
        return jsonify({"result": "NO_IMAGE", "name": "Unknown"})

    np_img = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"result": "ERROR", "name": "Unknown"})

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)

    if len(encodings) == 0:
        return jsonify({"result": "NO_FACE", "name": "Unknown"})

    encoding = encodings[0]

    distances = face_recognition.face_distance(known_encodings, encoding)
    best_match_index = np.argmin(distances)

    if distances[best_match_index] < 0.5:

        name = known_names[best_match_index]

        print("MATCH:", name)

        return jsonify({
            "result": "FACE_OK",
            "name": name
        })

    else:

        return jsonify({
            "result": "UNKNOWN",
            "name": "Unknown"
        })

@app.route("/log_access", methods=["POST"])
def log_access():

    data = request.json

    print("LOG MASUK:", data)

    return jsonify({
        "status": "ok"
    })
