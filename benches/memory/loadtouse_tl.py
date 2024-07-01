from pysmelt.generators.procedural import init_local_rules
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
    )
    next_line_tests.append(bench.as_ref)
test_group(name="next_line_pointer_chase_tests", tests=next_line_tests)

next_page = []
for size in sizes:
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
    )
    next_page.append(bench.as_ref)
test_group(name="next_page_pointer_chase_tests", tests=next_page)


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
    )
    random_chase_tests.append(bench.as_ref)
test_group(name="randptrchase", tests=random_chase_tests)
