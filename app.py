import sqlite3

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)

CORS(app, resources={
    r"/add-scooter": {"origins": "http://localhost:3000"},
    r"/add-reservation": {"origins": "http://localhost:3000"},
    r"/available-scooters": {"origins": "http://localhost:3000"},
    r"/update-scooter": {"origins": "http://localhost:3000"},
})


# connect db
def get_db_connection():
    conn = sqlite3.connect('data/database.db')
    conn.row_factory = sqlite3.Row
    return conn


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

    start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")

    # Check if start_time is after the current time
    current_time = datetime.now()
    if start_time > current_time:
        available = "yes"
    else:
        available = "no"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO scooters (first_name, last_name, phone_number, start_time, end_time, location, price_per_hour, available) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (first_name, last_name, phone_number, start_time, end_time, location, price, available)
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

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO reservations (owner_first_name, owner_last_name, client_first_name, client_last_name, "
        "phone_number, location, start_date, stop_date)"
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (owner_first_name, owner_last_name, client_first_name, client_last_name, phone_number, location, start_time,
         end_time)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation created"}), 201


# send available scooters data for front
@app.route("/available-scooters", methods=["GET"])
def get_reservation_data():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    current_time = datetime.now(timezone.utc).strftime("YYYY-MM-DDTHH:MM:SSZ")

    # Fetch reservation data from the database with a filter
    cursor.execute(
        "SELECT first_name, last_name, phone_number, location, price_per_hour "
        "FROM scooters "
        "WHERE end_time <= ? AND available = 'yes'", (current_time,)
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
    print(reservation_list)
    return jsonify(reservation_list)


# make a scooter unavailable when taken
@app.route("/update-scooter", methods=["POST"])
def update_scooter_availability():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE scooters SET available = ? WHERE first_name = ? AND last_name = ?",
        ("no", first_name, last_name)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Scooter availability updated"}), 200


if __name__ == '__main__':
    app.run()
