import asyncio
import curses
import itertools
import random
import time

from curses_tools import read_controls, draw_frame, get_frame_size


class GameSettings:
    def __init__(self):
        self.rocket_speed = 1
        self.rocket_frames = []
        self.stars = '+*.:'
        self.tic_timeout = 0.1
        self.max_stars = 200


async def blink(canvas, row, column, offset_tics=20, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(10 + offset_tics):
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


def draw_stars(canvas, settings, max_y, max_x):
    coroutines = []

    for _ in range(settings.max_stars):
        row = random.randint(1, max_y - 2)
        column = random.randint(1, max_x - 2)
        offset_tics = random.randint(20, 30)
        symbol = random.choice(settings.stars)

        coroutine = blink(canvas, row, column, offset_tics, symbol)
        coroutines.append(coroutine)
    return coroutines


async def manage_rocket(canvas, settings, max_y, max_x):
    frames_rocket = itertools.cycle(settings.rocket_frames)
    rocket_height, rocket_width = get_frame_size(next(frames_rocket))
    rocket_row = max_y // 2 - rocket_height // 2
    rocket_column = max_x // 2 - rocket_width // 2
    while True:
        rows_direction, columns_direction, _ = read_controls(canvas)
        new_rocket_row = rocket_row + rows_direction * settings.rocket_speed
        new_rocket_column = rocket_column + columns_direction * settings.rocket_speed

        rocket_row = max(0, min(max_y - rocket_height, new_rocket_row))
        rocket_column = max(0, min(max_x - rocket_width, new_rocket_column))
        rocket_frame = next(frames_rocket)
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_column, rocket_frame, negative=True)


def draw(canvas):
    settings = GameSettings()

    with open('frames/rocket/frame_1.txt', 'r') as frame_file:
        frame_1 = frame_file.read()
    with open('frames/rocket/frame_2.txt', 'r') as frame_file:
        frame_2 = frame_file.read()
    settings.rocket_frames = [frame_1, frame_1, frame_2, frame_2]

    curses.curs_set(False)
    canvas.nodelay(1)
    curses.use_default_colors()

    max_y, max_x = canvas.getmaxyx()
    coroutines = draw_stars(canvas, settings, max_y, max_x)
    coroutines = [manage_rocket(canvas, settings, max_y, max_x)] + coroutines

    while True:
        for coroutine in coroutines[:]:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(settings.tic_timeout)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
