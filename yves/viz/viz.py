from dataclasses import dataclass
from typing import Any, Dict, List, Union
from textual.app import App, ComposeResult, events, on
from textual.containers import Container, VerticalScroll
from textual.widgets import (
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
    TabPane,
    TabbedContent,
)
from textual_plotext import PlotextPlot
from yves.analysis.helper import ExperimentGraph
from rich.table import Table


class ObservedValueTable(Static):
    def __init__(self, observed_values: Dict[str, Any]):
        self.experiment = observed_values
        super().__init__()

    def on_mount(self) -> None:
        table = Table("Value name", "Value")
        table.title = "Derived values from experiments"
        for (
            x,
            y,
        ) in self.experiment.items():

            table.add_row(f"{x} ", f"{y} ")
        self.update(table)


class ExperimentAsTable(Static):

    def __init__(self, experiment: ExperimentGraph):
        self.experiment = experiment
        super().__init__()

    def on_mount(self) -> None:
        table = Table("Value name", "Value")
        table.title = self.experiment.name
        for (
            x,
            y,
        ) in zip(self.experiment.x_values, self.experiment.y_values):

            table.add_row(
                f"{x} {self.experiment.x_label}", f"{y} {self.experiment.y_label}"
            )
        self.update(table)


class YvesViz(App):
    CSS_PATH = "viz.tcss"

    def __init__(
        self, experiments: List[ExperimentGraph], observed_values: Dict[str, Any] = {}
    ):
        super().__init__()
        self.experiments = experiments
        # random observed values -- we add this as the first table in the table page
        self.observed_values = observed_values

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type(TabbedContent).active = tab

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent(initial="graphs"):
            with TabPane("graphs", id="graphs"):
                with Container():
                    yield ListView(
                        *[
                            ListItem(Label(experiment.name), id=f"exp-{idx}")
                            for idx, experiment in enumerate(self.experiments)
                        ],
                        id="plot-list",
                    )

                    yield PlotextPlot(id="plotter")
            with TabPane("tables", id="jessica"):
                with VerticalScroll():
                    if self.observed_values:
                        yield ObservedValueTable(self.observed_values)
                    for exp in self.experiments:
                        yield ExperimentAsTable(exp)

    @on(ListView.Selected, "#plot-list")
    def new_graph(self, message_type: ListView.Selected):

        idx = int(message_type.item.id.split("-")[-1])
        plot_data = self.experiments[idx]

        var = self.query_one("#plotter", expect_type=PlotextPlot)
        plt = var.plt
        plt.clear_data()
        plt.xlabel(plot_data.x_label)
        plt.ylabel(plot_data.y_label)
        xticks = [float(i) for i in range(len(plot_data.x_values))]
        xlabels = [str(xval) for xval in plot_data.x_values]
        plt.xticks(xticks, xlabels)

        plt.title(plot_data.name)
        plt.plot(range(len(plot_data.x_values)), plot_data.y_values)

        var.refresh()


if __name__ == "__main__":

    experiment_graphs = [
        ExperimentGraph(
            name="Experiment 1",
            x_label="x1",
            y_label="y1",
            x_values=list(range(1, 6)),
            y_values=list(range(1, 6)),
        ),
        ExperimentGraph(
            name="Experiment 2",
            x_label="x2",
            y_label="y2",
            x_values=list(range(2, 7)),
            y_values=list(range(2, 7)),
        ),
        ExperimentGraph(
            name="Experiment 3",
            x_label="x3",
            y_label="y3",
            x_values=list(range(3, 8)),
            y_values=list(range(3, 8)),
        ),
        ExperimentGraph(
            name="Experiment 4",
            x_label="x4",
            y_label="y4",
            x_values=list(range(4, 9)),
            y_values=list(range(4, 9)),
        ),
        ExperimentGraph(
            name="Experiment 5",
            x_label="x5",
            y_label="y5",
            x_values=list(range(5, 10)),
            y_values=list(range(5, 10)),
        ),
    ]

    YvesViz(experiment_graphs).run()
