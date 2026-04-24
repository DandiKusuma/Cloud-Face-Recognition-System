from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask import render_template_string

app = Flask(__name__)

doors = {
    "door1": {"username": "admin1", "password": "1234", "unlock": False},
    "door2": {"username": "admin2", "password": "5678", "unlock": False},
    "door3": {"username": "admin3", "password": "9999", "unlock": False},
}

def init_db():
    conn = sqlite3.connect("access_log.db")
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            door_id TEXT,
            name TEXT,
            card_uid TEXT,
            method TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

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
    return jsonify({
        "result": "FACE_OK",
        "name": "Dandi"
    })

@app.route("/log_access", methods=["POST"])
def log_access():
    data = request.json

    conn = sqlite3.connect("access_log.db")
    c = conn.cursor()

    c.execute('''
        INSERT INTO logs (door_id, name, card_uid, method, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get("door_id"),
        data.get("name"),
        data.get("card_uid"),
        data.get("method"),
        data.get("status"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})
    return jsonify({"status": "success"})

@app.route("/logs", methods=["GET"])
def get_logs():
    conn = sqlite3.connect("access_log.db")
    c = conn.cursor()

    c.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "door_id": row[1],
            "name": row[2],
            "card_uid": row[3],
            "method": row[4],
            "status": row[5],
            "timestamp": row[6]
        })

    return jsonify(data)

@app.route("/riwayat")
def dashboard():
    conn = sqlite3.connect("access_log.db")
    c = conn.cursor()

    c.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()

    html = """
    <html>
    <head>
        <title>Access Log Dashboard</title>
        <style>
            body { font-family: Arial; background: #111; color: #fff; }
            table { border-collapse: collapse; width: 100%; }
            th, td { padding: 10px; border: 1px solid #444; text-align: center; }
            th { background: #222; }
            tr:nth-child(even) { background: #1a1a1a; }
            h1 { text-align: center; }
        </style>
    </head>
    <body>
        <h1>DOOR ACCESS LOG</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Door</th>
                <th>Name</th>
                <th>UID</th>
                <th>Method</th>
                <th>Status</th>
                <th>Time</th>
            </tr>
    """

    for row in rows:
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
            <td>{row[5]}</td>
            <td>{row[6]}</td>
        </tr>
        """

    html += "</table></body></html>"

    return html
