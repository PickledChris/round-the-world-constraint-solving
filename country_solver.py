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

        all_section_models.append(
            SectionModel(section.name, section.weeks, start, interval, end, section.required_neighbours, section.banned_neighbours))

    models_by_name: dict[str, SectionModel] = {model.name: model for model in all_section_models}

    # Define the constraints
    all_intervals = [section.interval for section in all_section_models]
    model.AddNoOverlap(all_intervals)
    # Ensure that it's contiguous
    model.AddCumulative(all_intervals, [section.weeks for section in all_section_models], total_weeks)

    # Require neighbours that have been explicitly required
    for section_model in all_section_models:
        for required_neighbour in section_model.required_neighbours:
            required_neighbour_model = models_by_name[required_neighbour]
            # A required neighbour should be before or after
            is_after = model.NewBoolVar('is_after')
            is_before = model.NewBoolVar('is_before')
            model.Add(section_model.start == required_neighbour_model.end).OnlyEnforceIf(is_after)
            model.Add(section_model.end == required_neighbour_model.start).OnlyEnforceIf(is_before)
            model.AddBoolOr([is_before, is_after])

    # Ban neighbours that have been blocklisted
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
    solution_printer.generate_visualisations(section_constraints, total_weeks=total_weeks)
