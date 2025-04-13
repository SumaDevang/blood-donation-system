import sqlite3


def init_db():
    # Connect to (or create) the database file
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Drop existing tables to avoid conflicts
    cursor.executescript('''
        DROP TABLE IF EXISTS BloodRequests;
        DROP TABLE IF EXISTS DonationEligibility;
        DROP TABLE IF EXISTS Donations;
        DROP TABLE IF EXISTS Hospitals;
        DROP TABLE IF EXISTS Donors;
    ''')

    # Execute create.sql to create tables
    with open('sql/create.sql', 'r') as f:
        cursor.executescript(f.read())

    # Execute insert.sql to populate tables with data
    with open('sql/insert.sql', 'r') as f:
        cursor.executescript(f.read())

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database initialized successfully as database.db")


if __name__ == "__main__":
    init_db()