from flask import Flask, request, session, redirect, flash, render_template
import os

app = Flask(__name__)


@app.route("/")
def home():
    if session.get("logged_in"):
        name = session.get("username")
        return "Logged in, %s" % name
    else:
        return redirect("/login")


@app.route("/login", methods=["POST", "GET"])  # type: ignore
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # TODO make a real sign up page and real logins with input sanitisation
        if username == "admin" and password == "123456":
            session["logged_in"] = True
            session["username"] = username
            # TODO implement secure session management with secret key? permanent sessins and session timeouts
        else:
            flash("Incorrect username or password.", "error")
        return redirect("/")
    elif request.method == "GET":
        if not session.get("logged_in"):
            return render_template("login.html")
        else:
            return redirect("/")


@app.route("/signup", methods=["POST", "GET"])
def sign_up():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form("username")
        password = request.form("password")
        password_two = request.form("confirm_password")
        # TODO Things are sanitised
        if username != "unique":
            flash("Username taken", "error")
            return render_template("signup.html")
        if not password == password_two:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        # TODO add account to database
        flash("Account successfully created, feel free to log in", "message")
        return redirect("/login")


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
