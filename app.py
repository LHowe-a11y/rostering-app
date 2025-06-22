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
        if request.form["submit"] == "Logout button":
            session["logged_in"] = False
            session["id"] = 0
            return redirect("/login")
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
                flash(
                    "Please give day in lowercase text form. Must have a day, monday-saturday.",
                    "error",
                )
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
            end = sanitise(request.form["end"])
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
            if request.form["id"] is None or request.form["id"] == "":
                flash(
                    "Please give an ID for which dentist performs the shift.", "error"
                )
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
            if name is None or name == "":
                flash("Employee must have name", "error")
                return redirect("/tool")
            if request.form["max_days"] is None or request.form["max_days"] == "":
                max_days = 6
            else:
                max_days = request.form["max_days"]
            if request.form["max_hours"] is None or request.form["max_hours"] == "":
                max_hours = 38
            else:
                max_hours = request.form["max_hours"]
            new_employee = {
                "name": name,
                "max_hours": int(max_hours),
                "max_days": int(max_days),
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
        elif request.form["submit"] == "Delete specific employee":
            user_id = session.get("id")
            json_old_employees = manager.fetch_in_progress_employees(user_id)  # type: ignore
            employee_name = sanitise(request.form["employee_name"])
            # Verify there is something to delete
            if json_old_employees is not None:
                employee_list = json.loads(json_old_employees)
                employee_list_enum = enumerate(employee_list)
                for employee in employee_list_enum:
                    if employee[1]["name"] == employee_name:
                        employee_list.pop(employee[0])
                json_employees = json.dumps(employee_list)
                manager.update_in_progress_employees(user_id, json_employees)  # type: ignore

    # # Render template using test data
    # blank_roster = Roster(example_dentists, example_employees)
    # # test_table = blank_roster.display_roster([])
    # blank_roster.create_roster()
    # test_table = blank_roster.display_roster(blank_roster.fetch_roster())
    # return render_template("roster.html", table=test_table)

    # Render the in progress roster creation (or a blank if nothing is in progress)
    user_id = session.get("id")
    json_dentists = manager.fetch_in_progress_dentists(user_id)  # type: ignore
    json_employees = manager.fetch_in_progress_employees(user_id)  # type: ignore
    # Check there is an in progress thing
    if json_dentists is not None and json_employees is not None:
        dentists = json.loads(json_dentists)
        employees = json.loads(json_employees)
        if dentists != [] and employees != [] and len(employees) > 1:
            display_roster = Roster(dentists, employees)
            if display_roster.dentists.too_many_dentists:
                flash(
                    "More than 2 dentists have been scheduled on one day, this exceeds the expectations and boundaries of the program.",
                    "error",
                )
                table = [["No roster to display."]]
                return render_template("roster.html", table=table)
            if request.method == "GET" and len(request.form.getlist("submit")) > 0:
                timeout = request.form["timeout"]
                iterations = request.form["iterations"]
                if timeout is None:
                    timeout = 3
                if iterations is None:
                    iterations = 10
                display_roster.create_roster(int(timeout), int(iterations))
            else:
                display_roster.create_roster()
            if display_roster.failed:
                flash(
                    "The program timed out, and could not find any possible roster configurations. You might be able to change some settings to get a different outcome, but consider re-arranging your schedule.",
                    "error",
                )
                table = [["No roster to display."]]
                return render_template("roster.html", table=table)
            elif display_roster.timed_out:
                flash(
                    "The program found possible solutions, but less than the preferred minimum. This result may not be ideal.",
                    "warning",
                )
            table = display_roster.display_roster(display_roster.fetch_roster())
            return render_template("roster.html", table=table)
    flash(
        "You need at least one dentist shift and two employees to generate a roster, which you do not currently have."
    )
    table = [["No roster to display."]]
    return render_template("roster.html", table=table)


@app.route("/employees", methods=["POST", "GET"])
def employees():
    if not session.get("logged_in"):
        return redirect("/login")
    if request.method == "POST":
        if request.form["submit"] == "Add employee":
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
                        return redirect("/employees")
                    except TypeError:
                        flash(
                            "Please enter the IDs of the dentists for which an employee may act as an assistant. Separate each by commas, no spaces, no extra characters after the final id or before the first. IDs are always positive integers.",
                            "error",
                        )
                        return redirect("/employees")
                    available_roles.append(f"assistant_{id}")
            if name is None or name == "":
                flash("Employee must have name", "error")
                return redirect("/employees")
            if request.form["max_days"] is None or request.form["max_days"] == "":
                max_days = 6
            else:
                max_days = request.form["max_days"]
            if request.form["max_hours"] is None or request.form["max_hours"] == "":
                max_hours = 38
            else:
                max_hours = request.form["max_hours"]
            new_employee = {
                "name": name,
                "max_hours": int(max_hours),
                "max_days": int(max_days),
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
        elif request.form["submit"] == "Delete specific employee":
            user_id = session.get("id")
            json_old_employees = manager.fetch_in_progress_employees(user_id)  # type: ignore
            employee_name = sanitise(request.form["employee_name"])
            # Verify there is something to delete
            if json_old_employees is not None:
                employee_list = json.loads(json_old_employees)
                employee_list_enum = enumerate(employee_list)
                for employee in employee_list_enum:
                    if employee[1]["name"] == employee_name:
                        employee_list.pop(employee[0])
                json_employees = json.dumps(employee_list)
                manager.update_in_progress_employees(user_id, json_employees)  # type: ignore

    user_id = session.get("id")
    json_employees = manager.fetch_in_progress_employees(user_id)  # type: ignore
    if json_employees is not None:
        employees = json.loads(json_employees)
    else:
        employees = []

    table = []
    for employee in employees:
        row = []
        row.append(str(employee["name"] + "    "))
        row.append(str(employee["max_hours"]))
        row.append(str(employee["max_days"]))
        string = ""
        i = 0
        for day in employee["available_days"]:
            if i >= 1:
                string += ", "
            string += day
            i += 1
        string += "  "
        row.append(string)
        string = ""
        i = 0
        for role in employee["available_roles"]:
            if i >= 1:
                string += ", "
            string += role
            i += 1
        string += "  "
        row.append(string)
        table.append(row)

    return render_template("employees.html", table=table)


@app.route("/save", methods=["POST", "GET"])  # type: ignore
def save_roster():
    if not session.get("logged_in"):
        return redirect("/login")
    if request.method == "GET":
        return redirect("/")
    if request.form["submit"] == "Save roster":
        # Get roster info
        user_id = session.get("id")
        dentists = manager.fetch_in_progress_dentists(user_id)  # type: ignore
        employees = manager.fetch_in_progress_employees(user_id)  # type: ignore
        if (dentists is None or len(json.loads(dentists)) == 0) and (
            employees is None or len(json.loads(employees)) == 0
        ):
            flash(
                "You are trying to save a roster with no data. An incomplete roster may be saved, but not one with no data.",
                "error",
            )
        else:
            if dentists is None:
                dentists = json.dumps([])
            if employees is None:
                employees = json.dumps([])
        roster_name = request.form["name"]
        if roster_name is None:
            flash("To save a roster you must name it.", "error")
            return redirect("/tool")
        else:
            roster_name = sanitise(roster_name)
        manager.save_roster(user_id, dentists, employees, roster_name)  # type: ignore
        flash("Successfully saved this roster!", "message")
        flash("You can find your saved rosters by opening the menu.", "info")
        return redirect("/tool")
    elif request.form["submit"] == "Delete roster":
        if request.form.get("confirm_delete"):
            manager.delete_roster(int(request.form["roster_id"]))
        return redirect("/library")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/library")
def library():
    if not session.get("logged_in"):
        return redirect("/login")
    user_id = session.get("id")
    return render_template(
        "library.html",
        rosters=manager.retrieve_saved_rosters(user_id),  # type: ignore
        username=manager.fetch_username(user_id),  # type: ignore
    )


@app.route("/load", methods=["POST"])
def load_roster():
    if not session.get("logged_in"):
        return redirect("/login")
    user_id = session.get("id")
    username = request.form["username"]
    if manager.fetch_username(user_id) != username:  # type: ignore
        flash("You are trying to load a roster that does not belong to you.", "error")
        return redirect("/tool")
    roster_id = int(request.form["roster_id"])
    roster = manager.fetch_saved_roster(roster_id)
    if roster[0] != user_id:
        flash("You are trying to load a roster that does not belong to you.", "error")
        return redirect("/tool")
    dentists = roster[1]
    employees = roster[2]
    manager.update_in_progress_dentists(user_id, dentists)  # type: ignore
    manager.update_in_progress_employees(user_id, employees)  # type: ignore
    return redirect("/tool")


@app.route("/deletemyaccount", methods=["POST"])
def delete_account():
    if not session.get("logged_in"):
        return redirect("/login")
    if request.form.get("confirm_delete"):
        username = sanitise(request.form["username"])
        password = sanitise(request.form["password"])
        if manager.verify_login(username, password):
            user_id = manager.user_id(username, password)
            if user_id == session.get("id"):
                manager.delete_account(user_id)
                session["logged_in"] = False
                session["id"] = 0
                flash("Account deleted.", "info")
                return redirect("/login")
    session["logged_in"] = False
    session["id"] = 0
    flash("Failed to delete account due to incorrect details.", "error")
    return redirect("/login")


if __name__ == "__main__":
    # Secret key for encryption
    app.secret_key = os.urandom(24)
    # Debug mode, run web server!
    app.run(debug=True)
