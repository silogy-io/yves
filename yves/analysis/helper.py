from typing import Any, ClassVar, Dict
from dataclasses import dataclass
from pysmelt.interfaces.analysis import IQL, TestResult
import json


@dataclass(frozen=True)
class PerformanceCounters:
    ctrs: Dict[str, int]
    CYCLES: ClassVar[str] = "cycles"
    INSTRUCTIONS: ClassVar[str] = "instructions"

    @property
    def ipc(self) -> float:
        """
        Instructions per cycle -- fundamental description of bandwidth
        """
        return self.ctrs[self.INSTRUCTIONS] / self.ctrs[self.CYCLES]

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
