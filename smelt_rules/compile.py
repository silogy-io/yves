from dataclasses import dataclass, field
import pathlib
from pysmelt.interfaces import Target, SmeltFilePath, SmeltTargetType, TargetRef
from typing import List, Dict, Optional, Tuple
import platform


@dataclass
class download_zig(Target):
    zig_version: str = "0.13.0"

    @staticmethod
    def rule_type() -> SmeltTargetType:
        return SmeltTargetType.Build

    @staticmethod
    def get_zigos_and_isa() -> Tuple[str, str]:
        os, isa = platform.system(), platform.machine()
        zigos, zigisa = None, None
        if os == "Darwin":
            zigos = "macos"
        if isa == "arm64":
            zigisa = "aarch64"

        if zigos is None or zigisa is None:
            raise NotImplementedError(
                f"The combo of {os} and {isa} isn't yet supported for downloading the zig toolchain"
            )
        return zigos, zigisa

    def gen_script(self) -> List[str]:
        zigos, zigisa = download_zig.get_zigos_and_isa()
        compiler_path = self.get_outputs()["compiler"]

        return [
            f"cd {self.ws_path}",
            f'if [ ! -f "{compiler_path}" ]; then',
            f"curl -o zig.tar.xz https://ziglang.org/download/{self.zig_version}/zig-{zigos}-{zigisa}-{self.zig_version}.tar.xz && tar xvf zig.tar.xz",
            "fi",
        ]

    def get_outputs(self) -> Dict[str, str]:
        zigos, zigisa = download_zig.get_zigos_and_isa()
        return dict(
            compiler=f"{self.ws_path}/zig-{zigos}-{zigisa}-{self.zig_version}/zig"
        )


@dataclass
class compile_local_ubench_zig(Target):
    compiler_path: str
    benchmark_path: str
    ubench_parameters: Dict[str, str]
    compiler_target: Optional[TargetRef] = None
    """ 
    microbenchark parameters are passed in as a tuple of name and value

    this is fed to the compile in the format of -D{KEY}={VALUE}
    """
    opt_flags: str = "-march=native -O3"

    @staticmethod
    def rule_type() -> SmeltTargetType:
        return SmeltTargetType.Stimulus

    def bin_name(self) -> str:
        binary_name = f"$SMELT_ROOT/smelt-out/{self.name}/" + self.name + ".el"
        return str(binary_name)

    def get_dependencies(self) -> List[TargetRef]:
        if self.compiler_target:
            return [self.compiler_target]
        else:
            return []

    def gen_script(self) -> List[str]:

        param_str = " ".join(
            [f"-D{KEY}={VALUE}" for KEY, VALUE in self.ubench_parameters.items()]
        )
        bmpath = pathlib.Path(self.benchmark_path)

        if bmpath.suffix == ".cpp":
            zig_cmd = "c++"
        elif bmpath.suffix == ".c":
            zig_cmd = "cc"
        else:
            raise RuntimeError(f"Unsupported suffix on benchmark {self.benchmark_path}")

        bin_name = self.bin_name()
        return [
            f"{self.compiler_path} {zig_cmd} {param_str} {self.opt_flags} {self.benchmark_path} -o {bin_name}"
        ]

    def get_outputs(self) -> Dict[str, str]:
        return dict(binary=self.bin_name())
