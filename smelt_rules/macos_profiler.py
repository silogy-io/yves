from dataclasses import dataclass

from pysmelt.default_targets import TargetRef
from pysmelt.interfaces import (
    RuntimeRequirements,
    Target,
    SmeltTargetType,
)
from typing import List, Dict

from pysmelt.interfaces.procedural import import_as_target


@dataclass
class build_mac_profiler(Target):
    compiler_download: TargetRef
    mac_sources: List[str]

    def get_dependencies(self) -> List[TargetRef]:
        return [self.compiler_download]

    @staticmethod
    def rule_type() -> SmeltTargetType:
        return SmeltTargetType.Build

    @property
    def profiler_path(self) -> str:
        return f"{self.ws_path}/profiler.so"

    def gen_script(self) -> List[str]:
        srcs = " ".join(self.mac_sources)

        compiler_rule = import_as_target(self.compiler_download)

        compiler_path = compiler_rule.get_outputs()["compiler"]

        return [
            f"{compiler_path} cc -march=native -O3 -fPIC -shared {srcs} -o {self.ws_path}/profiler.so"
        ]

    def get_outputs(self) -> Dict[str, str]:
        return dict(profile_bin=self.profiler_path)


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
        return [f"DYLD_INSERT_LIBRARIES={self.profiler_path} {self.benchmark_path}"]

    def get_outputs(self) -> Dict[str, str]:
        ctr_file = self.ws_path + "/counters.json"
        return dict(counters=ctr_file)

    def runtime_requirements(self) -> RuntimeRequirements:
        rr = RuntimeRequirements.default()
        # Force the cpu requirement to be very high so only one benchmark runs
        # at a time
        rr.num_cpus = 1024
        return rr
