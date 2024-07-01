from pysmelt.interfaces.procedural import import_as_target
from pysmelt.default_targets import test_group

from yves.rules.compile import compile_local_ubench_zig
from yves.rules.profiler import local_benchmark

cpp_compiler = import_as_target("//download_zig.smelt.yaml:cpp_compiler")
profile_obj = import_as_target("//profilers/buildprof.smelt.yaml:profiler")


compiler_path = cpp_compiler.get_outputs()["compiler"]


iterations = 100


profiler_bin = profile_obj.get_outputs()["profile_bin"]

sizes = [2**n for n in range(2, 16)]

nextlinebench = "loadtouse.cpp"
next_line_tests = []
for size in sizes:
    benchmark = compile_local_ubench_zig(
        name=f"next_line_chase_{size}_kb",
        compiler_path=compiler_path,
        benchmark_path=nextlinebench,
        ubench_parameters={"RSS": size, "ITERATIONS": iterations},
        compiler_target=cpp_compiler.as_ref,
    )
    bench_bin = benchmark.get_outputs()["binary"]
    bench = local_benchmark(
        name=f"next_line_chase_{size}_kb_local",
        profiler_path=profiler_bin,
        benchmark_path=bench_bin,
        metadata={"RSS_IN_KB": size},
    )
    next_line_tests.append(bench.as_ref)
next_line_chase = test_group(
    name="next_line_pointer_chase_tests", tests=next_line_tests
)

page_sizes = [2**n for n in range(5, 16)]
next_page = []
for size in page_sizes:
    benchmark = compile_local_ubench_zig(
        name=f"next_page_chase_{size}_kb",
        compiler_path=compiler_path,
        benchmark_path=nextlinebench,
        ubench_parameters={"RSS": size, "ITERATIONS": iterations, "STRIDE": 4096},
        compiler_target=cpp_compiler.as_ref,
    )
    bench_bin = benchmark.get_outputs()["binary"]
    bench = local_benchmark(
        name=f"next_page_chase_{size}_kb_local",
        profiler_path=profiler_bin,
        benchmark_path=bench_bin,
        # this is in kb, so number of
        metadata={"PAGES_TOUCHED": size / 4},
    )
    next_page.append(bench.as_ref)
dtlbtg = test_group(name="dtlb_latency_sweep", tests=next_page)


random_chase_tests = []
random_chase_bench = "randptrchase.cpp"


for size in sizes:
    benchmark = compile_local_ubench_zig(
        name=f"rand_chase_{size}_kb",
        compiler_path=compiler_path,
        benchmark_path=random_chase_bench,
        ubench_parameters={"RSS": size, "ITERATIONS": iterations},
        compiler_target=cpp_compiler.as_ref,
    )
    bench_bin = benchmark.get_outputs()["binary"]
    bench = local_benchmark(
        name=f"rand_chase_{size}_kb_local",
        profiler_path=profiler_bin,
        benchmark_path=bench_bin,
        metadata={"RSS_IN_KB": size},
    )
    random_chase_tests.append(bench.as_ref)
rngtg = test_group(name="randptrchase", tests=random_chase_tests)

mctg = test_group(
    name="all_mem_tests", tests=[rngtg.as_ref, dtlbtg.as_ref, next_line_chase.as_ref]
)
