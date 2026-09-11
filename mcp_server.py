from mcp.server.fastmcp import FastMCP
import sqlite3
import os
import sys


mcp = FastMCP("Student Database")


# Get the folder where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use the same database
DB_PATH = os.path.join(BASE_DIR, "students.db")


@mcp.tool()
def get_student(name: str):
    """
    Search the student database by name.

    Available information:
    - Name
    - Age
    - Course
    - City
    """

    # Debug messages must go to stderr
    print(
        f"MCP searching for: {name}",
        file=sys.stderr,
        flush=True
    )

    print(
        f"Database path: {DB_PATH}",
        file=sys.stderr,
        flush=True
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, age, course, city
        FROM students
        WHERE LOWER(name) = LOWER(?)
    """, (name.strip(),))

    student = cursor.fetchone()

    conn.close()

    if student is None:
        return f"No student found with the name '{name}'."

    return (
        f"Name: {student[0]}\n"
        f"Age: {student[1]}\n"
        f"Course: {student[2]}\n"
        f"City: {student[3]}"
    )

@mcp.tool()
def add_student(name: str, age: int, course: str, city: str):
    """
    Add a new student to the database student.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (name, age, course, city)
        VALUES (?, ?, ?, ?)
    """, (name, age, course, city))

    conn.commit()
    conn.close()

    return f"Student {name} was added successfully."


if __name__ == "__main__":
    mcp.run()