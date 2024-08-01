import random
import itertools
import time
import curses
from utils import load_frames, sleep, TICK_LENGTH
from garbage import create_garbage
from ship import create_ship
from globals import coros, obstacles
from obstacles import show_obstacles
from utils import update_year, draw_text

STAR_PROBABILITY = 0.05
STRING_WINDOW_HEIGHT = 3


def create_stars(canvas, chance=STAR_PROBABILITY):
    stars = []
    maxy, maxx = canvas.getmaxyx()
    star_opts = list("+*.:")
    for y in range(1, maxy - 1):
        for x in range(1, maxx - 1):
            if random.random() > chance:
                continue
            star = random.choice(star_opts)
            stars.append((y, x, star))

    return stars


def update_objects(canvas):
    global coros, obstacles
    canvas.nodelay(True)
    curses.curs_set(False)
    stars = create_stars(canvas)
    for x, y, star in stars:
        coros.append(create_blink(canvas, x, y, star))
    maxy, maxx = canvas.getmaxyx()
    center = maxy // 2, maxx // 2
    ship_frames = load_frames("rocket")
    coros.append(create_ship(canvas, *center, ship_frames))
    coros.append(create_garbage(coros, canvas, 0.5))

    text_canvas = canvas.derwin(
        STRING_WINDOW_HEIGHT, maxx, maxy - STRING_WINDOW_HEIGHT, 0
    )
    coros.append(update_year())
    coros.append(draw_text(text_canvas, maxx))

    while True:
        for coro in coros.copy():
            try:
                coro.send(None)
            except StopIteration:
                coros.remove(coro)

        canvas.border()
        canvas.refresh()
        time.sleep(TICK_LENGTH)


def create_blink(canvas, row, column, symbol="*"):
    frames = [
        ((row, column, symbol, curses.A_DIM), 2),
        ((row, column, symbol), 0.3),
        ((row, column, symbol, curses.A_BOLD), 0.5),
        ((row, column, symbol), 0.3),
    ]

    offset = random.randint(0, len(frames) - 1)

    return blink(canvas, frames, offset)


async def blink(canvas, frames, offset):

    frames = frames[offset:] + frames[:offset]

    for args, t in itertools.cycle(frames):
        canvas.addstr(*args)
        await sleep(t)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(update_objects)
