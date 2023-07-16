from datetime import date, datetime
from pathlib import Path

import july
import matplotlib.pyplot as plt
import pandas as pd
from ortools.sat.python import cp_model

from model import SectionModel, SectionResult, Solution, SectionConstraint
from textwrap import wrap


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, section_models: list[SectionModel]):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._section_models = section_models
        total_weeks = sum(m.weeks for m in section_models)
        self._filename = Path(f"out/solutions-{len(section_models)}-sections-{total_weeks}-weeks.txt")
        self._filename.unlink(missing_ok=True)
        self._solution_count = 0
        self._solutions = []

    def OnSolutionCallback(self):
        self._solution_count += 1
        section_results = [SectionResult(sm.name, self.Value(sm.start), self.Value(sm.end)) for sm in self._section_models]

        if self._solution_count % 5000 == 0:
            print(f"Solutions so far: {self._solution_count}")

        with open(self._filename, "a") as out:
            out.write(f"\nSolution: {self._solution_count}\n")

            sorted_results = sorted(section_results, key=lambda r: r.start_week)
            for sr in sorted_results:
                out.write(str(sr) + "\n")

            self._solutions.append(Solution(sorted_results))

    def generate_visualisations(self, section_constraints: list[SectionConstraint], total_weeks: int = 52, date_start="2023-11-01"):
        first_day = get_day_index_of_year(date_start)
        section_count = len(self._section_models)

        fig, axs = plt.subplots(section_count // 2 + 1, 2, figsize=(20, 33))  # Create N subplots in 1 column
        fig.suptitle(f"{self._solution_count} solutions, {section_count} sections, {total_weeks} weeks")

        def add_plot(data, index, model):
            ax1 = july.heatmap(data.days, data.section_count, cmap="Purples", ax=axs[index // 2, index % 2])
            ax1.set_title(f"{model.name}: {model.weeks} weeks")
            sc = [sc for sc in section_constraints if sc.name == model.name]
            ax1.set_xlabel("\n".join(wrap(str(sc[0]).removeprefix(model.name + ": "), 80)))

        for i, model in enumerate(self._section_models):

            all_section_results = [section_result for solution in self._solutions for section_result in solution.section_results if
                                   section_result.section_name == model.name]

            day_buffer = 60
            df = pd.DataFrame({'days': pd.date_range(date_start, periods=total_weeks * 7 + day_buffer, freq='D'), 'section_count': 0})
            # For each SectionResult in all_weeks set corresponding days to 1
            for section_result in all_section_results:
                start_day, end_day = week_to_day_range(section_result.start_week, section_result.start_week, first_day)
                df.loc[start_day - 1:end_day - 1, 'section_count'] += 1  # Accounting for zero-based indexing

            add_plot(df, i, model)

        if section_count % 2 != 0:
            axs[section_count // 2, 1].axis('off')

        plt.tight_layout()

        plt.show()


# Create a function to transform weeks to a range of days
def week_to_day_range(start_week: int, end_week: int, first_day: int):
    start_day = (start_week - 1) * 7 + 3
    end_day = end_week * 7 + 2
    return start_day - first_day, end_day - first_day


def get_day_index_of_year(date_string) -> int:
    date = datetime.strptime(date_string, "%Y-%m-%d")
    new_year_day = datetime(year=date.year, month=1, day=1)
    return (date - new_year_day).days + 1
