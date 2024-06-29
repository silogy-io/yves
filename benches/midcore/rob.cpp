#include <cstdint>


#ifndef INST_CONTENT
#define INST_CONTENT "nop"
#endif

// The working set size, in kilobytes, used to configure how much memory is
// accessed 
#ifndef RSS
#define RSS 1024 * 192
#endif


// Number of times we iterate through the test

#ifndef ITERATIONS
#define ITERATIONS 1000
#endif

// unroll factor inside a kernel -- determines the amount of loads to backedges 
//
// Useful for tuning the ratio of the behaviour under load to the loop backedge
#ifndef OPS_PER_MISS
#define OPS_PER_MISS 8
#endif

#ifndef PAYLOAD_PER_ITERATION 
#define PAYLOAD_PER_ITERATION 8
#endif





#define RUNTIME_INIT_SIZE 1024

// all numbers are generated randomly at compile time. the internal state is pseudo
// remembered using the counter macro. the seed is based on time using the timestamp
// and time macro. additionally a custom random seed can be specified to fully rely

#ifndef RAND_SEED
#define RAND_SEED 0xbdac'f99b'3f7a'1bb4ULL
#endif



// just iterating over the macros will always result in same
// number because the internal state is only updated for each occurance
// of the following macros

// generates a random number seeded with time and the custom seed
#define DYC_RAND_NEXT (::Dynlec::CTRandomGeneratorValueSeeded<__COUNTER__>)
// generates a random number seeded with time and the custom seed between min and max ( [min, max[ )
#define DYC_RAND_NEXT_BETWEEN(min, max) (min + (::Dynlec::CTRandomGeneratorValueSeeded<__COUNTER__> % (max - min)))
// generates a random number seeded with time and the custom seed with a limit ( [0, limit[ )
#define DYC_RAND_NEXT_LIMIT(limit) DYC_RAND_NEXT_BETWEEN(0, limit)

namespace Dynlec
{
  // the random generator internal state is represented by
  // the CTRandomGeneratorRaw type with each of its values
  // x, y, z and c
  template <
    uint64_t x, 
    uint64_t y, 
    uint64_t z, 
    uint64_t c>
  class CTRandomGeneratorRaw
  {
    static_assert(y != 0, 
      "CompileTimeRandom can not be used with 'y' equals 0");
    static_assert(z != 0 || c != 0,
      "CompileTimeRandom can not be used with 'z' and 'c' equals 0");
  public:
    typedef CTRandomGeneratorRaw<
      6906969069ULL * x + 1234567ULL,
      ((y ^ (y << 13)) ^ ((y ^ (y << 13)) >> 17)) ^ (((y ^ (y << 13)) ^ ((y ^ (y << 13)) >> 17)) << 43),
      z + ((z << 58) + c),
      ((z + ((z << 58) + c)) >> 6) + (z + ((z << 58) + c) < ((z << 58) + c))> Next;

    constexpr static uint64_t Value = x + y + z;
  };

  // to prevent any accidental selection of invalid parameters
  // these values are omitted
  template <
    uint64_t x,
    uint64_t y,
    uint64_t z,
    uint64_t c>
  class CTRandomGeneratorRawSafe
    :
    public CTRandomGeneratorRaw<
      x, (y == 0) ? 1 : y, (z == 0 && c == 0) ? 1 : z, c>
  {
  };

  // CTRandomGenerator is used to quickly compute the nth iteration
  // of CTRandomGeneratorSafeRaw based on a single uint64_t seed
  template <uint64_t iterations, uint64_t seed>
  class CTRandomGenerator
  {
    friend CTRandomGenerator<iterations + 1, seed>;
    typedef typename CTRandomGenerator<iterations - 1, seed>::Current::Next Current;

  public:
    constexpr static uint64_t Value = Current::Value;
  };

  template <uint64_t seed>
  class CTRandomGenerator<0ULL, seed>
  {
    friend CTRandomGenerator<1ULL, seed>;

