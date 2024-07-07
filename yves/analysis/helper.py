from typing import Any, ClassVar, Dict
from dataclasses import dataclass
from pysmelt.interfaces.analysis import IQL, TestResult
import json

from dataclasses import dataclass
from typing import List


@dataclass
class ExperimentGraph:
    name: str
    x_label: str
    y_label: str
    x_values: List[str]
    y_values: List[int]


def find_edges(lst: List[float], edge_size: float = 2.0) -> List[int]:
    return [i for i in range(len(lst) - 1) if lst[i + 1] >= edge_size * lst[i]]


@dataclass(frozen=True)
class PerformanceCounters:
    ctrs: Dict[str, int]
    CYCLES: ClassVar[str] = "cycles"
    INSTRUCTIONS: ClassVar[str] = "instructions"
    BRANCHES: ClassVar[str] = "branches"
    BRANCH_MISSES: ClassVar[str] = "branch-misses"

    @property
    def ipc(self) -> float:
        """
        Instructions per cycle -- fundamental description of bandwidth
        """
        return self.ctrs[self.INSTRUCTIONS] / self.ctrs[self.CYCLES]

    @property
    def branch_misprediction_rate(self) -> float:
        """
        percent of branches that are mispredicted -- should be a value between zero and one


        1.5 is returned instead of a NaN, because sometimes the branch stat is messed up on mac
        """
        try:
            mispred_rate = self.ctrs[self.BRANCH_MISSES] / self.ctrs[self.BRANCHES]
        except ZeroDivisionError:
            mispred_rate = -0.2
        return mispred_rate

    @property
    def cpi(self) -> float:
        return 1 / self.ipc

    def __getitem__(self, ctr_name: str) -> int:
        return self.ctrs[ctr_name]


def load_counters(test: TestResult) -> PerformanceCounters:
    artifact = next(
        (art for art in test.outputs.artifacts if art.artifact_name == "counters.json"),
        None,
    )
    if artifact is None:
        raise RuntimeError(f"Could not find result for {test}")
    js = json.load(open(artifact.path))
    return PerformanceCounters(ctrs=js)


def load_metadata(test: TestResult) -> Dict[str, Any]:
    artifact = next(
        (art for art in test.outputs.artifacts if art.artifact_name == "metadata.json"),
        None,
    )
    if artifact is None:
        raise RuntimeError(f"Could not find metadata {test}")
    js = json.load(open(artifact.path))
    return js
