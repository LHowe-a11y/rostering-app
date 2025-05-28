# from decimal import Decimal
# from statistics import variance
import html
import bcrypt
import random
import statistics
import time


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
            self.employee_days_template[person["name"]] = []

    # A shift should be day: "monday", "tuesday",...  start: 0.0   end: 23.75   role: receptionist, assistant_1, runner...
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
    def __init__(self, dentists: DentistSchedule, employees: EmployeeList) -> None:
        self.best_roster = None
        self.r = random.Random()
        self.last_seed = (
            0  # Stores the final calculated seed after a generation has been performed
        )
        self.dentists = dentists
        self.employees = employees
        self.employee_hours = self.employees.employee_hours_template
        self.employee_days = self.employees.employee_days_template
        self.calculated_rosters = []  # The plan is to calculate the n best predicted iterations (meaning employee rules), then order by most preferable, and then iterate through until one is found which fits the rules.
        self.variances = {}
        self.schedule = []
        # Calculate the shifts for self.schedule here
        self.days_of_week = (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        )
        self.days_constructed = 0
        self.failed_seed = False
        for day in self.days_of_week:
            self.days_constructed += 1
            if self.dentists.no_shifts(self.days_constructed):
                pass
            elif self.dentists.double_shifts(self.days_constructed):
                new_shift = {
                    "day": day,
                    "start": 8.5,
                    "end": 16.0,
                    "role": "runner",
                }
                self.schedule.append(new_shift)

                dentist_one = self.dentists.int_to_day_list(self.days_constructed)[0]
                dentist_two = self.dentists.int_to_day_list(self.days_constructed)[1]

                if dentist_one["start"] <= dentist_two["start"]:
                    start_time = dentist_one["start"] + 0.5
                else:
                    start_time = dentist_two["start"] + 0.5

                if dentist_one["end"] >= dentist_two["end"]:
                    end_time = dentist_one["end"]
                else:
                    end_time = dentist_two["end"]

                new_shift = {
                    "day": day,
                    "start": start_time,
                    "end": end_time,
                    "role": "receptionist",
                }
                self.schedule.append(new_shift)
            else:
                dentist = self.dentists.int_to_day_list(self.days_constructed)[0]
                new_shift = {
                    "day": day,
                    "start": dentist["start"] + 0.5,
                    "end": dentist["end"],
                    "role": "receptionist",
                }
                self.schedule.append(new_shift)
            for dental_shift in self.dentists.int_to_day_list(self.days_constructed):
                new_shift = {
                    "day": day,
                    "start": dental_shift["start"] - 0.5,
                    "end": dental_shift["end"] + 0.25,
                    "role": "assistant_" + str(dental_shift["id"]),
                }
                self.schedule.append(new_shift)

    def create_roster(self) -> None:
        # necessary declarations/definitions of variables etc
        start_time = time.time()
        max_time = 10  # seconds
        n = 100
        min_calculated = 1  # should be later decided by user

        # All potential rosters are calculated in this loop
        while True:
            # calculation of n = 100
            for i in range(1, n + 1):
                seed = i + self.last_seed
                self.r.seed(seed)
                self.employee_hours = self.employees.employee_hours_template
                self.employee_days = self.employees.employee_days_template

                # calculate one permutation with a seed (maybe we grab the people with the lowest hours, if it's a tie, we pick randomly using seed, this would create more inital variation, yet still attempt to keep very fair)
                for shift in self.schedule:
                    available = self.employees.fetch_available_employees(
                        shift, self.employee_hours, self.employee_days
                    )
                    if len(available) == 0:
                        self.failed_seed = True
                        break
                    elif len(available) == 1:
                        assigned_employee = available[0]
                    else:
                        sorted_available = sorted(
                            available, key=lambda x: self.employee_hours[x["name"]]
                        )  # Sorts from current assigned hours low to high, still in list of employee dict form
                        lowest_hours = self.employee_hours[sorted_available[0]["name"]]
                        tied_lowest = []
                        for employee in sorted_available:
                            if self.employee_hours[employee["name"]] == lowest_hours:
                                tied_lowest.append(employee)
                            else:
                                break
                        choice = self.r.randint(0, len(tied_lowest) - 1)
                        assigned_employee = tied_lowest[choice]

                    # shift["assignee"] = assigned_employee
                    hours = shift["end"] - shift["start"]
                    self.employee_hours[assigned_employee["name"]] += hours
                    self.employee_days[assigned_employee["name"]].append(shift["day"])

                if self.failed_seed:
                    self.failed_seed = False
                    continue

                # calculate variance
                all_hours = []
                for x in self.employee_hours:
                    all_hours.append(self.employee_hours[x])
                variance = statistics.variance(all_hours)

                # store used "seed" and variance as dict key-value pair
                self.calculated_rosters.append(seed)
                self.variances[seed] = variance
            self.last_seed += n

            # check dict to see if any valid rosters have been found, if not try again, if yes continue
            if len(self.calculated_rosters) >= min_calculated:
                break
            if time.time() - start_time > max_time:
                # TODO timeout error message
                raise TimeoutError("Roster took too long to create.")

        # sort dict by variance ascending
        self.calculated_rosters = sorted(
            self.calculated_rosters, key=lambda x: self.variances[x]
        )

        # pick first dict value (maybe introduce a minimum fairness/maximum variance value user can input)
        self.best_roster = self.calculated_rosters[0]
        return

    def fetch_roster(self) -> list:
        self.r.seed(self.best_roster)
        self.employee_hours = self.employees.employee_hours_template
        self.employee_days = self.employees.employee_days_template
        for shift in self.schedule:
            available = self.employees.fetch_available_employees(
                shift, self.employee_hours, self.employee_days
            )
            if len(available) == 1:
                assigned_employee = available[0]
            else:
                sorted_available = sorted(
                    available, key=lambda x: self.employee_hours[x["name"]]
                )  # Sorts from current assigned hours low to high, still in list of employee dict form
                lowest_hours = self.employee_hours[sorted_available[0]["name"]]
                tied_lowest = []
                for employee in sorted_available:
                    if self.employee_hours[employee["name"]] == lowest_hours:
                        tied_lowest.append(employee)
                    else:
                        break
                choice = self.r.randint(0, len(tied_lowest) - 1)
                assigned_employee = tied_lowest[choice]

            shift["assignee"] = assigned_employee
            hours = shift["end"] - shift["start"]
            self.employee_hours[assigned_employee["name"]] += hours
            self.employee_days[assigned_employee["name"]].append(shift["day"])
        return self.schedule
