/* MicroOS Micro Arcade - Game 1: Snake */
#include "arcade_common.h"

#define MAX_W 40
#define MAX_H 20
#define MAX_SNAKE (MAX_W * MAX_H)

typedef struct { int x, y; } Pt;

static void place_food(Pt *food, const Pt *body, int len, int w, int h) {
    for (int tries = 0; tries < 2000; tries++) {
        int fx = rand() % w;
        int fy = rand() % h;
        int hit = 0;
        for (int i = 0; i < len; i++) {
            if (body[i].x == fx && body[i].y == fy) { hit = 1; break; }
        }
        if (!hit) { food->x = fx; food->y = fy; return; }
    }
    food->x = 0; food->y = 0;
}

static void render_snake(int w, int h, const Pt *body, int len, const Pt *food, int score, int best, int delay_ms) {
    fputs("\033[H", stdout);
    printf("MICRO ARCADE: SNAKE   Score: %d   Best: %d   Speed: %dms\033[K\n", score, best, delay_ms);
    putchar('+'); for (int x = 0; x < w; x++) putchar('-'); puts("+");
    for (int y = 0; y < h; y++) {
        putchar('|');
        for (int x = 0; x < w; x++) {
            char ch = ' ';
            if (food->x == x && food->y == y) ch = '*';
            if (body[0].x == x && body[0].y == y) ch = '@';
            else {
                for (int i = 1; i < len; i++) {
                    if (body[i].x == x && body[i].y == y) { ch = 'o'; break; }
                }
            }
            putchar(ch);
        }
        puts("|");
    }
    putchar('+'); for (int x = 0; x < w; x++) putchar('-'); puts("+");
    puts("Controls: Arrows / WASD to move | Q to quit\033[K");
    fflush(stdout);
}

static int run_game(void) {
    int rows, cols;
    term_get_size(&rows, &cols);
    int w = cols - 6; if (w > MAX_W) w = MAX_W; if (w < 16) w = 16;
    int h = rows - 7; if (h > MAX_H) h = MAX_H; if (h < 10) h = 10;

    Pt body[MAX_SNAKE];
    int len = 4;
    for (int i = 0; i < len; i++) { body[i].x = w / 2 - i; body[i].y = h / 2; }
    int dx = 1, dy = 0;
    Pt food;
    place_food(&food, body, len, w, h);

    int score = 0;
    int best = score_get("snake");
    int delay_ms = 140;
    int alive = 1;
    long long last_tick = now_ms();

    render_snake(w, h, body, len, &food, score, best, delay_ms);

    while (alive) {
        int key = term_read_key(20);
        if (key == 'q' || key == 'Q' || key == KEY_ESC) return 0;
        if ((key == KEY_UP || key == 'w' || key == 'W') && dy != 1)    { dx = 0; dy = -1; }
        if ((key == KEY_DOWN || key == 's' || key == 'S') && dy != -1) { dx = 0; dy = 1; }
        if ((key == KEY_LEFT || key == 'a' || key == 'A') && dx != 1)  { dx = -1; dy = 0; }
        if ((key == KEY_RIGHT || key == 'd' || key == 'D') && dx != -1){ dx = 1; dy = 0; }

        long long now = now_ms();
        if (now - last_tick >= delay_ms) {
            last_tick = now;
            Pt next = { body[0].x + dx, body[0].y + dy };
            if (next.x < 0 || next.x >= w || next.y < 0 || next.y >= h) {
                alive = 0;
            } else {
                for (int i = 0; i < len - 1; i++) {
                    if (body[i].x == next.x && body[i].y == next.y) { alive = 0; break; }
                }
            }
            if (!alive) break;

            int ate = (next.x == food.x && next.y == food.y);
            if (ate && len < MAX_SNAKE) len++;
            for (int i = len - 1; i > 0; i--) body[i] = body[i - 1];
            body[0] = next;

            if (ate) {
                score += 10;
                if (score > best) best = score_update("snake", score, 0);
                if (delay_ms > 55) delay_ms -= 4;
                place_food(&food, body, len, w, h);
            }

            render_snake(w, h, body, len, &food, score, best, delay_ms);
        }
    }

    score_update("snake", score, 0);
    fputs("\033[H\033[2J", stdout);
    printf("\n  === GAME OVER: SNAKE ===\n");
    printf("  Final Score : %d\n", score);
    printf("  High Score  : %d\n\n", score_get("snake"));
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
    while (run_game()) {
        fputs("\033[2J\033[H", stdout);
    }
    term_restore();
    return 0;
}
