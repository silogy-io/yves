from typing import ClassVar, Dict, List
from pysmelt.interfaces.analysis import IQL, TestResult
import json
from yves.analysis.helper import (
    ExperimentGraph,
    PerformanceCounters,
    load_counters,
    load_metadata,
)
from yves.viz.viz import YvesViz


def midcore_analysis(iql: IQL) -> List[ExperimentGraph]:
    rob_tests = iql.get_tests_from_testgroup("rob_capacity_sweep")
    exps = []
    if rob_tests:
        x = []
        y = []
        for test in rob_tests:
            counters = load_counters(test)
            metadata = load_metadata(test)
            cycles = counters[counters.CYCLES]
            misses = metadata["TOTAL_MISSES"]
            spec_size = metadata["TESTED_SIZE"]
            x.append(spec_size)
            y.append(cycles / misses)
        exps.append(
            ExperimentGraph(
                name="rob_capacity_sweep",
                x_label="prospective rob size",
                y_label="cycles per access",
                x_values=x,
                y_values=y,
            )
        )

    else:
        pass
    return exps


if __name__ == "__main__":
    iql = IQL.from_previous()
    rv = midcore_analysis(iql)
    print(rv)
    YvesViz(rv).run()
