
#include <asm/unistd.h>
#include <linux/perf_event.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                            int cpu, int group_fd, unsigned long flags) {
  int ret;

  ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
  return ret;
}

#define MAX_EVENTS 10
typedef struct {
  const char *alias; /// name for json, consistent with mac profiler
  int event_code;
} linux_event_alias;

static const linux_event_alias profile_events[] = {
    {"cycles", PERF_COUNT_HW_CPU_CYCLES},
    {"instructions", PERF_COUNT_HW_INSTRUCTIONS},

    {"branches", PERF_COUNT_HW_BRANCH_INSTRUCTIONS},
    {"branch-misses", PERF_COUNT_HW_BRANCH_MISSES},

};

static const int num_events =
    sizeof(profile_events) / sizeof(linux_event_alias);

int fd[MAX_EVENTS];

void __attribute__((constructor)) run_me_at_load_time() {

  int i;
  struct perf_event_attr pe[MAX_EVENTS];

  for (i = 0; i < num_events; i++) {
    memset(&pe[i], 0, sizeof(struct perf_event_attr));
    pe[i].type = PERF_TYPE_HARDWARE;
    pe[i].size = sizeof(struct perf_event_attr);
    pe[i].config = profile_events[i].event_code;
    pe[i].disabled = 1;
    pe[i].exclude_kernel = 1;
    pe[i].exclude_hv = 1;

    fd[i] = perf_event_open(&pe[i], 0, -1, -1, 0);
    if (fd[i] == -1) {
      fprintf(stderr, "Error opening event %d\n", i);
      exit(EXIT_FAILURE);
    }

    ioctl(fd[i], PERF_EVENT_IOC_RESET, 0);
    ioctl(fd[i], PERF_EVENT_IOC_ENABLE, 0);
  }
}

void __attribute__((destructor)) run_me_at_unload() {

  int i;
  long long count[MAX_EVENTS];
  for (i = 0; i < num_events; i++) {
    ioctl(fd[i], PERF_EVENT_IOC_DISABLE, 0);
    read(fd[i], &count[i], sizeof(long long));

    printf("Event %d: %lld\n", i, count[i]);

    close(fd[i]);
  }
}
