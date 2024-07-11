#!/home/matt/work/wmsh/vestaboard/venv/bin/python

import csv
import sys
import time
from graphics import Graphic, Images
from vestaboard import Board, Installable
from vestaboard.formatter import Formatter

MAX_WIDTH = 22
MAX_LINES = 6
BOARD_NAMES = ['train_board1', 'train_board2', 'co2_board']
KEY_FILE = 'keys.csv'
SLEEP_SECS = 15
GRAPHIC_DISPLAY_SECS = 30
MIN_GRAPHIC_INTERVAL_MINS = 5


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
    def __init__(self, csv_file):
        self.csv_file = csv_file
        boards = init_boards(KEY_FILE)
        self.train_board1 = boards[BOARD_NAMES[0]]
        self.train_board2 = boards[BOARD_NAMES[1]]
        self.co2_board = boards[BOARD_NAMES[2]]
        self.all_trains = read_input_file(csv_file)
        self.num_displayed = 0
        self.co2_total = 0
        self.disabled = False
        self.graphic_idx = 0
        self.last_graphic_display_time = int(time.strftime('%H%M'))

    def disable(self):
        self.disabled = True
        for board in [self.train_board1, self.train_board2, self.co2_board]:
            reset_board(board)

    def reset_trains(self):
        # Re-read trains file
        self.all_trains = read_input_file(self.csv_file)

    def run(self):
        while True:
            if self.should_display_graphic():
                self.show_current_graphic()
                time.sleep(GRAPHIC_DISPLAY_SECS)
            else:
                past_trains = self.get_display_trains()
                if len(past_trains) > 0 and len(past_trains) > self.num_displayed:
                    self.num_displayed = len(past_trains)
                    self.update_train_boards(past_trains)
                    self.update_co2(past_trains)
                time.sleep(SLEEP_SECS)
                print('...tick...')

    def should_display_graphic(self):
        time_now = int(time.strftime('%H%M'))
        if (time_now - self.last_graphic_display_time > MIN_GRAPHIC_INTERVAL_MINS) and (time_now % 5 == 0):
            self.last_graphic_display_time = time_now
            return True
        return False

    def show_current_graphic(self):
        display_graphic(Images[self.graphic_idx], self.train_board1, self.train_board2, self.co2_board, self.co2_total)
        self.graphic_idx += 1
        if self.graphic_idx > len(Images):
            self.graphic_idx = 0

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
            total_co2 = co2
            update_co2_board(self.co2_board, total_co2)


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
    line2 = Formatter().convertLine(f'CO2 saved-{co2kg}', justify='right')
    return [line1, line2]


def reset_board(board: Board):
    board.post('')


def update_train_board(board: Board, trains):
    content = []
    for train in trains:
        content += format_train(train.displayTime, train.place, train.co2)
    # Update board content
    board.raw(content, pad='bottom')


def update_co2_board(board: Board, co2_count):
    # text = f'Since the start of the day, travelling by train has saved {co2_count}kg of CO2 emissions'
    # print(f'CO2 Board: {text}')
    line1 = Formatter().convertLine('Total CO2 saved in')
    line2 = Formatter().convertLine('comparison to')
    line3 = Formatter().convertLine('car & plane')
    line4 = Formatter().convertLine(f'{co2_count}')
    content = [line1, line2, line3, line4]
    # Update board content
    board.raw(content, pad='center')


def display_graphic(graphic: Graphic, board1: Board, board2: Board, co2_board: Board, co2kg):
    board1.raw(graphic.board1_content)
    board2.raw(graphic.board2_content)
    co2_board.raw(format_graphic_text(graphic.text_lines, co2kg), pad='center')


def format_graphic_text(lines, co2kg):
    co2_content = []
    for line in lines:
        co2_content.append(Formatter().convertLine(line))
    co2_content.append(Formatter().convertLine(f'{co2kg}'))
    return co2_content


def main(args):
    if len(args) < 1:
        usage()
        sys.exit(1)

    board_runner = BoardRunner(args[0])
    board_runner.run()


def usage():
    print('Usage:')
    print('  python train_display.py {input.csv}')


if __name__ == '__main__':
    main(sys.argv[1:])
