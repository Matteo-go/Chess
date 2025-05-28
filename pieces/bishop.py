from pieces.piece import Piece

class Bishop(Piece):
    def __init__(self, color, col, row):
        super().__init__(color, col, row)
        self.name = "bishop"

    def get_valid_moves(self, board, last_move):
        return self.slide_moves(board, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

    def slide_moves(self, board, directions):
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            while self.in_bounds(r, c):
                target = board[r][c]
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc
        return moves
