import asyncio
import curses
import itertools
import random
import time

from curses_tools import read_controls, draw_frame, get_frame_size

SYMBOLS = '+*.:'
TIC_TIMEOUT = 0.1

with open('frames/rocket/frame_1.txt', 'r') as frame_file:
    frame_1 = frame_file.read()
with open('frames/rocket/frame_2.txt', 'r') as frame_file:
    frame_2 = frame_file.read()
frames = [frame_1, frame_2]
frames_rocket = itertools.cycle(frames)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(random.randint(10, 30)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for _ in range(3):
            await asyncio.sleep(0)


def draw_stars(canvas, max_y, max_x):
    coroutines = []

    for _ in range(200):
        row = random.randint(1, max_y - 2)
        column = random.randint(1, max_x - 2)
        symbol = random.choice(SYMBOLS)

        coroutine = blink(canvas, row, column, symbol)
        coroutines.append(coroutine)
    return coroutines


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(1)
    curses.use_default_colors()

    max_y, max_x = canvas.getmaxyx()
    rocket_height, rocket_width = get_frame_size(frame_1)
    rocket_row = max_y // 2 - rocket_height // 2
    rocket_column = max_x // 2 - rocket_width // 2

    coroutines = draw_stars(canvas, max_y, max_x)

    while True:
        rows_direction, columns_direction, _ = read_controls(canvas)

        new_rocket_row = rocket_row + rows_direction
        new_rocket_column = rocket_column + columns_direction

        if (0 <= new_rocket_row <= max_y - rocket_height) and (0 <= new_rocket_column <= max_x - rocket_width):
            rocket_row = new_rocket_row
            rocket_column = new_rocket_column

        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)

        rocket_frame = next(frames_rocket)
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame, negative=True)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
