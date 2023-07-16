import dataclasses
from datetime import datetime

from ortools.sat.python.cp_model import IntVar, IntervalVar


@dataclasses.dataclass()
class SectionModel:
    name: str
    weeks: int
    start: IntVar
    interval: IntervalVar
    end: IntVar
    required_neighbours: set[str]
    banned_neighbours: set[str]


@dataclasses.dataclass()
class SectionResult:
    section_name: str
    start_week: int
    end_week: int

    def __str__(self):
        formatted_name = f"{self.section_name} "
        return f"{self.section_name:<25} {self.end_week - self.start_week:<2} weeks: {week_to_month_week(self.start_week)} to {week_to_month_week(self.end_week)}"


@dataclasses.dataclass
class SectionConstraint:
    name: str
    best_months: list[str]
    best_times: list[int]
    weeks: int
    required_neighbours: set[str]
    banned_neighbours: set[str]

    def __init__(self, name: str, best_months: list[str], number_of_weeks_to_travel: int, required_neighbours: set[str]= frozenset([]),
                 banned_neighbours: set[str]= frozenset([])):
        self.name = name
        self.best_months = best_months
        self.best_times = self._parse_times(best_months)
        self.weeks = number_of_weeks_to_travel
        self.required_neighbours = required_neighbours
        self.banned_neighbours = banned_neighbours

    def _parse_times(self, best_times: list[str]) -> list[int]:
        week_numbers = []
        for month in best_times:
            week_ranges = WEEKS_2023_2024[month]
            for week_range in week_ranges:
                for r in range(week_range[0], week_range[1]):
                    week_numbers.append(r)

        return sorted(week_numbers)

    def __str__(self):
        required_neighbours = f", must be adjacent to {self.required_neighbours}" if self.required_neighbours else ""
        banned_neighbours = f"and not adjacent to {self.banned_neighbours}" if self.banned_neighbours else ""
        return f"{self.name}: Only in {self.best_months} {required_neighbours} {banned_neighbours}"


@dataclasses.dataclass
class Solution:
    section_results: list[SectionResult]


def week_to_month_week(week_number):
    if week_number > 52:
        week_number = week_number % 52
        year = "2024"
    else:
        year = "2023"
    if week_number == 0:
        week_number = 1
    d = datetime.fromisocalendar(2022, week_number, 1)  # ISO weeks start from Monday.
    month_name = d.strftime("%B")  # get month's name, i.e. 'January'
    start_of_the_month = d.replace(day=1)  # get the first day of the month
    week_of_month = (d - start_of_the_month).days // 7 + 1  # calculate the week of the month
    return f"{month_name:<9} {year}, week {week_of_month:<2}"


WEEKS_2023_2024 = {
    "November": [(44, 48), (96, 100)],
    "December": [(48, 53), (100, 104)],
    "January": [(53, 57)],
    "February": [(57, 61)],
    "March": [(61, 65)],
    "April": [(65, 70)],
    "May": [(70, 74)],
    "June": [(74, 78)],
    "July": [(78, 83)],
    "August": [(83, 87)],
    "September": [(87, 92)],
    "October": [(92, 96)],
}

# for month, week_ranges in WEEKS_2023_2024.items():
#     print(month)
#     for a, b in week_ranges:
#         print(f"{week_to_month_week(a)} -> {week_to_month_week(b)}")
