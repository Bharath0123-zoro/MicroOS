#include "arcade_common.h"
#include <sys/wait.h>

static int launch_game(const char *prog) {
    pid_t pid = fork();
    if (pid == 0) {
        execlp(prog, prog, (char *)NULL);
        fprintf(stderr, "Micro Arcade: failed to launch '%s': %s\n", prog, strerror(errno));
        _exit(127);
    }
    if (pid < 0) return -1;
    int status = 0;
    while (waitpid(pid, &status, 0) < 0 && errno == EINTR) {}
    return status;
}

int main(void) {
    char buf[64];

    for (;;) {
        printf("================================\n");
        printf("MICRO ARCADE\n\n");
        printf("1. Snake             (Best: %d)\n", score_get("snake"));
        printf("2. Tetris            (Best: %d)\n", score_get("tetris"));
        printf("3. Pong              (Best: %d)\n", score_get("pong"));
        printf("4. Minesweeper       (Best: %d wins)\n", score_get("mines"));
        printf("5. 2048              (Best: %d)\n", score_get("2048"));
        printf("6. Number Guessing   (Best: %d tries)\n", score_get("guess"));
        printf("7. Tic-Tac-Toe       (Best: %d wins)\n", score_get("tictactoe"));
        printf("8. Space Invaders    (Best: %d)\n", score_get("spaceinvaders"));
        printf("9. Exit\n\n");
        printf("Select game: ");
        fflush(stdout);

        if (!fgets(buf, sizeof(buf), stdin)) {
            printf("\n");
            break;
        }
        int choice = atoi(buf);
        switch (choice) {
            case 1: launch_game("snake"); break;
            case 2: launch_game("tetris"); break;
            case 3: launch_game("pong"); break;
            case 4: launch_game("mines"); break;
            case 5: launch_game("2048"); break;
            case 6: launch_game("guess"); break;
            case 7: launch_game("tictactoe"); break;
            case 8: launch_game("spaceinvaders"); break;
            case 9:
                return 0;
            default:
                printf("Invalid selection. Press Enter to continue...");
                fflush(stdout);
                if (!fgets(buf, sizeof(buf), stdin)) return 0;
                break;
        }
    }
    return 0;
}
