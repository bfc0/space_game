import itertools
from curses_tools import draw_frame, read_controls, get_frame_size
from utils import TICK_LENGTH, sleep
from fire import fire
from globals import coros, obstacles, year
from utils import show_game_over

SHIP_ANIM_DELAY = 3
MAX_SHIP_SPEED = 2


def create_ship(canvas, row, column, frames):
    frames = frames.copy()
    speed = [0, 0]

    async def animate_spaceship():
        nonlocal frames, row, column, speed
        frames = [f for f in frames for _ in range(SHIP_ANIM_DELAY)]

        for frame in itertools.cycle(frames):

            speed = update_ship_state(speed, frame)
            row, column, speed = update_position(row, column, speed, canvas, frame)
            draw_frame(canvas, row, column, frame)

            for obstacle in obstacles:
                if obstacle.has_collision(row, column):
                    coros.append(show_game_over(canvas))
                    draw_frame(canvas, row, column, frame, negative=True)
                    return

            await sleep(TICK_LENGTH)
            draw_frame(canvas, row, column, frame, negative=True)

    def update_ship_state(speed, ship_frame):
        global coros
        r, c, shots_fired = read_controls(canvas)

        if shots_fired and year[0] > 2020:
            _, width = get_frame_size(ship_frame)
            gun_location = row, column + width // 2
            coros.append(fire(canvas, *gun_location))

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
