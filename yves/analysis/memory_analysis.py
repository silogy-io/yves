from typing import Any, ClassVar, Dict, List, Tuple
from pysmelt.interfaces.analysis import IQL, TestResult
import json

from yves.analysis.helper import (
    ExperimentGraph,
    PerformanceCounters,
    load_counters,
    load_metadata,
)
from yves.viz.viz import YvesViz


iql = IQL.from_previous()


def memory_analysis(iql: IQL) -> Tuple[List[ExperimentGraph], Dict[str, Any]]:
    next_line_tests = iql.get_tests_from_testgroup("next_line_pointer_chase_tests")
    experiments = []
    observed_values = {}
    if next_line_tests:
        cpa = []
        x_axis = []
        for test in next_line_tests:
            counters = load_counters(test)
            metadata = load_metadata(test)

            cpa.append(counters.cpi)
            x_axis.append(metadata["RSS_IN_KB"])
        experiments.append(
            ExperimentGraph(
                name="next line pointer chase latency",
                x_label="working set size",
                y_label="cycles per access",
                x_values=x_axis,
                y_values=cpa,
            )
        )

    else:
        pass

    rand_chase = iql.get_tests_from_testgroup("randptrchase")
    if rand_chase:
        cpa = []
        x_axis = []
        for test in rand_chase:
            counters = load_counters(test)
            metadata = load_metadata(test)
            cpa.append(counters.cpi)
            x_axis.append(metadata["RSS_IN_KB"])
        experiments.append(
            ExperimentGraph(
                name="memory access latency",
                x_label="working set size",
                y_label="cycles per access",
                x_values=x_axis,
                y_values=cpa,
            )
        )
    else:
        pass

    dtlb_latency = iql.get_tests_from_testgroup("dtlb_latency_sweep")
    if dtlb_latency:
        cpa = []
        x_axis = []
        for test in dtlb_latency:
            counters = load_counters(test)
            metadata = load_metadata(test)
            cpa.append(counters.cpi)
            x_axis.append(str(metadata["PAGES_TOUCHED"]))
        experiments.append(
            ExperimentGraph(
                name="data tlb latency sweep",
                x_label="pages accessed",
                y_label="cycles per access",
                x_values=x_axis,
                y_values=cpa,
            )
        )
    else:
        pass
    return experiments, observed_values


if __name__ == "__main__":
    iql = IQL.from_previous()
    rv, observed = memory_analysis(iql)
    YvesViz(rv, observed).run()
