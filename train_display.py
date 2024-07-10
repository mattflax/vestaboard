#!/home/matt/work/wmsh/vestaboard/venv/bin/python

import csv
import sys
import time
import vestaboard
from vestaboard.formatter import Formatter

MAX_WIDTH = 22
MAX_LINES = 6
BOARD_NAMES = ['train_board1', 'train_board2', 'co2_board']
KEY_FILE = 'keys.csv'
SLEEP_SECS = 15


class Train:
    def __init__(self, input_time, place, co2, arr_or_dep: str):
        self.displayTime = input_time
        self.actualTime = time.strptime(f'{input_time}', '%H%M')
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
        self.trains = read_input_file(csv_file)
        self.num_displayed = 0
        self.co2_total = 0

    def reset_trains(self):
        # Re-read trains file
        self.trains = read_input_file(self.csv_file)

    def run(self):
        while True:
            rows = self.get_display_trains()
            if len(rows) > 0 and len(rows) > self.num_displayed:
                self.num_displayed = len(rows)
                self.update_train_boards(rows)
                self.update_co2(rows)
            time.sleep(SLEEP_SECS)
            print('...tick...')

    def get_display_trains(self):
        time_now = int(time.strftime('%H%M'))
        rows = []
        # Get all trains up to "now"
        for train in self.trains:
            if train.displayTime <= time_now:
                rows.append(train)
            else:
                break
        return rows

    def update_train_boards(self, rows):
        self.num_displayed = len(rows)
        # Reverse the order
        rows.reverse()
        # Most recent two go to top board
        update_train_board(self.train_board1, rows[0:2])
        # Next most recent go to middle, if they exist
        if len(rows) > 2:
            update_train_board(self.train_board2, rows[2:4])
        else:
            reset_board(self.train_board2)

    def update_co2(self, rows):
        co2 = 0
        for row in rows:
            co2 += row.co2
        if co2 != self.co2_total:
            total_co2 = co2
            update_co2_board(self.co2_board, total_co2)


def init_boards(key_file):
    boards = {}
    with open(key_file) as keys:
        csv_reader = csv.reader(keys)
        for i, row in enumerate(csv_reader):
            installable = vestaboard.Installable(apiKey=row[1], apiSecret=row[2], saveCredentials=False)
            boards[BOARD_NAMES[i]] = vestaboard.Board(installable)
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
    return sorted(rows, key=lambda a: a.displayTime)


def format_arrival(time, place, co2kg):
    text = f'{{66}} The {time:04} from {place} saved {co2kg}kg CO2 pp'
    print(f'Arrival: {text}')
    return Formatter().convertPlainText(text=text, justify='left', align='top', size=[3, 22])


def format_departure(time, place, co2kg):
    text = f'{{66}} The {time:04} to {place} will save {co2kg}kg CO2 pp'
    print(f'Departure: {text}')
    return Formatter().convertPlainText(text=text, justify='left', align='top', size=[3, 22])


def reset_board(board: vestaboard.Board):
    board.post('')


def update_train_board(board: vestaboard.Board, trains):
    content = []
    for train in trains:
        if train.arrival:
            content += format_arrival(train.displayTime, train.place, train.co2)
        else:
            content += format_departure(train.displayTime, train.place, train.co2)
    # Update board content
    board.raw(content, pad='center')


def update_co2_board(board: vestaboard.Board, co2_count):
    text = f'Since the start of the day, travelling by train has saved {co2_count}kg of CO2 emissions'
    print(f'CO2 Board: {text}')
    content = Formatter().convertPlainText(text=text)
    # Update board content
    board.raw(content)


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
