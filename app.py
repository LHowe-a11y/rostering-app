from flask import Flask, request, session, redirect, flash, render_template
import os
from public.scripts.tools import sanitise, Roster
from handler import AccountsManager

app = Flask(__name__)

manager = AccountsManager()


@app.route("/")
def home():
    if session.get("logged_in"):
        id = session.get("id")
        if id is None or id == 0:
            session["logged_in"] = False
            flash("You were logged in to an invalid account.", "error")
            return redirect("/login")
        return redirect("/tool")
    else:
        return redirect("/login")


@app.route("/login", methods=["POST", "GET"])  # type: ignore
def login():
    if request.method == "POST":
        username = sanitise(request.form["username"])
        password = sanitise(request.form["password"])
        if manager.verify_login(username, password):
            session["logged_in"] = True
            session["id"] = manager.user_id(username, password)
            # TODO implement secure session management with permanent sessions and session timeouts
        else:
            flash("Incorrect username or password.", "error")
        return redirect("/")
    elif request.method == "GET":
        if not session.get("logged_in"):
            return render_template("login.html")
        else:
            return redirect("/")


@app.route("/signup", methods=["POST", "GET"])  # type: ignore
def sign_up():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = sanitise(request.form["username"])
        password = sanitise(request.form["password"])
        password_two = sanitise(request.form["confirm_password"])
        if not manager.username_is_unique(username):
            flash("Username is taken.", "error")
            return render_template("signup.html")
        if not password == password_two:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")
        manager.create_account(username, password)
        flash("Account successfully created, feel free to log in.", "message")
        return redirect("/login")


@app.route("/tool", methods=["POST", "GET"])  # type: ignore
def tool():
    # if not session.get("logged_in"):
    #     return redirect("/login")
    # if request.method == "GET":
    #     table = [["No roster created/chosen."]]
    #     return render_template("roster.html", table=table)
    # if request.method == "POST":
    # TODO get the actual inputs from the web page
    blank_roster = Roster([], [])
    test_table = blank_roster.display_roster([])
    return render_template("roster.html", table=test_table)


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
