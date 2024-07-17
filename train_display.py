#!/home/vestaboard/vestaboard/.venv/bin/python

import csv
import sys
import time
from threading import Thread

from flask import Flask, render_template, redirect
from vestaboard import Board
from vestaboard.formatter import Formatter
from requests.exceptions import RequestException

from graphics import Graphic, Images

MAX_WIDTH = 22
MAX_LINES = 6
BOARD_NAMES = ['train_board1', 'train_board2', 'co2_board']
KEY_FILE = '/home/vestaboard/.config/vestaboard/keys.csv'
SLEEP_SECS = 15
GRAPHIC_DISPLAY_SECS = 30
MIN_GRAPHIC_INTERVAL_MINS = 2

app = Flask(__name__)


class Train:
    def __init__(self, input_time, place, co2, arr_or_dep: str):
        self.intTime = input_time
        self.actualTime = time.strptime(f'{input_time}', '%H%M')
        self.displayTime = f'{self.actualTime[3]:02}:{self.actualTime[4]:02}'
        self.place = place
        self.co2 = co2
        self.arrival = arr_or_dep.lower().startswith('a')

    def __str__(self):
        return f'{self.displayTime},{self.place},{self.co2}'

    def __repr__(self):
        return f'{self.displayTime},{self.place},{self.co2}'


class BoardRunner:
    csv_file = None
    all_trains = []
    num_displayed = 0
    co2_total = 0
    disabled = False
    graphic_idx = 0
    last_graphic_display_time = int(time.strftime('%H%M'))
    showing_graphic = False
    running = True

    def __init__(self):
        boards = init_boards(KEY_FILE)
        self.train_board1 = boards[BOARD_NAMES[0]]
        self.train_board2 = boards[BOARD_NAMES[1]]
        self.co2_board = boards[BOARD_NAMES[2]]

    def initialise_trains(self, csv_file):
        self.csv_file = csv_file
        self.all_trains = read_input_file(self.csv_file)

    def disable(self):
        self.disabled = True
        for board in [self.train_board1, self.train_board2, self.co2_board]:
            reset_board(board)

    def enable(self):
        self.disabled = False
        self.display_trains(force=True)

    def reset_trains(self):
        # Re-read trains file
        self.all_trains = read_input_file(self.csv_file)
        self.display_trains(force=True)

    def run(self):
        while self.running:
            if self.disabled:
                time.sleep(SLEEP_SECS)
            else:
                if self.should_display_graphic() and not self.showing_graphic:
                    self.show_current_graphic()
                    time.sleep(GRAPHIC_DISPLAY_SECS)
                else:
                    self.display_trains()
                    time.sleep(SLEEP_SECS)
                    print('...tick...')

    def should_display_graphic(self):
        time_now = int(time.strftime('%H%M'))
        if (time_now - self.last_graphic_display_time > MIN_GRAPHIC_INTERVAL_MINS) and (
                time_now % MIN_GRAPHIC_INTERVAL_MINS == 0):
            self.last_graphic_display_time = time_now
            return True
        return False

    def show_current_graphic(self):
        print(f'Showing graphic {self.graphic_idx}')
        display_graphic(Images[self.graphic_idx], self.train_board1, self.train_board2, self.co2_board, self.co2_total)
        self.showing_graphic = True
        self.graphic_idx += 1
        if self.graphic_idx >= len(Images):
            self.graphic_idx = 0

    def display_trains(self, force=False):
        past_trains = self.get_display_trains()
        if force or self.showing_graphic or (len(past_trains) > 0 and len(past_trains) > self.num_displayed):
            self.num_displayed = len(past_trains)
            self.update_train_boards(past_trains)
            self.update_co2(past_trains)
            self.showing_graphic = False

    def get_display_trains(self):
        time_now = int(time.strftime('%H%M'))
        rows = []
        # Get all trains up to "now"
        for train in self.all_trains:
            if train.intTime <= time_now:
                rows.append(train)
            else:
                break
        return rows

    def update_train_boards(self, trains):
        self.num_displayed = len(trains)
        # Reverse the order - most recent train first
        trains.reverse()
        # Most recent three go to top board
        update_train_board(self.train_board1, trains[0:3])
        # Next most recent go to middle, if they exist
        if len(trains) > 3:
            update_train_board(self.train_board2, trains[3:6])
        else:
            reset_board(self.train_board2)

    def update_co2(self, trains):
        co2 = 0
        for trains in trains:
            co2 += trains.co2
        if co2 != self.co2_total:
            self.co2_total = co2
        update_co2_board(self.co2_board, self.co2_total)


