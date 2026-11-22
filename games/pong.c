/* MicroOS Micro Arcade - Game 3: Pong (Two-Player) */
#include "arcade_common.h"

#define WIN_SCORE 7

static void render_pong(int w, int h, int p1, int p2, int pad_h, int bx, int by, int s1, int s2) {
    fputs("\033[H", stdout);
    printf("MICRO ARCADE: PONG   P1: %d  |  P2: %d   (First to %d)\033[K\n", s1, s2, WIN_SCORE);
    putchar('+'); for (int x = 0; x < w; x++) putchar('-'); puts("+");
    for (int y = 0; y < h; y++) {
        putchar('|');
        for (int x = 0; x < w; x++) {
            char ch = ' ';
            if (x == w / 2) ch = ':';
            if (x == 1 && y >= p1 && y < p1 + pad_h) ch = '#';
            if (x == w - 2 && y >= p2 && y < p2 + pad_h) ch = '#';
            if (x == bx && y == by) ch = 'O';
            putchar(ch);
        }
        puts("|");
    }
    putchar('+'); for (int x = 0; x < w; x++) putchar('-'); puts("+");
    puts("P1: W/S   |   P2: Up/Down (or I/K)   |   Q: Quit\033[K");
    fflush(stdout);
}

static int run_game(void) {
    int rows, cols;
    term_get_size(&rows, &cols);
    int w = cols - 4; if (w > 64) w = 64; if (w < 30) w = 30;
    int h = rows - 6; if (h > 20) h = 20; if (h < 12) h = 12;
    int pad_h = 4;

    int p1 = h / 2 - pad_h / 2;
    int p2 = h / 2 - pad_h / 2;
    int bx = w / 2, by = h / 2;
    int bdx = (rand() & 1) ? 1 : -1;
    int bdy = (rand() & 1) ? 1 : -1;
    int s1 = 0, s2 = 0;
    long long last_tick = now_ms();

    render_pong(w, h, p1, p2, pad_h, bx, by, s1, s2);

    while (s1 < WIN_SCORE && s2 < WIN_SCORE) {
        int key = term_read_key(15);
        if (key == 'q' || key == 'Q' || key == KEY_ESC) return 0;
        if ((key == 'w' || key == 'W') && p1 > 0) p1--;
        if ((key == 's' || key == 'S') && p1 + pad_h < h) p1++;
        if ((key == KEY_UP || key == 'i' || key == 'I') && p2 > 0) p2--;
        if ((key == KEY_DOWN || key == 'k' || key == 'K') && p2 + pad_h < h) p2++;

        long long now = now_ms();
        if (now - last_tick >= 65) {
            last_tick = now;
            bx += bdx;
            by += bdy;
            if (by <= 0) { by = 0; bdy = 1; }
            if (by >= h - 1) { by = h - 1; bdy = -1; }

            /* Left paddle collision */
            if (bx == 2 && by >= p1 && by < p1 + pad_h) {
                bdx = 1;
                if (by == p1) bdy = -1;
                else if (by == p1 + pad_h - 1) bdy = 1;
            }
            /* Right paddle collision */
            if (bx == w - 3 && by >= p2 && by < p2 + pad_h) {
                bdx = -1;
                if (by == p2) bdy = -1;
                else if (by == p2 + pad_h - 1) bdy = 1;
            }

            if (bx <= 0) {
                s2++; bx = w / 2; by = h / 2; bdx = 1;
            } else if (bx >= w - 1) {
                s1++; bx = w / 2; by = h / 2; bdx = -1;
            }

            render_pong(w, h, p1, p2, pad_h, bx, by, s1, s2);
        }
    }

    int top = s1 > s2 ? s1 : s2;
    score_update("pong", top, 0);
    fputs("\033[H\033[2J", stdout);
    printf("\n  === PONG MATCH COMPLETE ===\n");
    printf("  Winner: Player %d (%d - %d)\n\n", s1 > s2 ? 1 : 2, s1, s2);
    printf("  Press R to rematch or Q to quit...\n");
    fflush(stdout);
    for (;;) {
        int k = term_read_key(200);
        if (k == 'r' || k == 'R') return 1;
        if (k == 'q' || k == 'Q' || k == KEY_ESC || k == KEY_ENTER) return 0;
    }
}

int main(void) {
    srand((unsigned)time(NULL) ^ (unsigned)getpid());
    term_raw_enable();
    while (run_game()) fputs("\033[2J\033[H", stdout);
    term_restore();
    return 0;
}
