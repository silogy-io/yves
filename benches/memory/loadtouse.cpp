/*
 * Single file microbenchmark for measuring load to use latency
 *
 *
 * Instr stream will stride through an entire payload array ITERATIONS number of
 * times
 *
 *
 *
 * parameters:
 *
 * RSS will determine size of the working set -- it is declared in kilobytes
 *
 * STRIDE will determine the "load distance" -- it is declared in bytes, and
 * must be aligned to the size of a uint64_t
 *
 * ITERATIONS will determine how many times the working set is
 *
 */

#include <cstdint>
#define RUNTIME_INIT_SIZE 2048

// The working set size, in kilobytes, used to configure how much memory is
// accessed for a particular test
#ifndef RSS
#define RSS 32
#endif

// The access stride, in bytes, used for any linear access test --
#ifndef STRIDE
#define STRIDE 64
#endif

// the iteration count of a kernel -- e.g. for a memset test, if iterations is
// 1000, then memset is called 1000 times
#ifndef ITERATIONS
#define ITERATIONS 1000
#endif

// unroll factor inside a kernel -- determines the amount an instruction is
// replicated inside a kernel loop e.g. if we are measuring latency of ADD, and
// have an UNROLL_FACTOR of 8, then there will be 8 add instructions for each
// iteration of the kernel
//
// Useful for tuning the ratio of the behaviour under load to the loop backedge
#ifndef UNROLL_FACTOR
#define UNROLL_FACTOR 8
#endif

constexpr void init_mem(uint64_t *payload, uint64_t size, uint64_t stride) {
  auto stride_as_word = stride;

  for (auto i = 0; i < size; i++) {
    payload[i] = (i * sizeof(uint64_t) + stride_as_word) % size;
  }
}

// Stride is declared in bytes
template <uint64_t size, uint64_t stride> struct StridedPtrChase {
  uint64_t payload[size];
  constexpr StridedPtrChase() {
    static_assert(stride % sizeof(uint64_t) == 0,
                  "Memory stride must be modulo 8");
    static_assert(stride >= sizeof(uint64_t),
                  "Memory stride must be greater than the size of a uint64_t");
    auto stride_as_word = stride;
    init_mem(payload, size, stride);
  }
};

// number of loads that need to occur to stride across the entire working set
// size
constexpr auto RSS_AS_KB = RSS * 1024 / sizeof(uint64_t);
constexpr auto LOADS_PER_ITERATION = RSS * 1024 / STRIDE;
static_assert(LOADS_PER_ITERATION % UNROLL_FACTOR == 0,
              "Unroll factor MUST must divide loads per iteration evenly");

template <uint64_t depth>
// explicit load unroller
struct LoadFunroller {
  static const volatile uint64_t *generate(const volatile uint64_t *baseline,
                                           const volatile uint64_t *p) {
    p = reinterpret_cast<const volatile uint64_t *>(
        reinterpret_cast<uint64_t>(baseline) + *p);
    if constexpr (depth < UNROLL_FACTOR) {
      return LoadFunroller<depth + 1>::generate(baseline, p);
    } else {
      return p;
    }
  }
};

int main() {

#if RSS < RUNTIME_INIT_SIZE
  constexpr auto array = StridedPtrChase<RSS_AS_KB, STRIDE>();

  const volatile uint64_t *p = &array.payload[0];
  const volatile uint64_t *baseline = &array.payload[0];
#else
  auto array = new uint64_t[RSS_AS_KB];
  init_mem(array, RSS_AS_KB, STRIDE);

  const volatile uint64_t *p = &array[0];
  const volatile uint64_t *baseline = &array[0];

#endif

  for (int i = 0; i < ITERATIONS; i++) {
    for (int j = 0; j < LOADS_PER_ITERATION; j++) {
      p = LoadFunroller<0>::generate(baseline, p);
    }
  }
}
