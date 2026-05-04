from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register")
def register():
    os.system("python register_student.py")
    return "Student Registered!"

@app.route("/dataset")
def dataset():
    os.system("python dataset_creator.py")
    return "Dataset Created!"

@app.route("/train")
def train():
    os.system("python train_model.py")
    return "Model Trained!"

@app.route("/recognize")
def recognize():
    os.system("python recognize.py")
    return "Attendance Started!"

@app.route("/dashboard")
def dashboard():
    os.system("python dashboard.py")
    return "Dashboard Opened!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
