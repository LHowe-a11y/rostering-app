class Schedule:
    def __init__(self, shifts: list) -> None:
        raw_shifts = shifts
        self.monday: list
        self.tuesday: list
        self.wednesday: list
        self.thursday: list
        self.friday: list
        self.saturday: list

        """This section sorts and formats each shift for easier processing"""

        # Sort the shifts chronologically
        raw_shifts.sort()
        # Split each shift into its own list of parts
        self.shifts = list(map(lambda x: x.split(":"), raw_shifts))

        # Shifts are in the form Day:Start:End:Dentist e.g. 1:0830:1300:2 would mean Monday, 8:30 am to 1:00 pm, Dentist 2.

        for shift in self.shifts:  # For each shift in the total list of shifts
            # Turn each part of the shift into an integer to allow mathematics
            for item in shift:
                item = int(item)
            # Add the shift to a sub-list of shifts per-day
            match shift[0]:
                case 1:
                    self.monday.append(shift)

                case 2:
                    self.tuesday.append(shift)

                case 3:
                    self.wednesday.append(shift)

                case 4:
                    self.thursday.append(shift)

                case 5:
                    self.friday.append(shift)

                case 6:
                    self.saturday.append(shift)

                # I regrettably find myself needing something like this more often than rarely
                case _:
                    raise TypeError(
                        "A shift has not been successfully turned into a list of integers.",
                        shift,
                    )


class Roster:
    def __init__(self, dentist_schedule: Schedule) -> None:
        pass

    def create_roster(self):
        pass
