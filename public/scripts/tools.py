# from decimal import Decimal
# from statistics import variance
import html
import bcrypt


def sanitise(input: str) -> str:
    return html.escape(input, True)


def hash(input: str) -> bytes:
    bytestring = input.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytestring, salt)
    return hash


def check_hash(input: str, hash: bytes) -> bool:
    bytestring = input.encode("utf-8")
    return bcrypt.checkpw(bytestring, hash)


class DentistSchedule:
    def __init__(self, shifts: list) -> None:
        # raw_shifts = shifts
        self.monday: list
        self.tuesday: list
        self.wednesday: list
        self.thursday: list
        self.friday: list
        self.saturday: list

        """This section sorts and formats each shift for easier processing"""

        # # Sort the shifts chronologically
        # raw_shifts.sort()
        # # Split each shift into its own list of parts
        # self.shifts = list(map(lambda x: x.split(":"), raw_shifts))

        # Shifts are in the form Day:Start:End:Dentist e.g. 1:0830:1300:2 would mean Monday, 8:30 am to 1:00 pm, Dentist 2.
        # TODO change shifts into form {"day": "monday", "start": 13.75, "end": 29.25, "id": 2}

        for shift in shifts:  # For each shift in the total list of shifts
            # Turn each part of the shift into an integer to allow mathematics
            # Add the shift to a sub-list of shifts per-day
            match shift["day"]:
                case "monday":
                    self.monday.append(shift)

                case "tuesday":
                    self.tuesday.append(shift)

                case "wednesday":
                    self.wednesday.append(shift)

                case "thursday":
                    self.thursday.append(shift)

                case "friday":
                    self.friday.append(shift)

                case "saturday":
                    self.saturday.append(shift)

                # Error catching
                case _:
                    raise TypeError(
                        "A shift day is not a string monday-saturday",
                        shift,
                    )

        if (
            len(self.monday) > 2
            or len(self.tuesday) > 2
            or len(self.wednesday) > 2
            or len(self.thursday) > 2
            or len(self.friday) > 2
            or len(self.saturday) > 2
        ):
            raise SyntaxError(
                "More than two dentists shifted in one day, this exceeds the minimum requirements and is not included in program!"
            )

    def int_to_day_list(self, integer: int) -> list:
        match integer:
            case 1:
                return self.monday
            case 2:
                return self.tuesday
            case 3:
                return self.wednesday
            case 4:
                return self.thursday
            case 5:
                return self.friday
            case 6:
                return self.saturday
            case _:
                raise ValueError("Day integer was not 1-6", integer)

    def no_shifts(self, day: int) -> bool:
        number_of_shifts = len(self.int_to_day_list(day))
        return number_of_shifts == 0

    def double_shifts(self, day: int) -> bool:
        number_of_shifts = len(self.int_to_day_list(day))
        return number_of_shifts == 2


class EmployeeList:
    # Employees should be a list of dictionaries, each dictionary in the list is an employee.
    # Employee dict values: name (string), max_hours (int), max_days (int), available_days (list), available_roles (list).
    def __init__(self, employees: list) -> None:
        self.num_employees = len(employees)
        self.employees = employees
        self.employee_hours_template = {}
        for person in self.employees:
            self.employee_hours_template[person["name"]] = 0
        self.employee_days_template = {}
        for person in self.employees:
            self.employee_days_template[person["name"]] = 0

    # A shift should be day: "monday", "tuesday",...  start: 0.0   end: 23.75   role: receptionist, assistant_one, runner...
    def fetch_available_employees(
        self, shift: dict, employee_hours: dict, employee_days: dict
    ):
        possibilities = []
        for person in self.employees:
            if (
                shift["day"] in person["available_days"]
                and shift["role"] in person["available_roles"]
            ):
                days = len(employee_days[person["name"]])
                if (
                    days < person["max_days"]
                    and shift["day"] not in employee_days[person["name"]]
                ):
                    shift_length = shift["end"] - shift["start"]
                    hours_worked = employee_hours[person["name"]]
                    if hours_worked + shift_length <= person["max_hours"]:
                        possibilities.append(person)
        return possibilities


"""Classes DentistSchedule and EmployeeList will have methods which give objective data. 
The 'subjective' calculation -- being which employee is best for a shift -- will be calculated by the Roster class.
The Roster class will also calculate which shifts are necessary, based on the hard-coded preset rules.

Employee preference will be weighted based on the number of hours already assigned (as shifts should be assigned in chronological order), number of available roles/which available roles, number of shifts of each role available, etc."""  # I AM IN A CRISIS OVER THIS MATHS RIGHT NOW BECAUZSXE I AM A MASSIOVE ENERD AND AM OVERTHINKING IT


class Roster:
    DAYS = ()

    def __init__(self, dentists: DentistSchedule, employees: EmployeeList) -> None:
        self.dentists = dentists
        self.employees = employees
        self.employee_hours = self.employees.employee_hours_template
        self.employee_days = self.employees.employee_days_template
        self.iterations = 0
        self.calculated_rosters = []  # The plan is to calculate the n best predicted iterations (meaning employee rules), then order by most preferable, and then iterate through until one is found which fits the rules.
        self.schedule = []
        # Calculate the shifts for self.schedule here
        if self.dentists.no_shifts(1):
            pass
        elif self.dentists.double_shifts(1):
            pass
        else:
            pass
        for dental_shift in self.dentists.monday:
            new_shift = {
                "day": "monday",
                "start": dental_shift["start"] - 0.5,
                "end": dental_shift["end"] + 0.25,
                "role": "assistant_" + str(dental_shift["id"]),
            }
            self.schedule.append(new_shift)

    def create_roster(self):
        pass