    typedef typename CTRandomGeneratorRawSafe<
      seed ^ 1066149217761810ULL,
      seed ^ 362436362436362436ULL,
      seed ^ 1234567890987654321ULL,
      seed ^ 123456123456123456ULL>::Next Current;

  public:
    constexpr static uint64_t Value = Current::Value;
  };

  template <uint64_t iteration, uint64_t seed>
  constexpr static uint64_t CTRandomGeneratorValue = CTRandomGenerator<iteration, seed>::Value;

  
  const uint64_t CTRandomSeed = (RAND_SEED);

  template <uint64_t iteration>
  constexpr static uint64_t CTRandomGeneratorValueSeeded = CTRandomGeneratorValue<iteration, CTRandomSeed>;

  template <uint64_t n, uint64_t seed = ::Dynlec::CTRandomSeed>
  struct CTRandomStream
  {
    // callback(uint64_t index [0;n[, uint64_t random_number)
    template <typename T>
    static void Call(T callback)
    {
      CTRandomStream<n - 1, seed>::Call(callback);
      callback(n - 1, CTRandomGeneratorValue<n, seed>);
    }
  };

  template <uint64_t seed>
  struct CTRandomStream<0, seed>
  {
    template <typename T>
    static void Call(T callback) { }
  };
}




constexpr auto RSS_AS_KB = RSS * 1024 / sizeof(uint64_t);





constexpr void randomize(uint64_t *indices, uint64_t len) {

  for (std::uint64_t i = 0; i < len; ++i) {
    indices[i] = i * sizeof(uint64_t);
  }
  for (uint64_t i = 0; i < len - 1; ++i) {
    uint64_t j = i + DYC_RAND_NEXT_BETWEEN(0,len - i);
    if (i != j) {
      auto tmp = indices[i];
      indices[i] = indices[j];
      indices[j] = tmp;
    }
  }
}

template <uint64_t size> struct RandomPtrChase{
  uint64_t payload[size];
  constexpr RandomPtrChase() {

    for (auto i = 0; i < size; i++) {
      payload[i] = i;
    }
    randomize(payload, size);
  }
};


template <uint64_t size> struct RuntimeRandomPtrChase{
  uint64_t * payload;
  RuntimeRandomPtrChase() {
    payload = new uint64_t[size];
    for (auto i = 0; i < size; i++) {
      payload[i] = i;
    }
    randomize(payload, size);
  }
  ~RuntimeRandomPtrChase() {
    delete[] payload;
  }
};



template <uint64_t depth>
// explicit load unroller
struct RobFunroller {
  static const volatile uint64_t *generate(const volatile uint64_t *baseline,
                                           const volatile uint64_t *p) {
    if constexpr(depth==0) {
      p = reinterpret_cast<const volatile uint64_t *>(
          reinterpret_cast<uint64_t>(baseline) + *(p));
    }
    if constexpr (depth < OPS_PER_MISS) {
      if constexpr(depth !=0) {
        asm volatile(INST_CONTENT);


      }
      return RobFunroller<depth + 1>::generate(baseline, p);
    } else {
      return p;
    }
  }
};

template <uint64_t depth>
struct MetaFunroller {
  static const volatile uint64_t *generate(const volatile uint64_t *baseline,
                                           const volatile uint64_t *p) {
    if constexpr (depth < PAYLOAD_PER_ITERATION) {
      p = RobFunroller<0>::generate(baseline,p);
      return MetaFunroller<depth+1>::generate(baseline,p);
    } else {
      return p;
    }
  }
};



int main() {
#if RSS < RUNTIME_INIT_SIZE
  constexpr auto array = RandomPtrChase<RSS_AS_KB>();
  const volatile uint64_t *p = &array.payload[0];
  const volatile uint64_t *baseline = &array.payload[0];
#else
  auto array = new uint64_t[RSS_AS_KB];
  randomize(array, RSS_AS_KB);

  const volatile uint64_t *p = &array[0];
  const volatile uint64_t *baseline = &array[0];
#endif
  for (int i = 0; i < ITERATIONS; i++) { 
    p = MetaFunroller<0>::generate(baseline,p);
  }
}
