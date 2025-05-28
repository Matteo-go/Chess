from pieces.piece import Piece

class Knight(Piece):
    def __init__(self, color, col, row):
        super().__init__(color, col, row)
        self.name = "knight"

    def get_valid_moves(self, board, last_move):
        moves = []
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (-1, 2), (1, -2), (-1, -2)]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if self.in_bounds(r, c):
                target = board[r][c]
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves
