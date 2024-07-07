
/*
 * This test seeks to capacity of "branch history" that can be held in
 * directional branch predictors, as well as the latency associated with
 * directional branch mispredicts
 *
 *
 *
 *
 *
 *
 *
 *
 */

#include <cstdint>

#ifndef ITERATIONS
#define ITERATIONS 1000
#endif

#ifndef INNER_ITERATIONS
#define INNER_ITERATIONS 2
#endif

#ifndef NUM_BRANCHES
#define NUM_BRANCHES 512
#endif

template <uint64_t depth> struct NoopUnroller {
  static const void generate() {
    asm volatile("nop");
    if constexpr (depth != 0) {
      return NoopUnroller<depth - 1>::generate();
    }
  }
};

inline uint64_t xorrng(uint64_t x) {
  x ^= x << 13;
  x ^= x >> 7;
  x ^= x << 17;
  return x;
}

template <uint64_t depth> struct BranchFunroller {
  static const void generate(uint64_t &val) {
    constexpr uint64_t one = 1;
    constexpr uint64_t bit = one << (depth % 64);
    if constexpr (depth % 64 == 0) {
      val = xorrng(val);
    }
    if (val & bit) {
      asm volatile("nop");
    }
    if constexpr (depth != 0) {
      return BranchFunroller<depth - 1>::generate(val);
    }
  }
};

int main() {
  for (int i = 0; i < ITERATIONS; i++) {
    uint64_t val = 0x3fa4b2c8a9e17d52;
    for (int j = 0; j < INNER_ITERATIONS; j++) {
      BranchFunroller<NUM_BRANCHES>::generate(val);
    }
  }
}
