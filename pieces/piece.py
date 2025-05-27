class Piece:
    def __init__(self, color, col, row):
        self.color = color
        self.col = col
        self.row = row
        self.name = "piece"

    def position(self):
        return self.row, self.col

    def in_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8
