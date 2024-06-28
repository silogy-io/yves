
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
#define ITERATIONS 100000
#endif

// unroll factor inside a kernel -- determines the amount an instruction is
// replicated inside a kernel loop e.g. if we are measuring latency of ADD, and
// have an UNROLL_FACTOR of 8, then there will be 8 add instructions for each
// iteration of the kernel
//
// Useful for tuning the ratio of the behaviour under load to the loop backedge
#ifndef UNROLL_FACTOR
#define UNROLL_FACTOR 32
#endif

#ifndef INST_CONTENT
#define INST_CONTENT "nop"
#endif

template <uint64_t depth>
// explicit load unroller
struct InstFunroller {
  static const volatile void generate() {
    asm volatile(INST_CONTENT);

    if constexpr (depth < UNROLL_FACTOR) {
      return InstFunroller<depth + 1>::generate();
    } else {
    }
  }
};

int main() {
  for (int i = 0; i < ITERATIONS; i++) {
    InstFunroller<0>::generate();
  }
}
