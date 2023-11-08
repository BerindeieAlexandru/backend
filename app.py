import sqlite3

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone, timedelta

# from flask_ngrok import run_with_ngrok

app = Flask(__name__)

# enable CORS for all routes
CORS(app, resources={
    r"/add-scooter": {"origins": "http://localhost:3000"},
    r"/add-reservation": {"origins": "http://localhost:3000"},
    r"/available-scooters": {"origins": "http://localhost:3000"},
    r"/update-scooter": {"origins": "http://localhost:3000"},
})


# only when running with ngrok
# run_with_ngrok(app)  # Start ngrok when app is run

# connect db
def get_db_connection():
    conn = sqlite3.connect('data/database.db')
    conn.row_factory = sqlite3.Row
    return conn


# basic route
@app.route("/", methods=["GET"])
def empty():
    return jsonify({"message": "Hello World!"}), 200


# create a new reservation
@app.route("/add-scooter", methods=["POST"])
def create_reservation():
    data = request.get_json()
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    phone_number = data.get("phoneNumber")
    start_time = data.get("startTime")
    end_time = data.get("endTime")
    location = data.get("location")
    price = data.get("price")

    start_time1 = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
    end_time1 = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

    # Check if start_time is after the current time
    current_time = datetime.now()
    if start_time1 > current_time:
        available = "yes"
    else:
        available = "no"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO scooters (first_name, last_name, phone_number, start_time, end_time, location, price_per_hour, "
        "available)"
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (first_name, last_name, phone_number, start_time1, end_time1, location, price, available)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation created"}), 201


# create a new reservation
@app.route("/add-reservation", methods=["POST"])
def add_reservation():
    data = request.get_json()
    owner_first_name = data.get("owner_first_name")
    owner_last_name = data.get("owner_last_name")
    client_first_name = data.get("firstName")
    client_last_name = data.get("lastName")
    phone_number = data.get("phoneNumber")
    start_time = data.get("startTime")
    end_time = data.get("endTime")
    location = data.get("location")

    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reservations (owner_first_name, owner_last_name, client_first_name, client_last_name, "
        "phone_number, location, start_date, stop_date) "
        "SELECT ?, ?, ?, ?, ?, ?, ?, ? "
        "WHERE EXISTS ("
        "   SELECT 1 "
        "   FROM scooters s "
        "   LEFT JOIN scooter_busy_times sbt ON s.first_name = sbt.owner_fn AND s.last_name = sbt.owner_ln "
        "   LEFT JOIN reservations r ON s.first_name = r.owner_first_name AND s.last_name = r.owner_last_name "
        "   WHERE s.first_name = ? AND s.last_name = ? "
        "   AND s.start_time <= ? AND s.end_time >= ? "
        "   AND ? > ? "
        "   AND ( ( ? < sbt.start_time AND ? < sbt.start_time) "
        "   OR ( ? > sbt.end_time AND ? > sbt.end_time) OR sbt.start_time IS NULL )"
        "   AND ( ( ? < r.start_date AND ? < r.start_date) "
        "   OR ( ? > r.stop_date AND ? > r.stop_date) OR r.start_date IS NULL )"
        ")",
        (
            owner_first_name, owner_last_name, client_first_name, client_last_name,
            phone_number, location, start_time, end_time,
            owner_first_name, owner_last_name, start_time, end_time, end_time, start_time, start_time, end_time,
            start_time, end_time, start_time, end_time, start_time, end_time)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation created"}), 201


# send available scooters data for front
@app.route("/available-scooters", methods=["GET"])
def get_reservation_data():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        "SELECT first_name, last_name, phone_number, location, price_per_hour "
        "FROM scooters "
        "WHERE start_time >= ? AND end_time >= ? ",
        (
            current_time, current_time
        )
    )

    reservation_data = cursor.fetchall()

    conn.close()

    reservation_list = [
        {
            "first_name": row[0],
            "last_name": row[1],
            "phone_number": row[2],
            "location": row[3],
            "price_per_hour": row[4]
        }
        for row in reservation_data
    ]
    print(reservation_data)
    return jsonify(reservation_list)


# make a scooter unavailable when taken
@app.route("/update-scooter", methods=["POST"])
def update_scooter_availability():
    data = request.get_json()
    ofirst_name = data.get("owner_first_name")
    olast_name = data.get("owner_last_name")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
    end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO scooter_busy_times (first_name, last_name, start_time, end_time, owner_fn, owner_ln)"
                   "SELECT ?, ?, ?, ?, ?, ? "
                   "WHERE EXISTS ("
                   "   SELECT 1 "
                   "   FROM scooters s "
                   "LEFT JOIN reservations r ON s.first_name = r.owner_first_name AND s.last_name = r.owner_last_name"
                   "   LEFT JOIN scooter_busy_times sbt ON s.first_name = sbt.owner_fn AND s.last_name = sbt.owner_ln "
                   "   WHERE s.first_name = ? AND s.last_name = ? "
                   "   AND s.start_time <= ? AND s.end_time >= ? "
                   "   AND ? > ? "
                   "   AND ( ( ? < r.start_date AND ? < r.start_date) "
                   "   OR ( ? > r.stop_date AND ? > r.stop_date) OR r.start_date IS NULL )"
                   "   AND ( ( ? < sbt.start_time AND ? < sbt.start_time) "
                   "   OR ( ? > sbt.end_time AND ? > sbt.end_time) OR sbt.start_time IS NULL OR sbt.end_time IS NULL)"
                   ")",
                   (first_name, last_name, start_time, end_time, ofirst_name, olast_name, first_name, last_name,
                    start_time, end_time, end_time, start_time, start_time, end_time, start_time, end_time, start_time,
                    end_time, start_time, end_time)
                   )

    conn.commit()
    conn.close()

    return jsonify({"message": "Scooter availability updated"}), 200


if __name__ == '__main__':
    app.run()
