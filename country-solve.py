from ortools.sat.python import cp_model

import calendar


class Section:
    def __init__(self, name, best_times, weeks):
        self.name = name
        self.best_times = parse_times(best_times)
        self.weeks = weeks


def parse_times(best_times):
    times = best_times.lower().strip().split(' to ')
    start_month = list(calendar.month_name).index(times[0].capitalize())
    end_month = list(calendar.month_name).index(times[1].capitalize())
    return start_month, end_month


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
                f"{self._solution_count}: {self._sections[i].name}: week {self.Value(self._starts[i])} to {self.Value(self._starts[i])}")
        print("")


def solve_trip_scheduling(sections):
    model = cp_model.CpModel()

    num_sections = len(sections)

    starts = [model.NewIntVar(1, 52, '') for _ in range(num_sections)]
    ends = [model.NewIntVar(1, 52, '') for _ in range(num_sections)]

    for i in range(num_sections):
        model.Add(ends[i] - starts[i] + 1 == sections[i].weeks)
        if i < num_sections - 1:
            model.Add(starts[i + 1] >= ends[i])

    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(starts, ends, sections)
    status = solver.SearchForAllSolutions(model, solution_printer)


sections = [
    Section("Japan", "April to October", 4),
    Section("New Zealand", "September to April", 4),
    Section("Appalachian Trail", "March to August", 4),
    Section("Central Asia", "May to September", 6),
    Section("South America", "September to May", 9),
    Section("Southeast Africa", "July to March", 10),
    Section("China", "April to October", 2),
    Section("Southeast Asia", "January to December", 4),
    Section("Pacific Islands", "January to December", 2),
    Section("South Asia", "November to May", 4),
]

print(f"{len(sections)} totalling {sum(sec.weeks for sec in sections)}")
solve_trip_scheduling(sections)
