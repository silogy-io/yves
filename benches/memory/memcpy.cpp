/*
 * Single file microbenchmark for measuring memcpy bandwidth
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
 * STRIDE will determine the "copy distance" between each ld st pair-- it is
 * declared in bytes, and must be aligned to the size of a uint64_t. In
 * expectation, it should be
 *
 * ITERATIONS will determine how many times the working set is
 *
 */

#include <cstdint>

#ifndef RSS
#define RSS 32
#endif

#ifndef STRIDE
#define STRIDE 32
#endif

#ifndef ITERATIOS
#define ITERATIONS 1000
#endif

#ifndef UNROLL_FACTOR
#define UNROLL_FACTOR 32
#endif

// Stride is declared in bytes
template <uint64_t size, uint64_t stride> struct StridedPtrChase {
  uint64_t payload[size];
  constexpr StridedPtrChase() {
    static_assert(stride % sizeof(uint64_t) == 0,
                  "Memory stride must be modulo 8");
    static_assert(stride >= sizeof(uint64_t),
                  "Memory stride must be greater than the size of a uint64_t");
    auto stride_as_word = stride / sizeof(uint64_t);
    for (auto i = 0; i < size; i++) {
      payload[i] = (i + stride_as_word) % size;
    }
  }
};

constexpr auto RSS_AS_KB = RSS * 1024 / sizeof(uint64_t);
constexpr auto array = StridedPtrChase<RSS_AS_KB, STRIDE>();
// number of loads that need to occur to stride across the entire working set
// size
constexpr auto LOADS_PER_ITERATION = RSS * 1024 / STRIDE;

static_assert(LOADS_PER_ITERATION % UNROLL_FACTOR == 0,
              "Unroll factor MUST must divide loads per iteration evenly");

template <uint64_t depth>
// explicit load unroller
struct LoadFunroller {
  static const volatile uint64_t *generate(const volatile uint64_t *p) {
    p = reinterpret_cast<const volatile uint64_t *>(
        reinterpret_cast<uint64_t>(p) + *p);
    if constexpr (depth < UNROLL_FACTOR) {
      return LoadFunroller<depth + 1>::generate(p);
    } else {
      return p;
    }
  }
};

int main() {
  const volatile uint64_t *p = &array.payload[0];
  for (int i = 0; i < ITERATIONS; i++) {
    for (int j = 0; j < LOADS_PER_ITERATION; j++) {
      p = LoadFunroller<0>::generate(p);
    }
  }
}
