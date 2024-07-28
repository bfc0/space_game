import asyncio
import os


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def load_frames(name: str) -> list[str]:
    directory = f"animation/{name}"
    return [read_file(os.path.join(directory, f)) for f in os.listdir(directory)]


async def sleep(number):
    for _ in range(int(number * 10)):
        await asyncio.sleep(0)
