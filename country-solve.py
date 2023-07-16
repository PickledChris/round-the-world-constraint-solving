import dataclasses
import os
from pathlib import Path

from ortools.constraint_solver.pywrapcp import IntervalVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar
from datetime import datetime


@dataclasses.dataclass
class SectionConstraint:
    name: str
    best_times: list[int]
    weeks: int
    banned_neighbours: set[str]

    def __init__(self, name: str, best_times: list[str], number_of_weeks_to_travel: int, banned_neighbours: set[str]):
        self.name = name
        self.best_times = self._parse_times(best_times)
        self.weeks = number_of_weeks_to_travel
        self.banned_neighbours = banned_neighbours

    def _parse_times(self, best_times: list[str]) -> list[int]:
        week_numbers = []
        for month in best_times:
            week_ranges = WEEKS_2023_2024[month]
            for week_range in week_ranges:
                for r in range(week_range[0], week_range[1]):
                    week_numbers.append(r)

        return sorted(week_numbers)


@dataclasses.dataclass()
class SectionModel:
    name: str
    weeks: int
    start: IntVar
    interval: IntervalVar
    end: IntVar
    banned_neighbours: set[str]


@dataclasses.dataclass()
class SectionResult:
    section_name: str
    start_week: int
    end_week: int

    def __str__(self):
        formatted_name = f"{self.section_name} "
        return f"{self.section_name:<25} {self.end_week - self.start_week:<2} weeks: {week_to_month_week(self.start_week)} to {week_to_month_week(self.end_week)}"


def week_to_month_week(week_number):
    if week_number > 52:
        week_number = week_number % 52
    d = datetime.fromisocalendar(2022, week_number, 1)  # ISO weeks start from Monday.
    month_name = d.strftime("%B")  # get month's name, i.e. 'January'
    start_of_the_month = d.replace(day=1)  # get the first day of the month
    week_of_month = (d - start_of_the_month).days // 7 + 1  # calculate the week of the month
    return f"{month_name}-{week_of_month}"


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


def count_weeks(sections: list[SectionConstraint]):
    return sum(sec.weeks for sec in sections)


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, section_models: list[SectionModel]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._section_models = section_models
        self._solution_count = 0
        total_weeks = sum(m.weeks for m in section_models)
        self._filename = Path(f"out/solutions-{len(section_models)}-sections-{total_weeks}-weeks.txt")
        self._filename.unlink(missing_ok=True)

    def OnSolutionCallback(self):
        self._solution_count += 1
        section_results = [SectionResult(sm.name, self.Value(sm.start), self.Value(sm.end)) for sm in self._section_models]

        if self._solution_count % 5000 == 0:
            print(f"Solutions so far: {self._solution_count}")

        with open(self._filename, "a") as out:
            out.write(f"\nSolution: {self._solution_count}\n")

            for sr in sorted(section_results, key=lambda r: r.start_week):
                out.write(str(sr) + "\n")


def solve_trip_scheduling(section_constraints: list[SectionConstraint], start_week: int):
    model = cp_model.CpModel()
    total_weeks = count_weeks(section_constraints)
    end_week = start_week + total_weeks

    # Define the variables
    all_section_models: list[SectionModel] = []
    for i, section in enumerate(section_constraints):
        # From the start or earliest possible time, whichever is later
        earliest_start = max(start_week, min(section.best_times))
        # To the end or the last_viable week, whichever is sooner
        latest_end = min(end_week, max(section.best_times))

        start = model.NewIntVar(earliest_start, latest_end - section.weeks + 1, f"{section.name} start")
        end = model.NewIntVar(earliest_start + section.weeks, latest_end, f"{section.name} end")
        interval = model.NewIntervalVar(start, section.weeks, end, f"{section.name} interval")

        # Ensure that all weeks within the range are valid
        for w in range(section.weeks):
            week_index = start + w
            allowed_values = [model.NewBoolVar('') for _ in section.best_times]
            for value_var, time in zip(allowed_values, section.best_times):
                model.Add(week_index == time).OnlyEnforceIf(value_var)
            model.AddBoolOr(allowed_values)

        all_section_models.append(SectionModel(section.name, section.weeks, start, interval, end, section.banned_neighbours))

    models_by_name: dict[str, SectionModel] = {model.name: model for model in all_section_models}

    # Define the constraints
    all_intervals = [section.interval for section in all_section_models]
    model.AddNoOverlap(all_intervals)
    # Ensure that it's contiguous
    model.AddCumulative(all_intervals, [section.weeks for section in all_section_models], total_weeks)

    for section_model in all_section_models:
        for banned_neighbour in section_model.banned_neighbours:
            banned_neighbour_model = models_by_name[banned_neighbour]
            model.Add(section_model.start != banned_neighbour_model.end)
            model.Add(section_model.end != banned_neighbour_model.start)

    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solution_printer = SolutionPrinter(all_section_models)
    status = solver.SearchForAllSolutions(model, solution_printer)

    print("Status = ", status == cp_model.OPTIMAL)
    print("Solutions found : %i" % solution_printer._solution_count)
    print("Time = ", solver.WallTime(), "seconds")


AFRICA = "Southeast Africa"
AT = "Appalachian Trail"
CENTRAL_ASIA = "Central Asia"
CHINA = "China"
JAPAN = "Japan"
NEPAL_AND_INDIA = "Nepal and India"
NZPI = "New Zealand and PI"
SEA = "Southeast Asia"
SOUTH_AMERICA = "South America"

ALL = [AFRICA, AT, CENTRAL_ASIA, CHINA, JAPAN, NEPAL_AND_INDIA, NZPI, SEA, SOUTH_AMERICA]

sections = [
    SectionConstraint(AT, ["March", "April", "May", "June", "July", "August"], 5, banned_neighbours=set()),
    SectionConstraint(CENTRAL_ASIA, ["May", "June", "July", "August", "September"], 8, banned_neighbours=set()),
    SectionConstraint(CHINA, ["May", "June", "July", "August", "September"], 4, banned_neighbours=set()),
    SectionConstraint(JAPAN, ["April", "May", "June", "July", "August", "September", "October"], 4, banned_neighbours=set()),
    SectionConstraint(
        NZPI, ["January", "February", "March", "April", "September", "October", "November", "December"], 6, banned_neighbours=set()
    ),
    SectionConstraint(
        NEPAL_AND_INDIA, ["January", "February", "March", "April", "May", "November", "December"], 4, banned_neighbours=set()
    ),
    SectionConstraint(
        SOUTH_AMERICA,
        ["January", "February", "March", "April", "May", "September", "October", "November", "December"],
        9,
        banned_neighbours={AFRICA, SEA, NEPAL_AND_INDIA, CHINA, NZPI},
    ),
    SectionConstraint(
        AFRICA,
        ["January", "February", "March", "April", "July", "August", "September", "October", "November", "December"],
        10,
        banned_neighbours=set(),
    ),
    SectionConstraint(
        SEA,
        ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        6,
        banned_neighbours=set(),
    ),
]

print(f"{len(sections)} sections totalling {count_weeks(sections)} weeks")
for s in sections:
    print(s)
solve_trip_scheduling(sections, start_week=47)
