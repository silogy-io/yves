# Yves: a toolkit for performance testing

Yves is a suite of profilers, c++ benchmarks, [smelt](https://github.com/silogy-io/smelt) test lists and a python library for performance testing.

## Getting started

### Installation & setup

To get started, you'll need to install poetry, the python package manager:

```
pipx install poetry
```

After that completes, install yves with

```
poetry install
```

#### Linux setup

if you are on linux, you'll also need to set perf event paranoid to 0 to access perf counters

```
sudo sysctl kernel.perf_event_paranoid=0
```

### Running benchmarks

To run all of yves' benchmarks, launch smelt via:

```bash
poetry run smelt execute benches/all.smelt.yaml
```

If you are running on macos, you'll need to execute the benchmarks with sudo, in order to access performance counters:

```bash
sudo poetry run smelt execute benches/all.smelt.yaml
```

To view the output of the benchmarks, execute

```
poetry run yves/analysis/all.py
```

This will launch a `textual` application that can be exited via control-c

NOTE: to change the shown graph, press tab and then use the arrow keys

## Components

Yves is a collection of C++ benchmarks, [smelt](https://github.com/silogy-io/smelt) test lists and scripts for analysis.

### Profilers

Smelt includes a simple mac and linux profiler. These are simple, non-sampling profilers, that record performance counters events for the duration of a program, similar to `perf stat`.

I wrote these profilers for two reasons:

1. I wanted to do performance analysis on mac
2. I wanted this project to be as self contained as possible

Each profiler is compiled to a shared object and leverage the [LD_PRELOAD "trick"](https://stackoverflow.com/questions/426230/what-is-the-ld-preload-trick) to start counting events when each benchmark starts and ends. When each program exits, the performance counts are dumped to a json file in the current working directory named "counters.json"

The counters dumped currently are:

- cycles
- instructions
- branches
- branch-misses

Support for other counters could be brought up with a little elbow grease

### Benchmarks

All of the benchmarks are written in C++20, and leverage constexpr as much as possible. These benchmarks try to avoid using any system calls, so that the benchmarks can be re-used for the bring up of new designs. The exception to this is the use of "malloc" for large regions memory. Any benchmark that explicitly measures syscalls should be labeled as such

Additionally, every benchmark is a standalone, self-contained file that does not require any headers.

Each benchmark is written as a "template" with preprocessor defines that can be overridden. For example, for the random pointer chase benchmarks, the working set size of the memory foot print that is being pointer chased through is set via the RSS preprocessor variable.

### Compilers

By default, all benchmarks and profilers are compiled via zig 0.13.0, using the cc / c++ compiler functionality. I will bring up support for other compilers via godbolt if anyone asks.

### Testlists

The smelt test lists provide a mechanism to compile and run and profile benchmarks on your current machine. The "top level" test list is located at benches/all.smelt.yaml -- from there you can inspect the other test lists

### Analysis scripts

The smelt analysis scripts, that can be run after a test is executed, will parse the output of each benchmark and plot the data in the terminal.

## Future work

There are a futures I'd like to add, in no particular order:

- Running benchmarks on an open CPU or SOC (Ibex or SwerV)
- Adding directed instruction generation to measure latency and throughput of instructions
  - given a machine readable isa spec and a lot of labour, we could use this infra to re-create the Anger Fog tables for riscv/arm/x86
- Add many more benchmarks
  - all of the data prefetch patterns described at https://people.ucsc.edu/~hlitz/papers/asplos2020.pdf
  - icache capacity tests
  - memcpy, memset tests
  - simple GEMM/SGemm tests
