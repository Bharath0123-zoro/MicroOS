/* MicroOS Micro Arcade - Game 6: Number Guessing */
#include "arcade_common.h"

int main(void) {
    srand((unsigned)time(NULL) ^ (unsigned)getpid());
    char buf[64];

    for (;;) {
        fputs("\033[2J\033[H", stdout);
        printf("=====================================\n");
        printf("MICRO ARCADE: NUMBER GUESSING\n");
        printf("Best (fewest tries): %d\n", score_get("guess"));
        printf("=====================================\n");
        printf("Select difficulty:\n");
        printf("  1. Easy   (1 - 50)\n");
        printf("  2. Medium (1 - 100)\n");
        printf("  3. Hard   (1 - 500)\n");
        printf("  4. Quit\n\n");
        printf("Choice: ");
        fflush(stdout);

        if (!fgets(buf, sizeof(buf), stdin)) break;
        int diff = atoi(buf);
        if (diff == 4 || buf[0] == 'q' || buf[0] == 'Q') break;
        int max_n = (diff == 1) ? 50 : (diff == 3 ? 500 : 100);
        int secret = (rand() % max_n) + 1;
        int tries = 0;

        printf("\nI picked a secret number between 1 and %d. Type 'q' to quit.\n", max_n);
        for (;;) {
            printf("Guess #%d: ", tries + 1);
            fflush(stdout);
            if (!fgets(buf, sizeof(buf), stdin)) return 0;
            if (buf[0] == 'q' || buf[0] == 'Q') return 0;
            int g = atoi(buf);
            if (g < 1 || g > max_n) {
                printf("  Please enter a number between 1 and %d.\n", max_n);
                continue;
            }
            tries++;
            if (g < secret) {
                printf("  Higher!\n");
            } else if (g > secret) {
                printf("  Lower!\n");
            } else {
                printf("\n  CORRECT! The number was %d. Solved in %d attempts!\n", secret, tries);
                score_update("guess", tries, 1);
                printf("  Best record: %d attempts.\n", score_get("guess"));
                break;
            }
        }
        printf("\nPlay again? (y/n): ");
        fflush(stdout);
        if (!fgets(buf, sizeof(buf), stdin)) break;
        if (buf[0] != 'y' && buf[0] != 'Y') break;
    }
    return 0;
}
