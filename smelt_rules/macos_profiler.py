from dataclasses import dataclass, field
import pathlib
from pysmelt.interfaces import Target, SmeltFilePath, SmeltTargetType, TargetRef
from typing import List, Dict, Optional, Tuple
import platform


@dataclass
class mac_local_benchmark(Target):
    profiler_path: str
    benchmark_path: str

    def get_dependent_files(self) -> List[str]:
        return [self.profiler_path, self.benchmark_path]

    @staticmethod
    def rule_type() -> SmeltTargetType:
        return SmeltTargetType.Test

    def gen_script(self) -> List[str]:
        return [f"DYLD_INSERT_LIBRARIES=./{self.profiler_path} ./{self.benchmark_path}"]

    def get_outputs(self) -> Dict[str, str]:
        ctr_file = pathlib.Path(self.benchmark_path).with_suffix(".json").name
        return dict(counters=ctr_file)