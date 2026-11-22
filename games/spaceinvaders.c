/* MicroOS Micro Arcade - Game 8: Space Invaders */
#include "arcade_common.h"

#define SW 46
#define SH 18
#define EROWS 3
#define ECOLS 9
#define MAX_BULLETS 8

typedef struct { int x, y, active; } Bullet;

static void render_screen(int w, int h, int ex, int ey, int px, int lives, int score, int best, int wave,
                          const int enemy[EROWS][ECOLS], const Bullet pbul[MAX_BULLETS], const Bullet ebul[MAX_BULLETS]) {
    char scr[SH][SW + 1];
    for (int y = 0; y < h; y++) {
        memset(scr[y], ' ', (size_t)w);
        scr[y][w] = '\0';
    }
    for (int r = 0; r < EROWS; r++)
        for (int c = 0; c < ECOLS; c++)
            if (enemy[r][c]) {
                int gx = ex + c * 3, gy = ey + r * 2;
                if (gy >= 0 && gy < h && gx >= 0 && gx + 1 < w) {
                    scr[gy][gx] = (r == 0) ? 'W' : 'M';
                    scr[gy][gx + 1] = (r == 0) ? 'W' : 'M';
                }
            }
    for (int i = 0; i < MAX_BULLETS; i++) {
        if (pbul[i].active && pbul[i].y >= 0 && pbul[i].y < h && pbul[i].x >= 0 && pbul[i].x < w)
            scr[pbul[i].y][pbul[i].x] = '|';
        if (ebul[i].active && ebul[i].y >= 0 && ebul[i].y < h && ebul[i].x >= 0 && ebul[i].x < w)
            scr[ebul[i].y][ebul[i].x] = '!';
    }
    if (px > 0) scr[h - 1][px - 1] = '/';
    scr[h - 1][px] = 'A';
    if (px + 1 < w) scr[h - 1][px + 1] = '\\';

    fputs("\033[H", stdout);
    printf("SPACE INVADERS   Score: %d  Best: %d  Wave: %d  Lives: %d\033[K\n",
           score, best, wave, lives);
    putchar('+'); for (int x = 0; x < w; x++) putchar('-'); puts("+");
    for (int y = 0; y < h; y++) printf("|%s|\n", scr[y]);
    putchar('+'); for (int x = 0; x < w; x++) putchar('-'); puts("+");
    puts("A/D or Left/Right: Move | Space: Fire | Q: Quit\033[K");
    fflush(stdout);
}

static int run_game(void) {
    int rows, cols;
    term_get_size(&rows, &cols);
    int w = (cols - 4 < SW) ? (cols - 4) : SW;
    if (w < 26) w = 26;
    int h = (rows - 6 < SH) ? (rows - 6) : SH;
    if (h < 12) h = 12;

    int enemy[EROWS][ECOLS];
    for (int r = 0; r < EROWS; r++)
        for (int c = 0; c < ECOLS; c++)
            enemy[r][c] = 1;

    int ex = 2, ey = 1, edir = 1;
    int px = w / 2, lives = 3, score = 0, wave = 1;
    int best = score_get("spaceinvaders");
    Bullet pbul[MAX_BULLETS] = {{0}};
    Bullet ebul[MAX_BULLETS] = {{0}};

    long long last_frame = now_ms();
    long long last_enemy = now_ms();
    int enemy_interval = 420;

    render_screen(w, h, ex, ey, px, lives, score, best, wave, enemy, pbul, ebul);

    while (lives > 0) {
        int key = term_read_key(15);
        if (key == 'q' || key == 'Q' || key == KEY_ESC) return 0;
        if ((key == KEY_LEFT || key == 'a' || key == 'A') && px > 1) px--;
        if ((key == KEY_RIGHT || key == 'd' || key == 'D') && px < w - 2) px++;
        if (key == ' ' || key == KEY_UP || key == 'w' || key == 'W') {
            for (int i = 0; i < MAX_BULLETS; i++) {
                if (!pbul[i].active) {
                    pbul[i].x = px;
                    pbul[i].y = h - 2;
                    pbul[i].active = 1;
                    break;
                }
            }
        }

        long long now = now_ms();
        if (now - last_frame >= 60) {
            last_frame = now;
            /* Move player bullets */
            for (int i = 0; i < MAX_BULLETS; i++) {
                if (!pbul[i].active) continue;
                pbul[i].y--;
                if (pbul[i].y < 0) { pbul[i].active = 0; continue; }
                for (int r = 0; r < EROWS; r++) {
                    for (int c = 0; c < ECOLS; c++) {
                        if (!enemy[r][c]) continue;
                        int bx = ex + c * 3;
                        int by = ey + r * 2;
                        if (pbul[i].y == by && pbul[i].x >= bx && pbul[i].x <= bx + 1) {
                            enemy[r][c] = 0;
                            pbul[i].active = 0;
                            score += 20;
                            if (score > best) best = score_update("spaceinvaders", score, 0);
                        }
                    }
                }
            }
            /* Move enemy bullets */
            for (int i = 0; i < MAX_BULLETS; i++) {
                if (!ebul[i].active) continue;
                ebul[i].y++;
                if (ebul[i].y >= h) { ebul[i].active = 0; continue; }
                if (ebul[i].y == h - 1 && abs(ebul[i].x - px) <= 1) {
                    ebul[i].active = 0;
                    lives--;
                }
            }
            /* Random enemy shot */
            if (rand() % 14 == 0) {
                for (int tries = 0; tries < 10; tries++) {
                    int r = rand() % EROWS, c = rand() % ECOLS;
                    if (enemy[r][c]) {
                        for (int i = 0; i < MAX_BULLETS; i++) {
                            if (!ebul[i].active) {
                                ebul[i].x = ex + c * 3;
                                ebul[i].y = ey + r * 2 + 1;
                                ebul[i].active = 1;
                                break;
                            }
                        }
                        break;
                    }
                }
            }
        }

        if (now - last_enemy >= enemy_interval) {
            last_enemy = now;
            int alive_cnt = 0, min_c = ECOLS, max_c = -1, max_r = -1;
            for (int r = 0; r < EROWS; r++)
                for (int c = 0; c < ECOLS; c++)
                    if (enemy[r][c]) {
                        alive_cnt++;
                        if (c < min_c) min_c = c;
                        if (c > max_c) max_c = c;
                        if (r > max_r) max_r = r;
                    }
            if (alive_cnt == 0) {
                wave++;
                for (int r = 0; r < EROWS; r++)
                    for (int c = 0; c < ECOLS; c++)
                        enemy[r][c] = 1;
                ex = 2; ey = 1; edir = 1;
                if (enemy_interval > 160) enemy_interval -= 45;
            } else {
                int left_edge = ex + min_c * 3;
                int right_edge = ex + max_c * 3 + 1;
                if ((edir > 0 && right_edge >= w - 2) || (edir < 0 && left_edge <= 1)) {
                    edir = -edir;
                    ey++;
                    if (ey + max_r * 2 >= h - 1) { lives = 0; break; }
                } else {
                    ex += edir;
                }
            }
        }

        /* Render */
        render_screen(w, h, ex, ey, px, lives, score, best, wave, enemy, pbul, ebul);
    }

    score_update("spaceinvaders", score, 0);
    fputs("\033[H\033[2J", stdout);
    printf("\n  === GAME OVER: SPACE INVADERS ===\n");
    printf("  Final Score: %d   Wave: %d   Best: %d\n\n", score, wave, score_get("spaceinvaders"));
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
