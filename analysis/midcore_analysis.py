from typing import ClassVar, Dict
from pysmelt.interfaces.analysis import IQL, TestResult
import json
from helper import PerformanceCounters, load_counters, load_metadata

iql = IQL.from_previous()


rob_tests = iql.get_tests_from_testgroup("rob_capacity_sweep")


if rob_tests:
    for test in rob_tests:
        counters = load_counters(test)
        metadata = load_metadata(test)
        cycles = counters[counters.CYCLES]
        misses = metadata["TOTAL_MISSES"]

        print(f"{test.test_name}: {cycles / misses}")

else:
    raise RuntimeError("Could not find shit! These tests didn't run ")
