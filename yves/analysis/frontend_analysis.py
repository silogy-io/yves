from typing import Any, ClassVar, Dict, List, Tuple
from pysmelt.interfaces.analysis import IQL, TestResult
import json
import math

from yves.analysis.helper import (
    ExperimentGraph,
    PerformanceCounters,
    load_counters,
    load_metadata,
)
from yves.viz.viz import YvesViz


def frontend_analysis(iql: IQL) -> Tuple[List[ExperimentGraph], Dict[str, Any]]:
    next_line_tests = iql.get_tests_from_testgroup("directional_branch_history_sweep")
    experiments = []
    derived_values = {}
    if next_line_tests:
        cpb = []
        mispredict_rate = []
        x_axis = []
        for test in next_line_tests:
            counters = load_counters(test)
            metadata = load_metadata(test)

            cycles_per_branch = (
                counters[counters.CYCLES] / metadata["BRANCHES_OBSERVED"]
            )
            cpb.append(cycles_per_branch)
            mispredict_rate.append(counters.branch_misprediction_rate)
            x_axis.append(metadata["HISTORY"])

        # we have a few variables here: 
        # h = happy path latency -- the cycles latency for a correctly predicted branch. This value is contained in the variable cpb[0] 
        # u = mispredicted branch penalty -- cycles taken for a mispredicted branch.
        # 
        # algebraically, we know that
        # cpb[-1] == mispredict_rate[-1] * u + h 
        # 
        # with more substituting, we see 
        # cpb[-1] == mispredict_rate[-1] * u + cpb[0]
        # 
        # and finally u = (cpb[-1] - cpb[0]) / mispredict_rate[-1])
        #
        # there are some innacuracies that this method doesnt account for 
        # 1. really, we should be dividing by mispredict_rate[-1] - mispredict_rate[0], but for the smaller microbenchmarks, sometimes branches are not recorded 
        # 2. it assumes that there is only "one kind" of branch mispredict, which isn't true in all branch prediction microarchitectures now -- sometimes you may have a penalty 
        #
        observed_mispredict_penalty = f"{math.floor(
            (cpb[-1] - cpb[1]) / mispredict_rate[-1]
        )} cycles"
        derived_values["branch_mispred_cycle_penalty"] = observed_mispredict_penalty



        experiments.append(
            ExperimentGraph(
                name="directional branch history cycles per branch",
                x_label="unique directions per branch",
                y_label="cycles per branch",
                x_values=x_axis,
                y_values=cpb,
                description=f"""graphs how many cycles each branch bundle takes as the number of dynamic branches in the program increases -- this should illustrate the effective capacity of directional predictors

using some arithmetic described in frontend_analysis.py, it is observed that there is a:

{observed_mispredict_penalty} cycle penalty for a mispredicted branch

In a vaccum, that doesnt mean much -- many modern branch predictors also a micro predictor before their larger, more accurate predictor -- this number includes the penalty for missing both structures
                """
            )
        )
        experiments.append(
            ExperimentGraph(
                name="directional branch mispredict rate",
                x_label="history per branch",
                y_label="mispredict rate",
                x_values=x_axis,
                y_values=mispredict_rate,
                description="graphs branch mispredict_rate as a function of increased number of dynamic branches\n\n"
                            "in a vaccuum not interesting, but when compared to other chips, will give guidance on how large their branch predictors are, relatively"
            )
        )

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    else:
        pass
    return experiments, derived_values


if __name__ == "__main__":
    iql = IQL.from_previous()
    rv, observed = frontend_analysis(iql)
    YvesViz(rv, observed).run()
