from typing import ClassVar, Dict, List
from pysmelt.interfaces.analysis import IQL, TestResult
import json
from yves.analysis.helper import (
    ExperimentGraph,
    PerformanceCounters,
    load_counters,
    load_metadata,
)
from yves.analysis.midcore_analysis import midcore_analysis
from yves.analysis.frontend_analysis import frontend_analysis
from yves.analysis.memory_analysis import memory_analysis
from yves.viz.viz import YvesViz


if __name__ == "__main__":
    iql = IQL.from_previous()
    frontend_exp, observed_fe = frontend_analysis(iql)
    midcore_exp, observed_midc = midcore_analysis(iql)
    memory_exp, observed_mem = memory_analysis(iql)
    observed = {**observed_fe, **observed_midc, **observed_mem}
    all_exp = [*frontend_exp, *midcore_exp, *memory_exp]
    YvesViz(all_exp, observed).run()
