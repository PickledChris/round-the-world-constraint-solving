import dataclasses
from datetime import datetime

from ortools.sat.python import cp_model

from model import SectionModel, SectionConstraint
from output import SolutionPrinter


def count_weeks(sections: list[SectionConstraint]):
    return sum(sec.weeks for sec in sections)


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
            allowed_values = [model.NewBoolVar("") for _ in section.best_times]
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

    # Prevent neighbours that have been blocklisted
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
    solution_printer.generate_visualisations(total_weeks=total_weeks)


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
    SectionConstraint(AT, ["March", "April", "May", "June"], 5, banned_neighbours=set()),
    SectionConstraint(CENTRAL_ASIA, ["May", "June", "July", "August", "September"], 8, banned_neighbours=set()),
    SectionConstraint(CHINA, ["May", "June", "July", "August", "September"], 4, banned_neighbours=set()),
    SectionConstraint(JAPAN, ["April", "May", "June", "July", "August", "September", "October"], 4, banned_neighbours=set()),
    SectionConstraint(NZPI, ["January", "February", "March", "April", "October", "November", "December"], 6, banned_neighbours=set()),
    SectionConstraint(
        NEPAL_AND_INDIA, ["January", "February", "March", "April", "October", "November", "December"], 4, banned_neighbours=set()
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
