/* MicroOS Micro Arcade - Game 5: 2048 */
#include "arcade_common.h"

static void spawn_tile(int g[4][4]) {
    int empty[16][2], n = 0;
    for (int r = 0; r < 4; r++)
        for (int c = 0; c < 4; c++)
            if (g[r][c] == 0) { empty[n][0] = r; empty[n][1] = c; n++; }
    if (n == 0) return;
    int pick = rand() % n;
    g[empty[pick][0]][empty[pick][1]] = (rand() % 10 == 0) ? 4 : 2;
}

static int slide_line(int line[4], int *score) {
    int orig[4];
    memcpy(orig, line, sizeof(orig));
    int tmp[4] = {0}, k = 0;
    for (int i = 0; i < 4; i++) if (line[i]) tmp[k++] = line[i];
    for (int i = 0; i < 3; i++) {
        if (tmp[i] && tmp[i] == tmp[i + 1]) {
            tmp[i] *= 2;
            *score += tmp[i];
            tmp[i + 1] = 0;
            i++;
        }
    }
    int out[4] = {0};
    k = 0;
    for (int i = 0; i < 4; i++) if (tmp[i]) out[k++] = tmp[i];
    memcpy(line, out, sizeof(out));
    return memcmp(orig, out, sizeof(orig)) != 0;
}

static int move_grid(int g[4][4], int dir, int *score) {
    /* dir: 0=left, 1=right, 2=up, 3=down */
    int moved = 0;
    for (int i = 0; i < 4; i++) {
        int line[4];
        for (int j = 0; j < 4; j++) {
            if (dir == 0) line[j] = g[i][j];
            else if (dir == 1) line[j] = g[i][3 - j];
            else if (dir == 2) line[j] = g[j][i];
            else line[j] = g[3 - j][i];
        }
        if (slide_line(line, score)) moved = 1;
        for (int j = 0; j < 4; j++) {
            if (dir == 0) g[i][j] = line[j];
            else if (dir == 1) g[i][3 - j] = line[j];
            else if (dir == 2) g[j][i] = line[j];
            else g[3 - j][i] = line[j];
        }
    }
    return moved;
}

static int can_move(const int g[4][4]) {
    for (int r = 0; r < 4; r++)
        for (int c = 0; c < 4; c++) {
            if (g[r][c] == 0) return 1;
            if (c < 3 && g[r][c] == g[r][c + 1]) return 1;
            if (r < 3 && g[r][c] == g[r + 1][c]) return 1;
        }
    return 0;
}

static int has_2048(const int g[4][4]) {
    for (int r = 0; r < 4; r++)
        for (int c = 0; c < 4; c++)
            if (g[r][c] >= 2048) return 1;
    return 0;
}

static int run_game(void) {
    int g[4][4] = {{0}};
    int score = 0, best = score_get("2048");
    int won_shown = 0;
    spawn_tile(g);
    spawn_tile(g);

    for (;;) {
        if (score > best) best = score_update("2048", score, 0);
        fputs("\033[H", stdout);
        printf("MICRO ARCADE: 2048   Score: %d   Best: %d\033[K\n", score, best);
        if (has_2048(g) && !won_shown) {
            puts("  *** YOU REACHED 2048! Keep playing or press Q to quit! ***");
            won_shown = 1;
        } else {
            puts("                                                            ");
        }
        puts("+------+------+------+------+");
        for (int r = 0; r < 4; r++) {
            putchar('|');
            for (int c = 0; c < 4; c++) {
                if (g[r][c]) printf(" %4d |", g[r][c]);
                else         printf("   .  |");
            }
            puts("\n+------+------+------+------+");
        }
        puts("Arrows / WASD: Slide tiles | R: Restart | Q: Quit\033[K");
        fflush(stdout);

        if (!can_move(g)) break;

        int key = term_read_key(150);
        if (key == 'q' || key == 'Q' || key == KEY_ESC) return 0;
        if (key == 'r' || key == 'R') return 1;
        int dir = -1;
        if (key == KEY_LEFT  || key == 'a' || key == 'A') dir = 0;
        if (key == KEY_RIGHT || key == 'd' || key == 'D') dir = 1;
        if (key == KEY_UP    || key == 'w' || key == 'W') dir = 2;
        if (key == KEY_DOWN  || key == 's' || key == 'S') dir = 3;
        if (dir >= 0 && move_grid(g, dir, &score)) {
            spawn_tile(g);
        }
    }

    score_update("2048", score, 0);
    printf("\n  === GAME OVER: 2048 ===\n  Final Score: %d   Best: %d\n", score, score_get("2048"));
    printf("  Press R to restart or Q to quit...\n");
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
