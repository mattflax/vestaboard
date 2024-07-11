class Graphic:
    def __init__(self, board1, board2, co2_board, multiplier):
        self.board1_content = board1
        self.board2_content = board2
        self.text_lines = co2_board
        self.multiplier = multiplier


swimming_pool = Graphic(
    [
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 69, 69, 69, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 69, 69, 69, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 69, 69, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 69, 69, 70, 70, 70, 69, 69, 69, 69, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 69, 69, 69, 69, 69, 69, 70, 69, 69, 69, 69, 69, 69, 70, 70],
        [67, 67, 67, 67, 67, 69, 69, 69, 69, 69, 69, 69, 69, 67, 67, 69, 69, 69, 69, 67, 67, 67]
    ],
    [
        [67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67],
        [67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67],
        [67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70]
    ],
    [
        "Total CO2 equivalent", "to Olympic swimming", "pools"
    ],
    5.4
)

nessie = Graphic(
    [
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 66, 66, 66, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 66, 66, 66, 66, 66, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 66, 66, 70, 70, 70, 70, 66, 66, 66, 70, 70, 70, 70, 66, 66, 66, 70, 70],
        [70, 70, 70, 70, 66, 66, 70, 70, 70, 66, 66, 70, 66, 66, 70, 70, 66, 66, 70, 66, 66, 70],
        [67, 67, 67, 67, 66, 66, 66, 67, 67, 66, 66, 67, 66, 66, 67, 67, 66, 66, 67, 66, 66, 67]
    ],
    [
        [67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67],
        [67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67],
        [67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70],
        [70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70]
    ],
    [
        "Total CO2 equivalent", "to Loch Ness monster", "Nessie"
    ],
    5.4
)

Images = [swimming_pool, nessie]
