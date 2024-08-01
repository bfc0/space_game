import asyncio
from math import tan
import os
from curses_tools import draw_frame, get_frame_size
from globals import year
from game_scenario import PHRASES

TICK_LENGTH = 0.1


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def load_frames(name: str) -> list[str]:
    directory = f"animation/{name}"
    return [read_file(os.path.join(directory, f)) for f in os.listdir(directory)]


async def sleep(number):
    for _ in range(int(number * 10)):
        await asyncio.sleep(0)


async def show_game_over(canvas):
    [frame] = load_frames("game_over")
    canvas.refresh()
    max_row, max_column = canvas.getmaxyx()
    rows_frame, columns_frame = get_frame_size(frame)
    row = max_row // 2 - rows_frame // 2
    column = max_column // 2 - columns_frame // 2
    while True:
        draw_frame(canvas, row, column, frame)
        await sleep(TICK_LENGTH)


async def update_year():
    global year

    while True:
        await sleep(TICK_LENGTH * 15)
        year[0] += 1


async def draw_text(canvas, width):
    text = ""

    while True:
        text = f"Year {year[0]}. "
        if phrase := PHRASES.get(year[0]):
            text += phrase

        _, columns_size = get_frame_size(text)
        canvas.addstr(1, width // 2 - columns_size // 2, text)
        draw_frame(canvas, 1, width // 2 - columns_size // 2, text)
        canvas.refresh()
        await sleep(TICK_LENGTH)
        draw_frame(canvas, 1, width // 2 - columns_size // 2, text, True)
