from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form data safely
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()

        # 🔍 DEBUG (Render logs me dikhega)
        print("DEBUG:", username, password, role)

        # 🛑 Check empty fields
        if not username or not password or not role:
            return render_template("login.html", error="All fields are required")

        # ✅ Admin Login
        if role == "admin" and username == "admin" and password == "1234":
            return redirect(url_for("dashboard"))

        # ✅ Student Login
        elif role == "student" and username == password:
            return "Student Login Successful"

        # ❌ Invalid
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# 🔥 Important for Render (PORT use karo)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
