/* MicroOS Micro Arcade - Game 2: Tetris */
#include "arcade_common.h"

#define BW 10
#define BH 20

static const unsigned short SHAPES[7][4] = {
    {0x0F00, 0x2222, 0x00F0, 0x4444}, /* I */
    {0x8E00, 0x6440, 0x0E20, 0x44C0}, /* J */
    {0x2E00, 0x4460, 0x0E80, 0xC440}, /* L */
    {0x6600, 0x6600, 0x6600, 0x6600}, /* O */
    {0x6C00, 0x4620, 0x06C0, 0x8C40}, /* S */
    {0x4E00, 0x4640, 0x0E40, 0x4C40}, /* T */
    {0xC600, 0x2640, 0x0C60, 0x4C80}  /* Z */
};

static const char PIECE_CHAR[8] = " IJLOSTZ";

static int bit_at(int type, int rot, int r, int c) {
    return (SHAPES[type][rot & 3] >> (15 - (r * 4 + c))) & 1;
}

static int collides(const int board[BH][BW], int type, int rot, int px, int py) {
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            if (!bit_at(type, rot, r, c)) continue;
            int nx = px + c, ny = py + r;
            if (nx < 0 || nx >= BW || ny >= BH) return 1;
            if (ny >= 0 && board[ny][nx]) return 1;
        }
    }
    return 0;
}

static void render_tetris(const int board[BH][BW], int cur, int rot, int px, int py, int next_p, int score, int best, int lines, int level) {
    fputs("\033[H", stdout);
    printf("MICRO ARCADE: TETRIS   Score: %d  Best: %d  Lines: %d  Lv: %d\033[K\n",
           score, best, lines, level);
    printf("+--------------------+   Next:\n");
    for (int r = 0; r < BH; r++) {
        putchar('|');
        for (int c = 0; c < BW; c++) {
            int v = board[r][c];
            int pr = r - py, pc = c - px;
            if (pr >= 0 && pr < 4 && pc >= 0 && pc < 4 && bit_at(cur, rot, pr, pc))
                v = cur + 1;
            if (v) { putchar('['); putchar(PIECE_CHAR[v]); }
            else   { putchar(' '); putchar('.'); }
        }
        putchar('|');
        if (r < 4) {
            fputs("   ", stdout);
            for (int c = 0; c < 4; c++)
                fputs(bit_at(next_p, 0, r, c) ? "[]" : "  ", stdout);
        } else if (r == 6)  fputs("   A/D or Left/Right: Move", stdout);
        else if (r == 7)    fputs("   W or Up: Rotate", stdout);
        else if (r == 8)    fputs("   S or Down: Soft drop", stdout);
        else if (r == 9)    fputs("   Space: Hard drop", stdout);
        else if (r == 10)   fputs("   Q: Quit", stdout);
        fputs("\033[K\n", stdout);
    }
    puts("+--------------------+");
    fflush(stdout);
}

static int run_game(void) {
    int board[BH][BW];
    memset(board, 0, sizeof(board));

    int cur = rand() % 7, rot = 0, px = 3, py = 0;
    int next_p = rand() % 7;
    int score = 0, lines = 0, level = 1;
    int best = score_get("tetris");
    long long last_drop = now_ms();

    render_tetris(board, cur, rot, px, py, next_p, score, best, lines, level);

    for (;;) {
        int drop_ms = 550 - (level - 1) * 45;
        if (drop_ms < 100) drop_ms = 100;

        int key = term_read_key(20);
        if (key == 'q' || key == 'Q' || key == KEY_ESC) return 0;
        if ((key == KEY_LEFT || key == 'a' || key == 'A') && !collides(board, cur, rot, px - 1, py)) px--;
        if ((key == KEY_RIGHT || key == 'd' || key == 'D') && !collides(board, cur, rot, px + 1, py)) px++;
        if (key == KEY_UP || key == 'w' || key == 'W') {
            int nrot = (rot + 1) & 3;
            if (!collides(board, cur, nrot, px, py)) rot = nrot;
            else if (!collides(board, cur, nrot, px - 1, py)) { px--; rot = nrot; }
            else if (!collides(board, cur, nrot, px + 1, py)) { px++; rot = nrot; }
        }
        if (key == KEY_DOWN || key == 's' || key == 'S') {
            if (!collides(board, cur, rot, px, py + 1)) { py++; score += 1; }
        }
        if (key == ' ') {
            while (!collides(board, cur, rot, px, py + 1)) { py++; score += 2; }
            last_drop = 0;
        }

        long long now = now_ms();
        if (now - last_drop >= drop_ms) {
            last_drop = now;
            if (!collides(board, cur, rot, px, py + 1)) {
                py++;
            } else {
                for (int r = 0; r < 4; r++)
                    for (int c = 0; c < 4; c++)
                        if (bit_at(cur, rot, r, c) && py + r >= 0 && py + r < BH)
                            board[py + r][px + c] = cur + 1;

                int cleared = 0;
                for (int r = BH - 1; r >= 0; r--) {
                    int full = 1;
                    for (int c = 0; c < BW; c++) if (!board[r][c]) { full = 0; break; }
                    if (full) {
                        cleared++;
                        for (int rr = r; rr > 0; rr--)
                            memcpy(board[rr], board[rr - 1], sizeof(board[rr]));
                        memset(board[0], 0, sizeof(board[0]));
                        r++;
                    }
                }
                static const int pts[5] = {0, 100, 300, 500, 800};
                score += pts[cleared] * level;
                lines += cleared;
                level = 1 + lines / 10;
                if (score > best) best = score_update("tetris", score, 0);

                cur = next_p;
                next_p = rand() % 7;
                rot = 0; px = 3; py = 0;
                if (collides(board, cur, rot, px, py)) break;
            }
        }

        /* Render */
        render_tetris(board, cur, rot, px, py, next_p, score, best, lines, level);
    }

    score_update("tetris", score, 0);
    fputs("\033[H\033[2J", stdout);
    printf("\n  === GAME OVER: TETRIS ===\n");
    printf("  Score : %d   Lines : %d   High Score : %d\n\n", score, lines, score_get("tetris"));
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
