import asyncio
import random
from curses_tools import draw_frame, get_frame_size
from utils import load_frames, sleep, TICK_LENGTH
from obstacles import Obstacle
from explosion import explode
from game_scenario import get_garbage_delay_tics
from globals import obstacles, obstacles_in_last_collisions, year


async def create_garbage(coros, canvas, speed: float, randomize=True):
    garbage_types = load_frames("garbage")
    _, maxx = canvas.getmaxyx()

    while True:
        ticks = get_garbage_delay_tics(year[0])

        if not ticks:
            await sleep(TICK_LENGTH)
            continue

        if randomize:
            col = random.randint(0, maxx - 1)
            garbage_type = random.choice(garbage_types)
        else:
            col = 1
            garbage_type = garbage_types[0]

        fly_coro = fly_garbage(canvas, col, garbage_type, speed)
        coros.append(fly_coro)

        await sleep(TICK_LENGTH * ticks)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0
    h, w = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, h, w)
    obstacles.append(obstacle)

    while row < rows_number:
        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            mid = obstacle.get_center()
            await explode(canvas, *mid)
            break

        draw_frame(canvas, row, column, garbage_frame)
        obstacle.row = int(row)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

    obstacles.remove(obstacle)
