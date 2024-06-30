from dataclasses import dataclass
import json
import platform

from pysmelt.default_targets import TargetRef
from pysmelt.interfaces import (
    RuntimeRequirements,
    Target,
    SmeltTargetType,
)
from typing import Any, List, Dict, Optional

from pysmelt.interfaces.procedural import import_as_target


@dataclass
class local_profiler(Target):
    compiler_download: TargetRef
    mac_sources: List[str]
    linux_sources: List[str]

    def get_dependencies(self) -> List[TargetRef]:
        return [self.compiler_download]

    @staticmethod
    def rule_type() -> SmeltTargetType:
        return SmeltTargetType.Build

    @property
    def profiler_path(self) -> str:
        return f"{self.ws_path}/profiler.so"

    def gen_script(self) -> List[str]:
        osname = platform.system()
        if osname == "Darwin":
            srcs = " ".join(self.mac_sources)
        elif osname == "Linux":
            srcs = " ".join(self.linux_sources)

        compiler_rule = import_as_target(self.compiler_download)

        compiler_path = compiler_rule.get_outputs()["compiler"]

        return [
            f"{compiler_path} cc -march=native -O3 -fPIC -shared {srcs} -o {self.ws_path}/profiler.so"
        ]

    def get_outputs(self) -> Dict[str, str]:
        return dict(profile_bin=self.profiler_path)


@dataclass
class local_benchmark(Target):
    profiler_path: str
    benchmark_path: str
    metadata: Optional[Dict[str, Any]] = None

    def get_dependent_files(self) -> List[str]:
        return [self.profiler_path, self.benchmark_path]

    @staticmethod
    def rule_type() -> SmeltTargetType:
        return SmeltTargetType.Test

    def gen_script(self) -> List[str]:
        metadata = self.metadata if self.metadata else {}
        metadata_content = f"'{json.dumps(metadata)}'"
        osname = platform.system()
        if osname == "Darwin":
            rv = f"DYLD_INSERT_LIBRARIES={self.profiler_path} {self.benchmark_path}"
        elif osname == "Linux":
            rv = f"LD_PRELOAD={self.profiler_path} {self.benchmark_path}"
        else:
            raise RuntimeError(f"Unsupported os {osname}")

        return [f"echo {metadata_content} &> {self.metadata_out()}", f"{rv}"]

    def metadata_out(self) -> str:
        return self.ws_path + "/metadata.json"

    def get_outputs(self) -> Dict[str, str]:
        ctr_file = self.ws_path + "/counters.json"

        return dict(counters=ctr_file, metadata=self.metadata_out())

    def runtime_requirements(self) -> RuntimeRequirements:
        rr = RuntimeRequirements.default()
        # Force the cpu requirement to be very high so only one benchmark runs
        # at a time
        rr.num_cpus = 1024
        return rr
