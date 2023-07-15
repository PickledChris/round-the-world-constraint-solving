import dataclasses

from ortools.sat.python import cp_model

from weeks import WEEKS_2023_2024


@dataclasses.dataclass
class Section:
    name: str
    best_times: list[int]
    weeks: int

    def __init__(self, name, best_times: list[str], weeks):
        self.name = name
        self.best_times = parse_times(best_times)
        self.weeks = weeks


WEEKS_2023_2024 = {
    "November": (44, 48),
    "December": (48, 52),
    "January": (53, 57),
    "February": (57, 61),
    "March": (61, 65),
    "April": (66, 70),
    "May": (70, 74),
    "June": (74, 78),
    "July": (79, 83),
    "August": (83, 87),
    "September": (87, 92),
    "October": (92, 96),
    # "November": (96, 100)
}

month_index = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8,
               'september': 9, 'october': 10, 'november': 11, 'december': 12}


def get_week_numbers(month_name, year=2023):
    month = month_index[month_name]

    return WEEKS_2023_2024[month + (2023 - 2023)]


def parse_times(best_times: list[str]) -> list[int]:
    week_numbers = []
    for month in best_times:
        weeks = WEEKS_2023_2024[month]
        for x in range(weeks[0], weeks[1]):
            week_numbers.append(x)

    return sorted(week_numbers)


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, starts, ends, sections):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._starts = starts
        self._ends = ends
        self._sections = sections
        self._solution_count = 0

    def OnSolutionCallback(self):
        self._solution_count += 1
        for i in range(len(self._starts)):
            print(
                f"{self._solution_count}: {self._sections[i].name}: week {self.Value(self._starts[i])} to {self.Value(self._ends[i])}")
        print("")


def solve_trip_scheduling(sections):
    model = cp_model.CpModel()

    num_sections = len(sections)

    starts = [model.NewIntVar(44, 44 + 52, '') for _ in range(num_sections)]
    ends = [model.NewIntVar(44, 44 + 52, '') for _ in range(num_sections)]

    for i in range(num_sections):
        model.Add(ends[i] - starts[i] + 1 == sections[i].weeks)
        domain_weeks = model.NewIntVarFromDomain(cp_model.Domain.FromValues(sections[i].best_times), f'domain-{i}')
        domain_weeks
        model.AddVariableElement(ends[i], domain_i)

        model.Add(ends[i] <= sections[i].best_times[1])
        if i < num_sections - 1:
            model.Add(starts[i + 1] >= ends[i])

    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(starts, ends, sections)
    status = solver.SearchForAllSolutions(model, solution_printer)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Number of solutions found: {solution_printer._solution_count}')
    else:
        print('No Solution Found !')


sections = [
    # Section("Japan", ["April", "May", "June", "July", "August", "September", "October"], 4),
    Section("New Zealand", ["September", "October", "November", "December", "January", "February", "March", "April"], 4),
    # Section("Appalachian Trail", ["March", "April", "May", "June", "July", "August"], 4),
    # Section("Central Asia", ["May", "June", "July", "August", "September"], 6),
    # Section("South America", ["September", "October", "November", "December", "January", "February", "March", "April", "May"], 9),
    # Section("Southeast Africa", ["July", "August", "September", "October", "November", "December", "January", "February", "March"], 10),
    # Section("China", ["April", "May", "June", "July", "August", "September", "October"], 2),
    # Section("Southeast Asia",
    #         ["November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October"], 4),
    # Section("Pacific Islands",
    #         ["November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October"], 2),
    # Section("South Asia", ["November", "December", "January", "February", "March", "April", "May"], 4),
]

print(f"{len(sections)} sections totalling {sum(sec.weeks for sec in sections)} weeks")
for s in sections:
    print(s)
solve_trip_scheduling(sections)
