import sqlite3

import app
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
from datetime import datetime, timezone

app = Flask(__name__)
# allow routes for cross-origin requests
CORS(app, resources={
    r"/create-reservation": {"origins": "http://localhost:3000"},
    r"/get-reservation-data": {"origins": "http://localhost:3000"},
    r"/update-scooter": {"origins": "http://localhost:3000"}
})


# connect db
def get_db_connection():
    conn = sqlite3.connect('data/database.db')
    conn.row_factory = sqlite3.Row
    return conn


# create a new reservation
@app.route("/create-reservation", methods=["POST"])
def create_reservation():
    data = request.get_json()
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    phone_number = data.get("phoneNumber")
    start_time = data.get("startTime")
    end_time = data.get("endTime")
    location = data.get("location")

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
        "INSERT INTO reservations (first_name, last_name, phone_number, start_time, end_time, location, available) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (first_name, last_name, phone_number, start_time, end_time, location, available)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Reservation created"}), 201


# send available scooters data for front
@app.route("/get-reservation-data", methods=["GET"])
def get_reservation_data():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    current_time = datetime.now(timezone.utc).strftime("YYYY-MM-DDTHH:MM:SSZ")

    # Fetch reservation data from the database with a filter
    cursor.execute(
        "SELECT first_name, last_name, phone_number, location "
        "FROM reservations "
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
        "UPDATE reservations SET available = ? WHERE first_name = ? AND last_name = ?",
        ("no", first_name, last_name)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Scooter availability updated"}), 200


if __name__ == '__main__':
    app.run()
