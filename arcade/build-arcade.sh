#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/build/arcade-bin"
mkdir -p "${OUT_DIR}"

CFLAGS="-std=c11 -Os -Wall -Wextra -I${ROOT_DIR}/arcade -fno-stack-protector"
LDFLAGS="-static -s"

echo "[arcade] Compiling Micro Arcade launcher and 8 terminal games..."

gcc ${CFLAGS} "${ROOT_DIR}/arcade/arcade.c"         -o "${OUT_DIR}/arcade"        ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/snake.c"           -o "${OUT_DIR}/snake"         ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/tetris.c"          -o "${OUT_DIR}/tetris"        ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/pong.c"            -o "${OUT_DIR}/pong"          ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/mines.c"           -o "${OUT_DIR}/mines"         ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/game2048.c"        -o "${OUT_DIR}/2048"          ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/guess.c"           -o "${OUT_DIR}/guess"         ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/tictactoe.c"       -o "${OUT_DIR}/tictactoe"     ${LDFLAGS}
gcc ${CFLAGS} "${ROOT_DIR}/games/spaceinvaders.c"   -o "${OUT_DIR}/spaceinvaders" ${LDFLAGS}

chmod 0755 "${OUT_DIR}"/*
echo "[arcade] Compiled binaries:"
ls -lh "${OUT_DIR}"
TOTAL_BYTES="$(du -sb "${OUT_DIR}" | awk '{print $1}')"
echo "[arcade] Total uncompressed arcade size: ${TOTAL_BYTES} bytes ($((TOTAL_BYTES / 1024)) KB)"
