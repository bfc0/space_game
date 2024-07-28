import random
import itertools
import time
import curses
from utils import load_frames, sleep
from curses_tools import draw_frame, get_frame_size, read_controls
from fire import fire

STAR_PROBABILITY = 0.05
TICK_LENGTH = 0.1
SHIP_ANIM_DELAY = 3
MAX_SHIP_SPEED = 5


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
    canvas.nodelay(True)
    stars = create_stars(canvas)
    coros = [blink(canvas, x, y, star) for x, y, star in stars]
    maxy, maxx = canvas.getmaxyx()
    center = maxy // 2, maxx // 2
    coros.append(fire(canvas, *center))
    curses.curs_set(False)
    ship_frames = load_frames("rocket")
    run_ship = create_ship(canvas, *center, ship_frames)

    while True:
        for coro in coros:
            try:
                coro.send(None)
            except StopIteration:
                coros.remove(coro)

        run_ship.send(None)

        canvas.border()
        canvas.refresh()
        time.sleep(TICK_LENGTH)


def create_ship(canvas, row, column, frames):
    frames = frames.copy()
    speed = [0, 0]

    async def animate_spaceship():
        nonlocal frames, row, column, speed
        frames = [f for f in frames for _ in range(SHIP_ANIM_DELAY)]

        for frame in itertools.cycle(frames):

            speed = update_speed(speed)
            row, column, speed = update_position(
                row, column, speed, canvas, frame)
            draw_frame(canvas, row, column, frame)
            await sleep(TICK_LENGTH)
            draw_frame(canvas, row, column, frame, negative=True)

    def update_speed(speed):
        r, c, _ = read_controls(canvas)
        speed[0] = max(-MAX_SHIP_SPEED, min(MAX_SHIP_SPEED, speed[0] + r))
        speed[1] = max(-MAX_SHIP_SPEED, min(MAX_SHIP_SPEED, speed[1] + c))

        return speed

    def update_position(row, column, speed, canvas, frame):
        max_row, max_column = canvas.getmaxyx()
        new_row = row + speed[0]
        new_column = column + speed[1]
        height, width = get_frame_size(frame)

        if new_row < 1:
            new_row, speed[0] = 1, 0
        elif new_row > (limit := max_row - height - 1):
            new_row, speed[0] = limit, 0

        if new_column < 1:
            new_column, speed[1] = 1, 0
        elif new_column > (limit := max_column - width - 1):
            new_column, speed[1] = limit, 0

        return new_row, new_column, speed

    return animate_spaceship()


async def blink(canvas, row, column, symbol="*"):
    frames = [
        ((row, column, symbol, curses.A_DIM), 2),
        ((row, column, symbol), 0.3),
        ((row, column, symbol, curses.A_BOLD), 0.5),
        ((row, column, symbol), 0.3),
    ]

    # rotate animation by a random amount
    steps = random.randint(0, len(frames) - 1)
    frames = frames[steps:] + frames[:steps]

    for args, t in itertools.cycle(frames):
        canvas.addstr(*args)
        await sleep(t)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(update_objects)
