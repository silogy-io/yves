
#include "cJSON.h"
#include "time.h"
#include <asm/unistd.h>
#include <linux/limits.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
struct timespec start, stop;
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
    // not portable, tragically
    //{"walltime", PERF_COUNT_SW_TASK_CLOCK}

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
      fprintf(stderr,
              "Error opening event %s -- have you set perf event paranoid? \n",
              profile_events[i].alias);
      exit(EXIT_FAILURE);
    }

    ioctl(fd[i], PERF_EVENT_IOC_RESET, 0);
    ioctl(fd[i], PERF_EVENT_IOC_ENABLE, 0);
  }

  if (clock_gettime(CLOCK_REALTIME, &start) == -1) {
    fprintf(stderr, "clock gettime failed at the start");
    exit(EXIT_FAILURE);
  }
}

char *create_counter_str(void) {
  char *string = NULL;

  cJSON *counters = NULL;
  cJSON *counter = NULL;
  cJSON *counter_val = NULL;

  size_t index = 0;

  int i;
  long long count[MAX_EVENTS];
  for (i = 0; i < num_events; i++) {
    ioctl(fd[i], PERF_EVENT_IOC_DISABLE, 0);
    read(fd[i], &count[i], sizeof(long long));
    close(fd[i]);
  }

  if (clock_gettime(CLOCK_REALTIME, &stop) == -1) {
    fprintf(stderr, "clock gettime failed at the end of profiling");
    exit(EXIT_FAILURE);
  }

  int64_t interval_ns = 0;

  interval_ns =
      (stop.tv_sec - start.tv_sec) * 1e9; // Convert seconds to nanoseconds
  interval_ns += (stop.tv_nsec - start.tv_nsec); // Add the nanosecond part

  cJSON *top = cJSON_CreateObject();
  if (top == NULL) {
    goto end;
  }

  // counters = cJSON_CreateArray();
  // if (counters == NULL) {
  //   goto end;
  // }

  for (uint64_t i = 0; i < num_events; i++) {
    const linux_event_alias *alias = profile_events + i;

    uint64_t val = count[i];
    const char *name = alias->alias;
    counter_val = cJSON_CreateNumber(val);
    if (counter_val == NULL) {
      goto end;
    }
    cJSON_AddItemToObject(top, name, counter_val);
  }

  counter_val = cJSON_CreateNumber(interval_ns);
  if (counter_val == NULL) {
    goto end;
  }
  cJSON_AddItemToObject(top, "walltime_ns", counter_val);

  string = cJSON_Print(top);
  if (string == NULL) {
    fprintf(stderr, "Failed to put monitors to str.\n");
  }

end:
  cJSON_Delete(top);
  return string;
}

void __attribute__((destructor)) run_me_at_unload() {
  char *json_str = create_counter_str();

  char *target_root = getenv("TARGET_ROOT");
  char json_name[PATH_MAX + 50];
  sprintf(json_name, "%s/counters.json", target_root);
  printf("file name is %s", json_name);

  FILE *file = fopen(json_name, "w");
  if (file == NULL) {
    printf("Error opening file for counters!\n");
  }

  printf("%s\n", json_str);

  fputs(json_str, file);

  fclose(file);
}
