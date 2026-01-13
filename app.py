from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "/tmp/database.db"

# --------------------
# Initialize / Repair Database
# --------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        enroll TEXT,
        name TEXT,
        total_classes INTEGER,
        attended INTEGER
    )
    """)

    # FORCE admin user (idempotent)
    cur.execute("""
    INSERT OR REPLACE INTO admin (username, password)
    VALUES ('admin', 'admin')
    """)

    conn.commit()
    conn.close()

# --------------------
# Database connection
# --------------------
def get_db():
    return sqlite3.connect(DB_PATH)

# --------------------
# Login
# --------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )
        admin = cur.fetchone()
        db.close()

        if admin:
            return redirect("/dashboard")

    return render_template("login.html")

# --------------------
# Dashboard
# --------------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# --------------------
# Add Student
# --------------------
@app.route("/add_student", methods=["POST"])
def add_student():
    enroll = request.form["enroll"]
    name = request.form["name"]
    total = int(request.form["total"])
    attended = int(request.form["attended"])

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO attendance VALUES (?,?,?,?)",
        (enroll, name, total, attended)
    )
    db.commit()
    db.close()

    return redirect("/dashboard")

# --------------------
# Search Student
# --------------------
@app.route("/student", methods=["POST"])
def student():
    enroll = request.form["enroll"]

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM attendance WHERE enroll=?",
        (enroll,)
    )
    student = cur.fetchone()
    db.close()

    return render_template("student.html", student=student)

# --------------------
# App Start
# --------------------
init_db()

if __name__ == "__main__":
    app.run()
