from typing import ClassVar, Dict
from pysmelt.interfaces.analysis import IQL, TestResult
import json
from helper import PerformanceCounters, load_counters

iql = IQL.from_previous()


next_line_tests = iql.get_tests_from_testgroup("next_line_pointer_chase_tests")
if next_line_tests:
    for test in next_line_tests:
        counters = load_counters(test)
        print(counters.cpi)
else:
    raise RuntimeError("Could not find shit! These tests didn't run ")


rand_chase = iql.get_tests_from_testgroup("randptrchase")
if rand_chase:
    for test in rand_chase:
        counters = load_counters(test)
        print(counters.cpi)
else:
    raise RuntimeError("Could not find shit! These tests didn't run ")
