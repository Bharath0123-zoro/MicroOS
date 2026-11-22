/* MicroOS Micro Arcade - Game 7: Tic-Tac-Toe (2-Player & vs CPU) */
#include "arcade_common.h"

static char check_win(const char b[9]) {
    static const int lines[8][3] = {
        {0,1,2},{3,4,5},{6,7,8},
        {0,3,6},{1,4,7},{2,5,8},
        {0,4,8},{2,4,6}
    };
    for (int i = 0; i < 8; i++) {
        char a = b[lines[i][0]];
        if (a != ' ' && a == b[lines[i][1]] && a == b[lines[i][2]]) return a;
    }
    return 0;
}

static int board_full(const char b[9]) {
    for (int i = 0; i < 9; i++) if (b[i] == ' ') return 0;
    return 1;
}

static int cpu_pick(char b[9]) {
    /* 1. Try winning move for O */
    for (int i = 0; i < 9; i++) {
        if (b[i] == ' ') {
            b[i] = 'O';
            if (check_win(b) == 'O') { b[i] = ' '; return i; }
            b[i] = ' ';
        }
    }
    /* 2. Block X winning move */
    for (int i = 0; i < 9; i++) {
        if (b[i] == ' ') {
            b[i] = 'X';
            if (check_win(b) == 'X') { b[i] = ' '; return i; }
            b[i] = ' ';
        }
    }
    /* 3. Center, corners, then any */
    static const int pref[9] = {4, 0, 2, 6, 8, 1, 3, 5, 7};
    for (int i = 0; i < 9; i++) if (b[pref[i]] == ' ') return pref[i];
    return -1;
}

static void draw_board(const char b[9]) {
    printf("\n");
    for (int r = 0; r < 3; r++) {
        printf("   ");
        for (int c = 0; c < 3; c++) {
            int idx = r * 3 + c;
            char ch = (b[idx] == ' ') ? (char)('1' + idx) : b[idx];
            printf(" %c ", ch);
            if (c < 2) printf("|");
        }
        printf("\n");
        if (r < 2) printf("   ---+---+---\n");
    }
    printf("\n");
}

int main(void) {
    char buf[64];
    for (;;) {
        fputs("\033[2J\033[H", stdout);
        printf("=====================================\n");
        printf("MICRO ARCADE: TIC-TAC-TOE\n");
        printf("Total Wins Recorded: %d\n", score_get("tictactoe"));
        printf("=====================================\n");
        printf("  1. Single Player (You = X vs CPU = O)\n");
        printf("  2. Two Players   (Player X vs Player O)\n");
        printf("  3. Quit\n\n");
        printf("Select mode: ");
        fflush(stdout);
        if (!fgets(buf, sizeof(buf), stdin)) break;
        int mode = atoi(buf);
        if (mode == 3 || buf[0] == 'q' || buf[0] == 'Q') break;
        int vs_cpu = (mode != 2);

        char b[9];
        memset(b, ' ', sizeof(b));
        char turn = 'X';
        char winner = 0;

        while (!winner && !board_full(b)) {
            fputs("\033[2J\033[H", stdout);
            printf("TIC-TAC-TOE (%s)\n", vs_cpu ? "vs CPU" : "2-Player");
            draw_board(b);

            if (vs_cpu && turn == 'O') {
                int mv = cpu_pick(b);
                if (mv >= 0) b[mv] = 'O';
            } else {
                printf("Player %c move (1-9, or q to quit): ", turn);
                fflush(stdout);
                if (!fgets(buf, sizeof(buf), stdin)) return 0;
                if (buf[0] == 'q' || buf[0] == 'Q') return 0;
                int cell = atoi(buf) - 1;
                if (cell < 0 || cell > 8 || b[cell] != ' ') continue;
                b[cell] = turn;
            }
            winner = check_win(b);
            turn = (turn == 'X') ? 'O' : 'X';
        }

        fputs("\033[2J\033[H", stdout);
        draw_board(b);
        if (winner) {
            printf("  *** PLAYER %c WINS! ***\n", winner);
            if (!vs_cpu || winner == 'X') {
                score_update("tictactoe", score_get("tictactoe") + 1, 0);
            }
        } else {
            printf("  *** DRAW GAME! ***\n");
        }
        printf("\nPlay again? (y/n): ");
        fflush(stdout);
        if (!fgets(buf, sizeof(buf), stdin)) break;
        if (buf[0] != 'y' && buf[0] != 'Y') break;
    }
    return 0;
}
