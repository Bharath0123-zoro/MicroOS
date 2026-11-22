/* MicroOS Micro Arcade - Game 4: Minesweeper */
#include "arcade_common.h"

#define MW 12
#define MH 10
#define MINES 16

static void reveal_flood(int r, int c, int mine[MH][MW], int rev[MH][MW], int flg[MH][MW], int adj[MH][MW]) {
    if (r < 0 || r >= MH || c < 0 || c >= MW) return;
    if (rev[r][c] || flg[r][c] || mine[r][c]) return;
    rev[r][c] = 1;
    if (adj[r][c] == 0) {
        for (int dr = -1; dr <= 1; dr++)
            for (int dc = -1; dc <= 1; dc++)
                if (dr || dc) reveal_flood(r + dr, c + dc, mine, rev, flg, adj);
    }
}

static int run_game(void) {
    int mine[MH][MW] = {{0}}, rev[MH][MW] = {{0}}, flg[MH][MW] = {{0}}, adj[MH][MW] = {{0}};
    int placed = 0;
    while (placed < MINES) {
        int r = rand() % MH, c = rand() % MW;
        if (!mine[r][c]) { mine[r][c] = 1; placed++; }
    }
    for (int r = 0; r < MH; r++) {
        for (int c = 0; c < MW; c++) {
            int cnt = 0;
            for (int dr = -1; dr <= 1; dr++)
                for (int dc = -1; dc <= 1; dc++) {
                    int nr = r + dr, nc = c + dc;
                    if (nr >= 0 && nr < MH && nc >= 0 && nc < MW && mine[nr][nc]) cnt++;
                }
            adj[r][c] = cnt;
        }
    }

    int cr = MH / 2, cc = MW / 2;
    int state = 0; /* 0=playing, 1=won, -1=lost */

    while (state == 0) {
        int flagged = 0, revealed = 0;
        for (int r = 0; r < MH; r++)
            for (int c = 0; c < MW; c++) {
                if (flg[r][c]) flagged++;
                if (rev[r][c]) revealed++;
            }
        if (revealed == MH * MW - MINES) { state = 1; break; }

        fputs("\033[H", stdout);
        printf("MICRO ARCADE: MINESWEEPER   Mines: %d  Flags: %d  Wins: %d\033[K\n",
               MINES, flagged, score_get("mines"));
        printf("+"); for (int c = 0; c < MW * 3; c++) putchar('-'); puts("+");
        for (int r = 0; r < MH; r++) {
            putchar('|');
            for (int c = 0; c < MW; c++) {
                char ch = '#';
                if (rev[r][c]) ch = adj[r][c] ? (char)('0' + adj[r][c]) : ' ';
                else if (flg[r][c]) ch = 'F';
                if (r == cr && c == cc) printf("[%c]", ch);
                else printf(" %c ", ch);
            }
            puts("|");
        }
        printf("+"); for (int c = 0; c < MW * 3; c++) putchar('-'); puts("+");
        puts("Arrows/WASD: Move | Space/Enter: Reveal | F: Flag | Q: Quit\033[K");
        fflush(stdout);

        int key = term_read_key(100);
        if (key == 'q' || key == 'Q' || key == KEY_ESC) return 0;
        if ((key == KEY_UP || key == 'w' || key == 'W') && cr > 0) cr--;
        if ((key == KEY_DOWN || key == 's' || key == 'S') && cr < MH - 1) cr++;
        if ((key == KEY_LEFT || key == 'a' || key == 'A') && cc > 0) cc--;
        if ((key == KEY_RIGHT || key == 'd' || key == 'D') && cc < MW - 1) cc++;
        if (key == 'f' || key == 'F') {
            if (!rev[cr][cc]) flg[cr][cc] = !flg[cr][cc];
        }
        if (key == ' ' || key == KEY_ENTER) {
            if (!flg[cr][cc]) {
                if (mine[cr][cc]) { state = -1; }
                else { reveal_flood(cr, cc, mine, rev, flg, adj); }
            }
        }
    }

    if (state == 1) score_update("mines", score_get("mines") + 1, 0);

    fputs("\033[H\033[2J", stdout);
    printf("MICRO ARCADE: MINESWEEPER — %s\n", state == 1 ? "YOU WIN!" : "BOOM! GAME OVER");
    printf("+"); for (int c = 0; c < MW * 3; c++) putchar('-'); puts("+");
    for (int r = 0; r < MH; r++) {
        putchar('|');
        for (int c = 0; c < MW; c++) {
            char ch = mine[r][c] ? '*' : (adj[r][c] ? (char)('0' + adj[r][c]) : ' ');
            printf(" %c ", ch);
        }
        puts("|");
    }
    printf("+"); for (int c = 0; c < MW * 3; c++) putchar('-'); puts("+");
    printf("Press R to play again or Q to quit...\n");
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
