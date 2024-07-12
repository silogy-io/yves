from pysmelt.interfaces.procedural import import_as_target
from pysmelt.default_targets import test_group


from pysmelt.generators.procedural import init_local_rules


init_local_rules()
from compile import compile_local_ubench_zig
from profiler import local_benchmark


cpp_compiler = import_as_target("//download_zig.smelt.yaml:cpp_compiler")
profile_obj = import_as_target("//profilers/buildprof.smelt.yaml:profiler")


compiler_path = cpp_compiler.get_outputs()["compiler"]


profiler_bin = profile_obj.get_outputs()["profile_bin"]

branch_hist = "branch_hist.cpp"

bhist_iterations = 10000
per_branch_histories = [
    2,
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
    1024,
    1024 + 256,
    1024 + 512,
    2048,
]
num_branches = 1024
branch_tests = []
for size in per_branch_histories:
    benchmark = compile_local_ubench_zig(
        name=f"directional_branch_history_{size}",
        compiler_path=compiler_path,
        benchmark_path=branch_hist,
        ubench_parameters={
            "INNER_ITERATIONS": size,
            "ITERATIONS": bhist_iterations,
            "NUM_BRANCHES": num_branches,
        },
        compiler_target=cpp_compiler.as_ref,
    )
    bench_bin = benchmark.get_outputs()["binary"]
    bench = local_benchmark(
        name=f"directional_branch_history_{size}_local",
        profiler_path=profiler_bin,
        benchmark_path=bench_bin,
        metadata={
            "BRANCHES_OBSERVED": size * num_branches * bhist_iterations,
            "HISTORY": size,
        },
    )
    branch_tests.append(bench.as_ref)

dbh = test_group(name="directional_branch_history_sweep", tests=branch_tests)

ftcg = test_group(
    name="all_frontend_tests",
    tests=[dbh.as_ref],
)
