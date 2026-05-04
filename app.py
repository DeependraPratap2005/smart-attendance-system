from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

# 🔐 Login Route (GET + POST)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Simple login (change as needed)
        if username == "admin" and password == "1234":
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Credentials"

    return render_template("login.html")


# 📝 Register Student
@app.route("/register")
def register():
    subprocess.run(["python", "register_student.py"])
    return "Student Registered!"


# 📸 Create Dataset
@app.route("/dataset")
def dataset():
    subprocess.run(["python", "dataset_creator.py"])
    return "Dataset Created!"


# 🧠 Train Model
@app.route("/train")
def train():
    subprocess.run(["python", "train_model.py"])
    return "Model Trained!"


# 🎥 Recognize Face / Attendance
@app.route("/recognize")
def recognize():
    subprocess.run(["python", "recognize.py"])
    return "Attendance Started!"


# 📊 Dashboard Page
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ▶ Run App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
