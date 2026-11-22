#ifndef MICROOS_ARCADE_COMMON_H
#define MICROOS_ARCADE_COMMON_H

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/select.h>
#include <sys/stat.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

enum {
    KEY_NONE = 0,
    KEY_UP = 1000,
    KEY_DOWN,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_ENTER,
    KEY_ESC
};

static struct termios g_orig_termios;
static int g_raw_active = 0;

static inline void term_restore(void) {
    if (g_raw_active) {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &g_orig_termios);
        g_raw_active = 0;
    }
    fputs("\033[?25h\033[0m", stdout);
    fflush(stdout);
}

static inline void term_sig_handler(int sig) {
    (void)sig;
    term_restore();
    fputs("\n", stdout);
    fflush(stdout);
    _exit(0);
}

static inline void term_raw_enable(void) {
    if (!isatty(STDIN_FILENO)) return;
    if (tcgetattr(STDIN_FILENO, &g_orig_termios) == 0) {
        struct termios raw = g_orig_termios;
        raw.c_lflag &= (tcflag_t)~(ECHO | ICANON);
        raw.c_cc[VMIN] = 0;
        raw.c_cc[VTIME] = 0;
        if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) == 0) {
            g_raw_active = 1;
            signal(SIGINT, term_sig_handler);
            signal(SIGTERM, term_sig_handler);
        }
    }
    fputs("\033[?25l\033[2J\033[H", stdout);
    fflush(stdout);
}

static inline void term_get_size(int *rows, int *cols) {
    struct winsize ws;
    *rows = 24;
    *cols = 80;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0) {
        if (ws.ws_row > 0) *rows = ws.ws_row;
        if (ws.ws_col > 0) *cols = ws.ws_col;
    }
}

static inline int term_read_key(int timeout_ms) {
    fd_set rfds;
    struct timeval tv;
    FD_ZERO(&rfds);
    FD_SET(STDIN_FILENO, &rfds);
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    int r = select(STDIN_FILENO + 1, &rfds, NULL, NULL, timeout_ms < 0 ? NULL : &tv);
    if (r <= 0) return KEY_NONE;

    unsigned char c = 0;
    if (read(STDIN_FILENO, &c, 1) != 1) return KEY_NONE;

    if (c == '\r' || c == '\n') return KEY_ENTER;
    if (c == 27) {
        /* Check for arrow escape sequence ESC [ A/B/C/D */
        fd_set efds;
        struct timeval etv = {0, 25000};
        FD_ZERO(&efds);
        FD_SET(STDIN_FILENO, &efds);
        if (select(STDIN_FILENO + 1, &efds, NULL, NULL, &etv) > 0) {
            unsigned char seq[2] = {0, 0};
            if (read(STDIN_FILENO, &seq[0], 1) == 1 && (seq[0] == '[' || seq[0] == 'O')) {
                if (read(STDIN_FILENO, &seq[1], 1) == 1) {
                    if (seq[1] == 'A') return KEY_UP;
                    if (seq[1] == 'B') return KEY_DOWN;
                    if (seq[1] == 'C') return KEY_RIGHT;
                    if (seq[1] == 'D') return KEY_LEFT;
                }
            }
        }
        return KEY_ESC;
    }
    return (int)c;
}

static inline const char *score_db_path(void) {
    struct stat st;
    if (stat("/persist/arcade", &st) == 0 && S_ISDIR(st.st_mode)) {
        return "/persist/arcade/scores.db";
    }
    if (stat("/persist", &st) == 0 && S_ISDIR(st.st_mode)) {
        mkdir("/persist/arcade", 0755);
        if (stat("/persist/arcade", &st) == 0) {
            return "/persist/arcade/scores.db";
        }
    }
    return "/tmp/microos-scores.db";
}

static inline int score_get(const char *game) {
    FILE *f = fopen(score_db_path(), "r");
    if (!f) return 0;
    char name[64];
    int val = 0, best = 0;
    while (fscanf(f, "%63s %d", name, &val) == 2) {
        if (strcmp(name, game) == 0) {
            best = val;
            break;
        }
    }
    fclose(f);
    return best;
}

static inline int score_update(const char *game, int score, int lower_is_better) {
    int prev = score_get(game);
    int is_new = 0;
    if (lower_is_better) {
        if (score > 0 && (prev == 0 || score < prev)) is_new = 1;
    } else {
        if (score > prev) is_new = 1;
    }
    if (!is_new) return prev;

    const char *path = score_db_path();
    char names[32][64];
    int vals[32];
    int count = 0;
    int found = 0;

    FILE *f = fopen(path, "r");
    if (f) {
        while (count < 32 && fscanf(f, "%63s %d", names[count], &vals[count]) == 2) {
            if (strcmp(names[count], game) == 0) {
                vals[count] = score;
                found = 1;
            }
            count++;
        }
        fclose(f);
    }
    if (!found && count < 32) {
        snprintf(names[count], sizeof(names[count]), "%s", game);
        vals[count] = score;
        count++;
    }
    f = fopen(path, "w");
    if (f) {
        for (int i = 0; i < count; i++) {
            fprintf(f, "%s %d\n", names[i], vals[i]);
        }
        fclose(f);
    }
    return score;
}

static inline long long now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000LL + ts.tv_nsec / 1000000LL;
}

#endif
