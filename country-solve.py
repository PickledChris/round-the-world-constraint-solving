import dataclasses

from ortools.constraint_solver.pywrapcp import IntervalVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar


@dataclasses.dataclass
class SectionConstraint:
    name: str
    best_times: list[int]
    weeks: int

    def __init__(self, name: str, best_times: list[str], number_of_weeks_to_travel: int):
        self.name = name
        self.best_times = self._parse_times(best_times)
        self.weeks = number_of_weeks_to_travel

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


@dataclasses.dataclass()
class SectionResult:
    section_name: str
    start_week: int
    end_week: int

    def __str__(self):
        return f"{self.section_name}: week {self.start_week} to {self.end_week}"


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

    def OnSolutionCallback(self):
        self._solution_count += 1
        section_results = [SectionResult(sm.name, self.Value(sm.start), self.Value(sm.end)) for sm in self._section_models]

        if self._solution_count % 5000 == 0:
            print(f"Solutions so far: {self._solution_count}")

        with open("out/solutions.txt", "a") as out:
            out.write(f"\nSolution: {self._solution_count}\n")

            for sr in sorted(section_results, key=lambda r: r.start_week):
                out.write(str(sr) +"\n")


def solve_trip_scheduling(section_constraints: list[SectionConstraint], start_week: int):
    model = cp_model.CpModel()
    total_weeks = count_weeks(section_constraints)
    end_week = start_week + total_weeks + 1

    # Define the variables
    all_sections: list[SectionModel] = []
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

        all_sections.append(SectionModel(section.name, section.weeks, start, interval, end))

    # Define the constraints
    all_intervals = [section.interval for section in all_sections]
    model.AddNoOverlap(all_intervals)
    model.AddCumulative(all_intervals, [section.weeks for section in all_sections], total_weeks)

    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solution_printer = SolutionPrinter(all_sections)
    status = solver.SearchForAllSolutions(model, solution_printer)

    print("Status = ", status == cp_model.OPTIMAL)
    print("Solutions found : %i" % solution_printer._solution_count)
    print("Time = ", solver.WallTime(), "seconds")


sections = [
    SectionConstraint("Japan", ["April", "May", "June", "July", "August", "September", "October"], 4),
    SectionConstraint("New Zealand and PI", ["September", "October", "November", "December", "January", "February", "March", "April"], 6),
    # SectionConstraint("Pacific Islands",
    #                   ["November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September",
    #                    "October"], 2),
    SectionConstraint("Appalachian Trail", ["March", "April", "May", "June", "July", "August"], 4),
    SectionConstraint("Central Asia", ["May", "June", "July", "August", "September"], 6),
    SectionConstraint("South America", ["September", "October", "November", "December", "January", "February", "March", "April", "May"], 9),
    SectionConstraint("Southeast Africa",
                      ["July", "August", "September", "October", "November", "December", "January", "February", "March"], 10),
    SectionConstraint("China", ["April", "May", "June", "July", "August", "September", "October"], 2),
    SectionConstraint("Southeast Asia",
                      ["November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September",
                       "October"], 4),
    SectionConstraint("South Asia", ["November", "December", "January", "February", "March", "April", "May"], 4)
]

print(f"{len(sections)} sections totalling {count_weeks(sections)} weeks")
for s in sections:
    print(s)
solve_trip_scheduling(sections, start_week=47)