def init_boards(key_file):
    boards = {}
    with open(key_file) as keys:
        csv_reader = csv.reader(keys)
        for i, row in enumerate(csv_reader):
            boards[BOARD_NAMES[i]] = Board(localApi={'ip': row[3], 'key': row[4], 'saveToken': False})
            # installable = Installable(apiKey=row[1], apiSecret=row[2], saveCredentials=False)
            # boards[BOARD_NAMES[i]] = Board(installable)
    return boards


def read_input_file(file):
    rows = []
    with open(file) as csv_file:
        input_reader = csv.reader(csv_file)
        for row in input_reader:
            if len(row) >= 3:
                try:
                    arr_time = int(row[0])
                    co2 = int(row[2])
                    rows.append(Train(arr_time, row[1], co2, row[3]))
                except ValueError:
                    continue
    return sorted(rows, key=lambda a: a.intTime)


def format_train(display_time, place, co2kg):
    line1 = Formatter().convertLine(f'{display_time}-{place}', justify='left')
    line2 = Formatter().convertLine(f'CO2 saved-{co2kg}kg', justify='right')
    return [line1, line2]


def reset_board(board: Board):
    try:
        board.post('')
    except RequestException as e:
        print(f'Caught RequestException resetting content - {e.strerror}')


def update_train_board(board: Board, trains):
    content = []
    for train in trains:
        content += format_train(train.displayTime, train.place, train.co2)
    while len(content) < MAX_LINES:
        content.append(Formatter().convertLine(''))
    # Update board content
    board_raw(board, content, pad='bottom')


def update_co2_board(board: Board, co2_count):
    # text = f'Since the start of the day, travelling by train has saved {co2_count}kg of CO2 emissions'
    # print(f'CO2 Board: {text}')
    line1 = Formatter().convertLine('Total CO2 saved in')
    line2 = Formatter().convertLine('comparison to')
    line3 = Formatter().convertLine('car & plane')
    line4 = Formatter().convertLine(f'{co2_count:,}kg')
    content = [line1, line2, line3, line4]
    # Update board content
    board_raw(board, content, pad='center')


def display_graphic(graphic: Graphic, board1: Board, board2: Board, co2_board: Board, co2kg):
    board_raw(board1, graphic.board1_content)
    board_raw(board2, graphic.board2_content)
    board_raw(co2_board, format_graphic_text(graphic.text_lines, co2kg * graphic.multiplier), pad='center')


def board_raw(board: Board, content, pad=None):
    try:
        board.raw(content, pad=pad)
    except RequestException as e:
        print(f'Caught RequestException posting raw - {e.strerror}')


def format_graphic_text(lines, metric):
    co2_content = []
    for line in lines:
        co2_content.append(Formatter().convertLine(line))
    co2_content.append(Formatter().convertLine(f'{metric:,.1f}'))
    return co2_content


@app.route("/start")
def start():
    board_runner.enable()
    return redirect('/')


@app.route("/stop")
def stop():
    board_runner.disable()
    return redirect('/')


@app.route("/reload")
def reload():
    board_runner.reset_trains()
    return redirect('/')


@app.route("/")
def index():
    return render_template('index.html', active=(not board_runner.disabled))


board_runner = BoardRunner()


def main(args):
    if len(args) < 1:
        usage()
        sys.exit(1)

    # Start the board running
    board_runner.initialise_trains(args[0])
    board_thread = Thread(target=board_runner.run)
    print('Starting board thread')
    board_thread.start()
    print('Board thread running')
    # And start the web app
    app.run(host='192.168.0.10', port=5000)


def usage():
    print('Usage:')
    print('  python train_display.py {input.csv}')


if __name__ == '__main__':
    main(sys.argv[1:])
