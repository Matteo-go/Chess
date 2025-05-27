from pieces.piece import Piece

class King(Piece):
    def __init__(self, color, col, row):
        super().__init__(color, col, row)
        self.name = "king"

    def get_valid_moves(self, board):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = self.row + dr, self.col + dc
                if self.in_bounds(r, c):
                    target = board[r][c]
                    if target is None or target.color != self.color:
                        moves.append((r, c))
        return moves
