import random
import sys
import time

GRID = [
    "S....#....",
    ".##..#.##.",
    ".#C.....#.",
    ".#####..#.",
    "........#G",
]
ROWS, COLS = len(GRID), len(GRID[0])
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
RESPAWN = 4
MAX_STEPS = 60
SLOPPY_GOAL = 5.0
BUG_TILE = None


def set_grid(rows):
    global GRID, ROWS, COLS, START, GOAL, COIN, BUG_TILE
    GRID = rows
    ROWS, COLS = len(GRID), len(GRID[0])
    START, GOAL, COIN, BUG_TILE = find("S"), find("G"), find("C"), find("X")


def find(ch):
    for r, row in enumerate(GRID):
        for c, x in enumerate(row):
            if x == ch:
                return (r, c)


START, GOAL, COIN = find("S"), find("G"), find("C")
BUG_TILE = find("X")


def reward_fn(mode, event):
    if mode == "sloppy":
        return {"coin": 1.0, "goal": SLOPPY_GOAL, "step": 0.0}[event]
    return {"coin": 0.0, "goal": 10.0, "step": -0.1}[event]


def step(pos, timer, action, mode):
    dr, dc = MOVES[action]
    r, c = pos[0] + dr, pos[1] + dc
    if not (0 <= r < ROWS and 0 <= c < COLS) or GRID[r][c] == "#":
        r, c = pos
    pos = (r, c)
    timer = max(0, timer - 1)
    if pos == GOAL:
        return pos, timer, reward_fn(mode, "goal"), True, "goal"
    if BUG_TILE and pos == BUG_TILE:
        return pos, timer, reward_fn(mode, "goal"), True, "bug"
    if pos == COIN and timer == 0:
        return pos, RESPAWN, reward_fn(mode, "coin") + reward_fn(mode, "step"), False, "coin"
    return pos, timer, reward_fn(mode, "step"), False, None


def train(mode, episodes=6000, alpha=0.2, gamma=0.97, init=0.0):
    q = {}
    for ep in range(episodes):
        eps = max(0.05, 1 - ep / (episodes * 0.7))
        pos, timer = START, 0
        for _ in range(MAX_STEPS):
            s = (pos, timer)
            qs = q.setdefault(s, [init] * 4)
            a = random.randrange(4) if random.random() < eps else qs.index(max(qs))
            pos, timer, rew, done, _ = step(pos, timer, a, mode)
            nq = q.setdefault((pos, timer), [init] * 4)
            target = rew + (0 if done else gamma * max(nq))
            qs[a] += alpha * (target - qs[a])
            if done:
                break
    return q


def run(q, mode, show=False):
    pos, timer = START, 0
    coins, total, path = 0, 0.0, [pos]
    for t in range(MAX_STEPS):
        qs = q.get((pos, timer), [0.0] * 4)
        a = qs.index(max(qs))
        pos, timer, rew, done, ev = step(pos, timer, a, mode)
        total += rew
        coins += ev == "coin"
        path.append(pos)
        if show:
            draw(pos, timer, t + 1, coins, total)
        if done:
            return True, coins, total, path
    return False, coins, total, path


def draw(pos, timer, t, coins, total):
    out = ["\033[H\033[J"]
    for r in range(ROWS):
        line = ""
        for c in range(COLS):
            if (r, c) == pos:
                line += "A "
            elif (r, c) == COIN:
                line += ("C " if timer == 0 else "c ")
            else:
                line += GRID[r][c].replace("S", ".") + " "
        out.append(line)
    out.append(f"\nstep {t:>2}   coins {coins:>2}   score {total:.1f}")
    print("\n".join(out))
    time.sleep(0.08)


def report(mode):
    random.seed(0)
    q = train(mode)
    reached, coins, total, path = run(q, mode)
    print(f"[{mode}] reached goal: {reached} | coins farmed: {coins} | score: {total:.1f} | steps: {len(path) - 1}")
    return q


if __name__ == "__main__":
    modes = sys.argv[1:] or ["sloppy", "fixed"]
    animate = "--watch" in modes
    modes = [m for m in modes if m != "--watch"] or ["sloppy", "fixed"]
    for m in modes:
        q = report(m)
        if animate:
            input(f"enter to watch the {m} agent...")
            run(q, m, show=True)
            input("enter to continue...")
