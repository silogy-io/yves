from pysmelt.generators.procedural import init_local_rules
from pysmelt.interfaces.procedural import import_as_target
from pysmelt.default_targets import raw_bash_build
from pysmelt.path_utils import get_git_root
from pysmelt.default_targets import test_group


mod = init_local_rules()

from compile import download_zig, compile_local_ubench_zig
from macos_profiler import mac_local_benchmark

cpp_compiler = import_as_target("//download_zig.smelt.yaml:cpp_compiler")
compiler_path = cpp_compiler.get_outputs()["compiler"]


iterations = 10


src_path = f"{get_git_root()}/profilers"

mac_sources = " ".join([f"{src_path}/cJSON.c", f"{src_path}/mac_profiler.c"])


profile_obj = raw_bash_build(
    name="build_mac_profiler",
    # TODO FIXME:
    cmds=[
        f"{compiler_path} cc -march=native -O3 -fPIC -shared {mac_sources} -o $SMELT_ROOT/smelt-out/build_mac_profiler/profile.so"
    ],
    deps=[cpp_compiler.as_ref],
    outputs={"profile_bin": "$SMELT_ROOT/smelt-out/build_mac_profiler/profile.so"},
)


profiler_bin = profile_obj.get_outputs()["profile_bin"]


name_to_torture = {"nop": "nop"}

nextlinebench = "inst_torture.cpp"
next_line_tests = []
for tname, inst in name_to_torture.items():
    benchmark = compile_local_ubench_zig(
        name=f"{tname}_torture",
        compiler_path=compiler_path,
        benchmark_path=nextlinebench,
        ubench_parameters={"INST_CONTENT": f'"{inst}"'},
        compiler_target=cpp_compiler.as_ref,
    )
    bench_bin = benchmark.get_outputs()["binary"]
    bench = mac_local_benchmark(
        name=f"{tname}_torture_mac",
        profiler_path=profiler_bin,
        benchmark_path=bench_bin,
    )
