from flask import Flask, request, session, redirect, flash, render_template
import os
from public.scripts.tools import sanitise, Roster
from handler import DatabaseManager
import json

# Initialise flask application
app = Flask(__name__)

# Initialise database manager
manager = DatabaseManager()

# Test data
example_dentists = [
    {
        "day": "monday",
        "start": 13.75,
        "end": 19.0,
        "id": 2,
    },
    {
        "day": "wednesday",
        "start": 13.75,
        "end": 19.0,
        "id": 2,
    },
    {
        "day": "wednesday",
        "start": 8.5,
        "end": 14.25,
        "id": 1,
    },
]

example_employees = [
    {
        "name": "Scomo",
        "max_hours": 999,
        "max_days": 16,
        "available_days": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ],
        "available_roles": ["receptionist", "runner", "assistant_1", "assistant_2"],
    },
    {
        "name": "Albakneezee",
        "max_hours": 999,
        "max_days": 16,
        "available_days": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ],
        "available_roles": ["receptionist", "runner", "assistant_1", "assistant_2"],
    },
    {
        "name": "Boris Johnson",
        "max_hours": 999,
        "max_days": 16,
        "available_days": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ],
        "available_roles": ["receptionist", "runner", "assistant_1", "assistant_2"],
    },
    {
        "name": "Adil",
        "max_hours": 999,
        "max_days": 16,
        "available_days": [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ],
        "available_roles": ["receptionist", "runner", "assistant_1", "assistant_2"],
    },
]


@app.route("/")
def home():
    # Redirect either to login or to roster tool immediately
    if session.get("logged_in"):
        id = session.get("id")
        # Redirect to login and correct false data (security architecture)
        if id is None or id == 0:
            session["logged_in"] = False
            flash("You were logged in to an invalid account.", "error")
            return redirect("/login")
        return redirect("/tool")
    else:
        return redirect("/login")


@app.route("/login", methods=["POST", "GET"])  # type: ignore
def login():
    # If attempt at login
    if request.method == "POST":
        # Get login data and sanitise (escapes bad inputs)
        username = sanitise(request.form["username"])
        password = sanitise(request.form["password"])
        # Verify data
        if manager.verify_login(username, password):
            session["logged_in"] = True
            session["id"] = manager.user_id(username, password)
            # TODO implement secure session management with permanent sessions and session timeouts
        else:
            flash("Incorrect username or password.", "error")
        # Redirect to home directory
        return redirect("/")
    elif request.method == "GET":
        # Display login page (or redirect if already logged in)
        if not session.get("logged_in"):
            return render_template("login.html")
        else:
            return redirect("/")


@app.route("/signup", methods=["POST", "GET"])  # type: ignore
def sign_up():
    # Render login template
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        # Get account data and sanitise
        username = sanitise(request.form["username"])
        password = sanitise(request.form["password"])
        password_two = sanitise(request.form["confirm_password"])
        # Verify unique username
        if not manager.username_is_unique(username):
            flash("Username is taken.", "error")
            return render_template("signup.html")
        # Verify same password as confirmed password (to avoid accidental typos)
        if not password == password_two:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")
        # Add account to database
        manager.create_account(username, password)
        flash("Account successfully created, feel free to log in.", "message")
        return redirect("/login")


