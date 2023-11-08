import sqlite3


# Create scooters table
def create_scooters():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scooters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            location TEXT NOT NULL,
            price_per_hour REAL NOT NULL,
            available TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Create the "reservations" table
def create_reservations():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_first_name TEXT NOT NULL,
            owner_last_name TEXT NOT NULL,
            client_first_name TEXT NOT NULL,
            client_last_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            location TEXT NOT NULL,
            start_date DATETIME NOT NULL,
            stop_date DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Create the "scooter_busy_times" table
def create_scooter_busy_times():
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scooter_busy_times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            owner_fn TEXT NOT NULL,
            owner_ln TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Create the tables
create_scooters()
create_reservations()
create_scooter_busy_times()
