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
                description="next cache line ptr chase sweep -- x axis is the working set size of the ptr chase, y axis is cycle latency for each load"
                "any cpu worth its salt will capture this pattern with prefetchers"
                "early on in these experiments, iteration count is too low, and explains why cpi dips below the expected load to use latency",
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
                description="random ptr chase sweep -- x axis is the working set size of the ptr chase, y axis is cycle latency for each load"
                "the steep increases in on the y axis as x increases should inform when a new level of cache is being hit"
                "that x value is the approximate size of the cash -- x values are in kilobytes",
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
                description="similar to the next line pointer chase, but stride size is 4096 bytes -- often the page size for many systems"
                "this test sweep sweeps across accessing an increasing number of pages -- hopefully it would illuminate tlb size and miss latency, even with prefetching"
                "this sweep needs to be investigated",
            )
        )
    else:
        pass
    return experiments, observed_values


if __name__ == "__main__":
    iql = IQL.from_previous()
    rv, observed = memory_analysis(iql)
    YvesViz(rv, observed).run()
