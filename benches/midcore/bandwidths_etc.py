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


def format_for_define(inst: str) -> str:
    inst = inst.replace(" ", "\\ ")
    return f'\\"{inst}\\"'


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


name_to_torture = {
    "nop_bw": "nop",
    "add_bw": "add x1, x2, x2",
}

nextlinebench = "inst_torture.cpp"
next_line_tests = []
for tname, inst in name_to_torture.items():
    benchmark = compile_local_ubench_zig(
        name=f"{tname}_torture",
        compiler_path=compiler_path,
        benchmark_path=nextlinebench,
        ubench_parameters={"INST_CONTENT": format_for_define(inst)},
        compiler_target=cpp_compiler.as_ref,
    )
    bench_bin = benchmark.get_outputs()["binary"]
    bench = mac_local_benchmark(
        name=f"{tname}_torture_mac",
        profiler_path=profiler_bin,
        benchmark_path=bench_bin,
        metadata={"content": inst},
    )

rob_bench = "rob.cpp"
potential_structure_sizes = [
    1,
    2,
    32,
    64,
    128,
    192,
    228,
    256,
    312,
    400,
    512,
    768,
    1024,
]
rob_chase_tests = []
PAYLOADS_PER_ITER = 8
TOTAL_ITER = 8000000
inst = "add x12, x1, x1"
# inst = "fadd d1, d2, d2"
for potential_structure_size in potential_structure_sizes:
    rob_benchmark = compile_local_ubench_zig(
        name=f"{potential_structure_size}_rob_capacity",
        compiler_path=compiler_path,
        benchmark_path=rob_bench,
        ubench_parameters={
            "PAYLOAD_PER_ITERATION": PAYLOADS_PER_ITER,
            "ITERATIONS": TOTAL_ITER,
            "OPS_PER_MISS": potential_structure_size,
            "INST_CONTENT": format_for_define(inst),
        },
        compiler_target=cpp_compiler.as_ref,
    )
    rob_bench_bin = rob_benchmark.get_outputs()["binary"]
    bench = mac_local_benchmark(
        name=f"{potential_structure_size}_rob_capacity_mac",
        profiler_path=profiler_bin,
        benchmark_path=rob_bench_bin,
        metadata={"TOTAL_MISSES": PAYLOADS_PER_ITER * TOTAL_ITER},
    )
    rob_chase_tests.append(bench.as_ref)
test_group(name="rob_capacity_sweep", tests=rob_chase_tests)
