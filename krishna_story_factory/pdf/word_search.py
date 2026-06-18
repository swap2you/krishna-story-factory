from __future__ import annotations

import random
import string
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WordSearchPuzzle:
    grid: list[list[str]]
    placed_words: list[str]
    answer_key: dict[str, str]


def build_word_search(words: list[str], *, size: int = 12, seed: int = 42) -> WordSearchPuzzle:
    rng = random.Random(seed)
    cleaned = [_clean_word(w) for w in words if _clean_word(w)]
    cleaned = cleaned[:10] or ["KRISHNA", "PRAYER", "DEVAKI", "VASUDEVA", "KAMSA"]
    cleaned = sorted(cleaned, key=len, reverse=True)

    grid = [[" " for _ in range(size)] for _ in range(size)]
    answer_key: dict[str, str] = {}

    for word in cleaned:
        placed = _place_word(grid, word, rng)
        if placed:
            answer_key[word] = placed

    for row in range(size):
        for col in range(size):
            if grid[row][col] == " ":
                grid[row][col] = rng.choice(string.ascii_uppercase)

    return WordSearchPuzzle(grid=grid, placed_words=list(answer_key.keys()), answer_key=answer_key)


def _clean_word(word: str) -> str:
    return "".join(ch for ch in word.upper() if ch.isalpha())


def _place_word(grid: list[list[str]], word: str, rng: random.Random) -> str | None:
    size = len(grid)
    directions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1), (-1, 1)]
    attempts = 0
    while attempts < 200:
        attempts += 1
        dr, dc = rng.choice(directions)
        row = rng.randrange(size)
        col = rng.randrange(size)
        end_row = row + dr * (len(word) - 1)
        end_col = col + dc * (len(word) - 1)
        if not (0 <= end_row < size and 0 <= end_col < size):
            continue
        coords: list[tuple[int, int]] = []
        ok = True
        for i, letter in enumerate(word):
            r = row + dr * i
            c = col + dc * i
            existing = grid[r][c]
            if existing not in {" ", letter}:
                ok = False
                break
            coords.append((r, c))
        if not ok:
            continue
        for (r, c), letter in zip(coords, word):
            grid[r][c] = letter
        direction_name = _direction_name(dr, dc)
        return f"row {row + 1}, col {col + 1}, {direction_name}"
    return None


def _direction_name(dr: int, dc: int) -> str:
    if dr == 0 and dc == 1:
        return "across"
    if dr == 1 and dc == 0:
        return "down"
    if dr == 1 and dc == 1:
        return "diagonal down-right"
    if dr == 0 and dc == -1:
        return "across (reverse)"
    if dr == -1 and dc == 0:
        return "up"
    if dr == -1 and dc == -1:
        return "diagonal up-left"
    if dr == 1 and dc == -1:
        return "diagonal down-left"
    return "diagonal up-right"
