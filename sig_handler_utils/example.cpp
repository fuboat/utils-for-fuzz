#include <iostream>

#define BOOST_STACKTRACE_USE_ADDR2LINE
#include <assert.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>

#include <boost/stacktrace.hpp>

void print_bt(void) {
    std::cout << boost::stacktrace::stacktrace() << std::endl;
}

static void handler(int sig, siginfo_t *dont_care, void *dont_care_either) {
    print_bt();
    exit(1);
}

void do_segv() {
    int x = 0;
    int y = 0;
    int z = x / y;
}

void do_abort() { assert(false); }

int main() {
    struct sigaction sa;

    memset(&sa, 0, sizeof(struct sigaction));
    sigemptyset(&sa.sa_mask);

    sa.sa_flags = SA_NODEFER;
    sa.sa_sigaction = handler;

    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGFPE, &sa, NULL);
    sigaction(SIGABRT, &sa, NULL);

    do_abort();

    return 0;
}
