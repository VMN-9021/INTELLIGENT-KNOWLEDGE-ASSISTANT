import sqlite3
import os


# Always use students.db from this project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")


def create_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            course TEXT,
            city TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_student(name, age, course, city):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (name, age, course, city)
        VALUES (?, ?, ?, ?)
    """, (name, age, course, city))

    conn.commit()
    conn.close()


def get_student(name):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, age, course, city
        FROM students
        WHERE name = ?
    """, (name,))

    student = cursor.fetchone()

    conn.close()

    return student


if __name__ == "__main__":

    create_database()

    add_student(
        "Vaibhavi",
        22,
        "MCA",
        "Bangalore"
    )

    print(get_student("Vaibhavi"))