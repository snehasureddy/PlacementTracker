# Import SQLite3, a built-in Python module for working with SQLite databases.
import sqlite3


# Connect to placements.db. If the file does not exist, SQLite creates it.
connection = sqlite3.connect("placements.db")

# Create a cursor to execute SQL commands.
cursor = connection.cursor()

# Create the applications table only if it does not already exist.
cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    job_role TEXT NOT NULL,
    application_date TEXT,
    status TEXT
)
""")

# Save the table creation in the database.
connection.commit()

# Close the database connection.
connection.close()

print("Success: placements.db and the applications table are ready.")
