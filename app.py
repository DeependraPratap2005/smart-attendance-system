from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        # Admin Login
        if role == "admin" and username == "admin" and password == "1234":
            return redirect(url_for("dashboard"))

        # Student Login (simple logic)
        elif role == "student" and username == password:
            return "Student Login Successful"

        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
