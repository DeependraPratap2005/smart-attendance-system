from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import sqlite3
import subprocess
import os
import shutil
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secret123"


# =====================================================
# DATABASE
# =====================================================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        uid TEXT UNIQUE,
        course TEXT,
        parent_email TEXT,
        parent_phone TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    """)

    c.execute("SELECT * FROM admin WHERE email=?", ("admin@gmail.com",))
    if not c.fetchone():
        c.execute("INSERT INTO admin(email,password) VALUES(?,?)",
                  ("admin@gmail.com", "1234"))

    conn.commit()
    conn.close()


init_db()


# =====================================================
# HELPERS
# =====================================================
def get_df():
    file = "attendance/attendance.csv"

    if os.path.exists(file):
        return pd.read_csv(file)

    return pd.DataFrame(columns=[
        "Name", "Date", "Time",
        "Subject", "Faculty",
        "Slot", "Status"
    ])


def filter_report(df, mode):
    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    today = datetime.now().date()

    if mode == "today":
        return df[df["Date"].dt.date == today]

    elif mode == "weekly":
        start = today - timedelta(days=7)
        return df[df["Date"].dt.date >= start]

    elif mode == "monthly":
        return df[
            (df["Date"].dt.month == today.month) &
            (df["Date"].dt.year == today.year)
        ]

    elif mode == "yearly":
        return df[df["Date"].dt.year == today.year]

    return df


# =====================================================
# LOGIN
# =====================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        role = request.form["role"]
        user = request.form["user"].strip()
        password = request.form["pass"].strip()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        if role == "admin":
            c.execute("SELECT * FROM admin WHERE email=? AND password=?",
                      (user, password))

            if c.fetchone():
                session["admin"] = user
                conn.close()
                return redirect("/admin")

        elif role == "student":
            c.execute("SELECT * FROM students WHERE uid=?", (user,))
            student = c.fetchone()

            if student:
                uid = student[2].strip().lower()

                if uid == password.lower():
                    session["student"] = student[1].strip()
                    session["uid"] = student[2].strip()

                    conn.close()
                    return redirect("/student")

        conn.close()
        return render_template("login.html", error="Login Failed")

    return render_template("login.html")


# =====================================================
# ADMIN PANEL (FIXED)
# =====================================================
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/")

    mode = request.args.get("mode", "today")

    conn = sqlite3.connect("database.db")
    students_raw = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    students = []

    for s in students_raw:
        uid = s[2]
        has_face = os.path.exists(f"dataset/{uid}")

        students.append({
            "id": s[0],
            "name": s[1],
            "uid": s[2],
            "course": s[3],
            "has_face": has_face
        })

    total_students = len(students)

    df = get_df()
    df = filter_report(df, mode)

    present = len(df[df["Status"] == "Present"])
    absent = len(df[df["Status"] == "Absent"])

    return render_template(
        "dashboard.html",
        students=students,
        total_students=total_students,
        present=present,
        absent=absent,
        mode=mode
    )


# =====================================================
# ADD STUDENT
# =====================================================
@app.route("/add", methods=["POST"])
def add():
    if "admin" not in session:
        return redirect("/")

    d = request.form

    conn = sqlite3.connect("database.db")

    try:
        conn.execute("""
        INSERT INTO students(name,uid,course,parent_email,parent_phone)
        VALUES(?,?,?,?,?)
        """, (
            d["name"].strip(),
            d["uid"].strip(),
            d["course"].strip(),
            d["email"].strip(),
            d["phone"].strip()
        ))
        conn.commit()
    except:
        pass

    conn.close()
    return redirect("/admin")


# =====================================================
# DELETE
# =====================================================
@app.route("/delete/<int:id>")
def delete(id):
    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()

    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    if student:
        uid = student[2].strip()
        folder = os.path.join("dataset", uid)

        if os.path.exists(folder):
            shutil.rmtree(folder)

    return redirect("/admin")


# =====================================================
# FACE FUNCTIONS (FIXED DUPLICATE ISSUE)
# =====================================================
@app.route("/add_face/<uid>")
def add_face(uid):
    subprocess.Popen(["python", "capture_faces.py", uid])
    subprocess.Popen(["python", "train_model.py"])
    return redirect("/admin")


@app.route("/remove_face/<uid>")
def remove_face(uid):
    path = f"dataset/{uid}"

    if os.path.exists(path):
        shutil.rmtree(path)

    subprocess.Popen(["python", "train_model.py"])
    return redirect("/admin")


# =====================================================
# EDIT
# =====================================================
@app.route("/edit/<int:id>")
def edit(id):
    if "admin" not in session:
        return redirect("/")

    conn = sqlite3.connect("database.db")
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit.html", student=student)


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "admin" not in session:
        return redirect("/")

    d = request.form

    conn = sqlite3.connect("database.db")

    conn.execute("""
    UPDATE students
    SET name=?,uid=?,course=?,parent_email=?,parent_phone=?
    WHERE id=?
    """, (
        d["name"].strip(),
        d["uid"].strip(),
        d["course"].strip(),
        d["email"].strip(),
        d["phone"].strip(),
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/admin")


# =====================================================
# REPORT
# =====================================================
@app.route("/student_report/<int:id>")
def student_report(id):
    if "admin" not in session:
        return redirect("/")

    mode = request.args.get("mode", "today")

    conn = sqlite3.connect("database.db")
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()

    if not student:
        return redirect("/admin")

    name = student[1].strip()

    df = get_df()
    df = df[df["Name"].str.strip() == name]
    df = filter_report(df, mode)

    records = df.to_dict(orient="records")

    return render_template(
        "report.html",
        name=name,
        total=len(df),
        present=len(df[df["Status"] == "Present"]),
        absent=len(df[df["Status"] == "Absent"]),
        records=records,
        mode=mode
    )


# =====================================================
# START / STOP ATTENDANCE
# =====================================================
@app.route("/start_attendance", methods=["POST"])
def start_attendance():
    if "admin" not in session:
        return redirect("/")

    subject = request.form["subject"]
    faculty = request.form["faculty"]
    slot = request.form["time_slot"]
    date = request.form["date"]

    with open("current_session.txt", "w") as f:
        f.write(f"{subject}|{faculty}|{slot}|{date}")

    with open("attendance_status.txt", "w") as f:
        f.write("ON")

    return redirect("/admin")


@app.route("/stop")
def stop():
    with open("attendance_status.txt", "w") as f:
        f.write("OFF")

    return redirect("/admin")


@app.route("/status")
def status():
    try:
        with open("attendance_status.txt") as f:
            return jsonify({"status": f.read().strip()})
    except:
        return jsonify({"status": "OFF"})


# =====================================================
# EXPORT
# =====================================================
@app.route("/export")
def export():
    return send_file("attendance/attendance.csv", as_attachment=True)


# =====================================================
# STUDENT PANEL
# =====================================================
@app.route("/student")
def student():
    if "student" not in session:
        return redirect("/")

    name = session["student"]

    df = get_df()
    student_df = df[df["Name"].str.strip() == name]

    total = len(student_df)
    present = len(student_df[student_df["Status"] == "Present"])
    absent = len(student_df[student_df["Status"] == "Absent"])

    percent = round((present / total) * 100, 2) if total > 0 else 0

    return render_template(
        "student.html",
        name=name,
        total=total,
        present=present,
        absent=absent,
        percent=percent,
        records=student_df.to_dict(orient="records")
    )


# =====================================================
# FACE START
# =====================================================
@app.route("/start_face")
def start_face():
    subprocess.Popen(["python", "recognize.py"])
    return "<h2>Face Recognition Started</h2>"


# =====================================================
# LOGOUT
# =====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)