@app.route("/tool", methods=["POST", "GET"])  # type: ignore
def tool():
    if not session.get("logged_in"):
        return redirect("/login")
    # if request.method == "GET":
    #     table = [["No roster created/chosen."]]
    #     return render_template("roster.html", table=table)
    # if request.method == "POST":
    # TODO get the actual inputs from the web page
    if request.method == "POST":
        # If statement determines user action/request
        if request.form["submit"] == "Add dentist":
            # Fetch data
            user_id = session.get("id")
            json_old_dentists = manager.fetch_in_progress_dentists(user_id)  # type: ignore
            # Prevent error from non-existent database entry
            if json_old_dentists is None:
                dental_shifts = []
            else:
                dental_shifts = json.loads(json_old_dentists)
            # Format data from inputs into intended format and sanitise and validate it
            day = sanitise(request.form["day"])
            if (
                day != "monday"
                and day != "tuesday"
                and day != "wednesday"
                and day != "thursday"
                and day != "friday"
                and day != "saturday"
            ):
                flash("Please give day in lowercase text form", "error")
                return redirect("/tool")
            start = sanitise(request.form["start"])
            try:
                test = float(start)  # noqa: F841
            except ValueError:
                flash(
                    "Please enter start and end times in hours, decimal, e.g. 9am-5:45pm is 9.0-17.75"
                )
                return redirect("/tool")
            except TypeError:
                flash(
                    "Please enter start and end times in hours, decimal, e.g. 9am-5:45pm is 9.0-17.75"
                )
                return redirect("/tool")
            end = sanitise(request.form["start"])
            try:
                test = float(end)  # noqa: F841
            except ValueError:
                flash(
                    "Please enter start and end times in hours, decimal, e.g. 9am-5:45pm is 9.0-17.75"
                )
                return redirect("/tool")
            except TypeError:
                flash(
                    "Please enter start and end times in hours, decimal, e.g. 9am-5:45pm is 9.0-17.75"
                )
                return redirect("/tool")
            new_shift = {
                "day": day,
                "start": float(start),
                "end": float(end),
                "id": int(request.form["id"]),
            }
            dental_shifts.append(new_shift)
            json_dentists = json.dumps(dental_shifts)
            # Create new database entry to update if none exists
            if json_old_dentists is None:
                manager.new_in_progress(user_id)  # type: ignore
            # Update in progress database
            manager.update_in_progress_dentists(user_id, json_dentists)  # type: ignore
        elif request.form["submit"] == "Delete last dentist":
            # fetch data
            user_id = session.get("id")
            json_old_dentists = manager.fetch_in_progress_dentists(user_id)  # type: ignore
            # Verify there is something to delete
            if json_old_dentists is not None:
                dental_shifts = json.loads(json_old_dentists)
                if dental_shifts != []:
                    # delete
                    dental_shifts.pop()
                    json_dentists = json.dumps(dental_shifts)
                    manager.update_in_progress_dentists(user_id, json_dentists)  # type: ignore
        elif request.form["submit"] == "Add employee":
            # Fetch data
            user_id = session.get("id")
            json_old_employees = manager.fetch_in_progress_employees(user_id)  # type: ignore
            # Prevent error from non-existent database entry
            if json_old_employees is None:
                employee_list = []
            else:
                employee_list = json.loads(json_old_employees)
            # Format data from inputs into intended format and sanitise and validate it
            name = sanitise(request.form["name"])
            available_days = []
            if request.form.get("available_monday"):
                available_days.append("monday")
            if request.form.get("available_tuesday"):
                available_days.append("tuesday")
            if request.form.get("available_wednesday"):
                available_days.append("wednesday")
            if request.form.get("available_thursday"):
                available_days.append("thursday")
            if request.form.get("available_friday"):
                available_days.append("friday")
            if request.form.get("available_saturday"):
                available_days.append("saturday")
            available_roles = []
            if request.form.get("available_runner"):
                available_roles.append("runner")
            if request.form.get("available_receptionist"):
                available_roles.append("receptionist")
            if not (
                request.form["available_assistants"] is None
                or request.form["available_assistants"] == ""
            ):
                assistant_ids = sanitise(request.form["available_assistants"]).split(
                    ","
                )
                for id in assistant_ids:
                    try:
                        id_int = int(id)
                        if id_int <= 0:
                            raise ValueError()
                    except ValueError:
                        flash(
                            "Please enter the IDs of the dentists for which an employee may act as an assistant. Separate each by commas, no spaces, no extra characters after the final id or before the first. IDs are always positive integers.",
                            "error",
                        )
                        return redirect("/tool")
                    except TypeError:
                        flash(
                            "Please enter the IDs of the dentists for which an employee may act as an assistant. Separate each by commas, no spaces, no extra characters after the final id or before the first. IDs are always positive integers.",
                            "error",
                        )
                        return redirect("/tool")
                    available_roles.append(f"assistant_{id}")
            new_employee = {
                "name": name,
                "max_hours": int(request.form["max_hours"]),
                "max_days": int(request.form["max_days"]),
                "available_days": available_days,
                "available_roles": available_roles,
            }
            employee_list.append(new_employee)
            json_employees = json.dumps(employee_list)
            # Create new database entry to update if none exists
            if json_old_employees is None:
                manager.new_in_progress(user_id)  # type: ignore
            # Update in progress database
            manager.update_in_progress_employees(user_id, json_employees)  # type: ignore
        elif request.form["submit"] == "Delete last employee":
            # fetch data
            user_id = session.get("id")
            json_old_employees = manager.fetch_in_progress_employees(user_id)  # type: ignore
            # Verify there is something to delete
            if json_old_employees is not None:
                employee_list = json.loads(json_old_employees)
                if employee_list != []:
                    # delete
                    employee_list.pop()
                    json_employees = json.dumps(employee_list)
                    manager.update_in_progress_employees(user_id, json_employees)  # type: ignore

    # Render template using test data
    blank_roster = Roster(example_dentists, example_employees)
    # test_table = blank_roster.display_roster([])
    blank_roster.create_roster()
    test_table = blank_roster.display_roster(blank_roster.fetch_roster())
    return render_template("roster.html", table=test_table)


if __name__ == "__main__":
    # Secret key for encryption
    app.secret_key = os.urandom(24)
    # Debug mode, run web server!
    app.run(debug=True)
