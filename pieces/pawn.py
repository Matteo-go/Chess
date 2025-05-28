from pieces.piece import Piece

class Pawn(Piece):
    def __init__(self, color, col, row):
        super().__init__(color, col, row)
        self.name = "pawn"

    def get_valid_moves(self, board, last_move=None):
        direction = -1 if self.color == "white" else 1
        moves = []

        # Avancer
        if self.in_bounds(self.row + direction, self.col) and board[self.row + direction][self.col] is None:
            moves.append((self.row + direction, self.col))

            # Double avance si au départ
            if (self.color == "white" and self.row == 6) or (self.color == "black" and self.row == 1):
                if board[self.row + 2 * direction][self.col] is None:
                    moves.append((self.row + 2 * direction, self.col))

        # Prise diagonale
        for dc in [-1, 1]:
            r, c = self.row + direction, self.col + dc
            if self.in_bounds(r, c):
                target = board[r][c]
                if target and target.color != self.color:
                    moves.append((r, c))

        if last_move:
            enemy_piece, from_r, from_c, to_r, to_c = last_move
            if isinstance(enemy_piece, Pawn) and enemy_piece.color != self.color:
                if abs(to_r - from_r) == 2 and to_r == self.row:
                    if abs(to_c - self.col) == 1:
                        moves.append((self.row + direction, to_c))

        return moves
